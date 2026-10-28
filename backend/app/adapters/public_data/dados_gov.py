from typing import Any, Dict, List, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel

class DadosGovAdapter(BaseAdapter):
    adapter_id = "dados_gov"
    name = "Portal Brasileiro de Dados Abertos (Dados.gov.br)"
    category = "dados_publicos"
    description = "Pesquisa em conjuntos de dados e repositórios oficiais disponibilizados pelos órgãos do governo federal brasileiro."
    official_url = "https://dados.gov.br"
    supported_inputs = ["nome", "razao_social", "termo"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        query = (target or "").strip()
        if not query:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message="Termo de pesquisa para dados abertos não pode ser vazio.",
                confidence=ConfidenceLevel.LOW,
            )

        # Endpoint da API pública do Dados.gov.br
        url = f"https://dados.gov.br/dados/api/publico/conjuntos-dados/pesquisa"
        params = {"q": query, "pagina": 1, "tamanho": 10}

        async with self.get_client() as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                # Fallback amigável com link oficial caso a API CKAN esteja em manutenção
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.PARTIAL,
                    timestamp="",
                    execution_time_ms=0,
                    verification_url=f"https://dados.gov.br/dados/conjuntos-dados?q={query}",
                    data={
                        "termo_pesquisado": query,
                        "link_direto_busca": f"https://dados.gov.br/dados/conjuntos-dados?q={query}",
                    },
                    error_message=f"API temporariamente instável ({str(e)}). Link de consulta web gerado com sucesso.",
                    confidence=ConfidenceLevel.MEDIUM,
                )

            itens = []
            raw_records = data.get("registros", []) if isinstance(data, dict) else []
            for item in raw_records[:8]:
                itens.append({
                    "titulo": item.get("titulo"),
                    "descricao": (item.get("descricao") or "")[:200] + "...",
                    "orgao": item.get("organizacao", {}).get("nome") if isinstance(item.get("organizacao"), dict) else item.get("organizacao"),
                    "link_detalhes": f"https://dados.gov.br/dados/conjuntos-dados/{item.get('id')}",
                    "modificado_em": item.get("dataModificacao"),
                })

            normalized = {
                "termo_pesquisado": query,
                "total_conjuntos_encontrados": data.get("totalRegistros", len(itens)),
                "conjuntos_dados": itens,
                "portal_busca_url": f"https://dados.gov.br/dados/conjuntos-dados?q={query}",
            }

            status = ResultStatus.CONFIRMED if itens else ResultStatus.NOT_FOUND

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=status,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                verification_url=f"https://dados.gov.br/dados/conjuntos-dados?q={query}",
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Resultados indexados pela infraestrutura oficial de Dados Abertos do Governo Federal (Dados.gov.br).",
                ]
            )

