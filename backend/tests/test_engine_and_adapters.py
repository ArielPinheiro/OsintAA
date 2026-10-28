import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.engine.orchestrator import query_engine
from backend.app.engine.models import QueryRequest, ResultStatus, ConfidenceLevel
from backend.app.adapters.cnpj.brasilapi_cnpj import BrasilApiCnpjAdapter
from backend.app.adapters.documents.document_analyzer import DocumentAnalyzerAdapter

@pytest.mark.anyio
async def test_cnpj_adapter_mock():
    adapter = BrasilApiCnpjAdapter()
    
    # Mock de resposta da BrasilAPI
    fake_json = {
        "cnpj": "33000167000101",
        "razao_social": "PETROLEO BRASILEIRO S A PETROBRAS",
        "nome_fantasia": "PETROBRAS",
        "descricao_situacao_cadastral": "ATIVA",
        "cnae_fiscal": "0600001",
        "cnae_fiscal_descricao": "Extração de petróleo e gás natural",
        "cnaes_secundarios": [],
        "qsa": [
            {"nome_socio": "MARIA DA SILVA", "qualificacao_socio": "Diretor", "faixa_etaria": "51 a 60 anos"}
        ]
    }
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_json
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await adapter.execute("33000167000101")
        assert res.status == ResultStatus.CONFIRMED
        assert res.data["razao_social"] == "PETROLEO BRASILEIRO S A PETROBRAS"
        assert res.data["qsa_total"] == 1
        assert res.confidence == ConfidenceLevel.HIGH

@pytest.mark.anyio
async def test_document_analyzer_hash_calculation():
    adapter = DocumentAnalyzerAdapter()
    sample_bytes = b"OSINT BRAZUCA ULTIMATE - TEST CONTENT 2026"
    
    res = await adapter.execute("teste.txt", context={"file_bytes": sample_bytes, "filename": "teste.txt"})
    assert res.status == ResultStatus.CONFIRMED
    assert "sha256" in res.data["hashes"]
    assert "md5" in res.data["hashes"]
    assert res.data["tamanho_bytes"] == len(sample_bytes)
    assert res.confidence == ConfidenceLevel.HIGH

@pytest.mark.anyio
async def test_engine_error_isolation():
    """Verifica que o erro em um adaptador não derruba os demais adaptadores na mesma consulta."""
    req = QueryRequest(category="cnpj", target="33000167000101")
    
    # Fazemos um adapter falhar propositalmente com exceção e outro ter sucesso
    async def failing_run(*args, **kwargs):
        raise TimeoutError("Simulated timeout in primary adapter")

    async def successful_run(*args, **kwargs):
        from backend.app.engine.models import SourceExecutionResult
        return SourceExecutionResult(
            source_id="mock_success",
            source_name="Mock Sucesso",
            category="cnpj",
            status=ResultStatus.CONFIRMED,
            timestamp="",
            execution_time_ms=5.0,
            data={"teste": "ok"}
        )

    # Executar consulta com o motor central
    with patch.object(BrasilApiCnpjAdapter, "run", side_effect=failing_run):
        with patch.object(query_engine._adapters["receitaws_cnpj"], "run", side_effect=successful_run):
            resp = await query_engine.execute_query(req)
            
            # Uma fonte falhou, mas a outra concluiu com sucesso
            assert resp.summary.total_sources >= 2
            assert any(r.status == ResultStatus.ERROR for r in resp.results)
            assert any(r.status == ResultStatus.CONFIRMED for r in resp.results)

