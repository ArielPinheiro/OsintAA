import json
import pytest
from backend.app.engine.models import (
    QueryResponse,
    QuerySummary,
    ResultStatus,
    ConfidenceLevel,
    SourceExecutionResult,
)
from backend.app.reports.exporter import export_to_json, export_to_csv, export_to_html

@pytest.fixture
def sample_response():
    return QueryResponse(
        query_id="test-query-uuid-1234",
        category="cpf",
        target_raw="52998224725",
        target_masked="***.982.247-**",
        started_at="2026-10-28T12:00:00Z",
        finished_at="2026-10-28T12:00:02Z",
        duration_seconds=2.0,
        summary=QuerySummary(total_sources=1, completed=1, manual_steps=1),
        results=[
            SourceExecutionResult(
                source_id="cpf_official",
                source_name="Receita Federal - CPF",
                category="cpf",
                status=ResultStatus.CONFIRMED,
                timestamp="2026-10-28T12:00:01Z",
                execution_time_ms=120.5,
                verification_url="https://servicos.receita.fazenda.gov.br",
                confidence=ConfidenceLevel.HIGH,
                data={"regiao": "SP", "valido": True},
                limitations=["Exige CAPTCHA manual no portal oficial"],
                requires_manual_action=True,
            )
        ]
    )

def test_export_json_preserves_privacy(sample_response):
    json_out = export_to_json(sample_response)
    data = json.loads(json_out)
    assert data["target_masked"] == "***.982.247-**"
    assert "target_raw" not in data  # NUNCA expor target_raw no dump do relatório
    assert data["query_id"] == "test-query-uuid-1234"

def test_export_csv(sample_response):
    csv_out = export_to_csv(sample_response)
    lines = csv_out.strip().split("\r\n") if "\r\n" in csv_out else csv_out.strip().split("\n")
    assert len(lines) == 2  # Cabeçalho + 1 linha de resultado
    assert "***.982.247-**" in lines[1]
    assert "cpf_official" in lines[1]
    assert "confirmado" in lines[1]

def test_export_html(sample_response):
    html_out = export_to_html(sample_response)
    assert "<!DOCTYPE html>" in html_out
    assert "OSINT Brazuca Ultimate" in html_out
    assert "***.982.247-**" in html_out
    assert "52998224725" not in html_out  # Dados não mascarados NÃO aparecem no HTML
    assert "DECLARAÇÃO DE CONFORMIDADE E PRIVACIDADE" in html_out

