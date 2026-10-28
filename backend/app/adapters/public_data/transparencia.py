from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel

class TransparenciaGovAdapter(BaseAdapter):
    adapter_id = "transparencia_gov"
    name = "Portal da Transparência, Compras Públicas e Diários Oficiais"
    category = "dados_publicos"
    description = "Geração de consultas e cruzamento de dados com portais federais de transparência, licitações públicas (Compras.gov.br), sanções (CEIS/CNEP) e Diário Oficial da União."
    official_url = "https://portaldatransparencia.gov.br"
    supported_inputs = ["cnpj", "nome", "razao_social", "termo"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        term = (target or "").strip()
        encoded = quote_plus(term)

        portais = [
            {
                "orgao": "Controladoria-Geral da União (CGU)",
                "sistema": "Portal da Transparência - Busca Integrada",
                "tipo": "Despesas, Servidores, Licitações e Contratos",
                "url": f"https://portaldatransparencia.gov.br/busca?termo={encoded}",
                "requer_autenticacao": False,
            },
            {
                "orgao": "Controladoria-Geral da União (CGU)",
                "sistema": "Cadastro de Empresas Inidôneas e Suspensas (CEIS)",
                "tipo": "Sanções administrativas que impedem contratar com o poder público",
                "url": f"https://portaldatransparencia.gov.br/sancoes/ceis?termo={encoded}",
                "requer_autenticacao": False,
            },
            {
                "orgao": "Controladoria-Geral da União (CGU)",
                "sistema": "Cadastro Nacional de Empresas Punidas (CNEP)",
                "tipo": "Sanções da Lei Anticorrupção (Lei 12.846/2013)",
                "url": f"https://portaldatransparencia.gov.br/sancoes/cnep?termo={encoded}",
                "requer_autenticacao": False,
            },
            {
                "orgao": "Ministério da Gestão e Inovação (MGI)",
                "sistema": "Portal Nacional de Contratações Públicas (PNCP / Compras.gov.br)",
                "tipo": "Editais, atas de registro de preço e contratações diretas",
                "url": f"https://pncp.gov.br/app/editais?q={encoded}",
                "requer_autenticacao": False,
            },
            {
                "orgao": "Imprensa Nacional",
                "sistema": "Diário Oficial da União (DOU)",
                "tipo": "Publicações oficiais de atos governamentais, nomeações e contratos",
                "url": f"https://www.in.gov.br/consulta/-/buscar/dou?q={encoded}",
                "requer_autenticacao": False,
            },
            {
                "orgao": "Open Knowledge Brasil",
                "sistema": "Querido Diário (Diários Oficiais Municipais)",
                "tipo": "Pesquisa em diários oficiais de municípios brasileiros",
                "url": f"https://queridodiario.ok.org.br/busca?query={encoded}",
                "requer_autenticacao": False,
            }
        ]

        normalized = {
            "termo_investigado": term,
            "portais_oficiais_estruturados": portais,
            "total_portais_configurados": len(portais),
        }

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=ResultStatus.CONFIRMED,
            timestamp="",
            execution_time_ms=0,
            data=normalized,
            verification_url=f"https://portaldatransparencia.gov.br/busca?termo={encoded}",
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Links parametrizados e compatíveis com a arquitetura oficial dos portais governamentais.",
                "Não requer autenticação prévia nem violação de termos de uso.",
            ]
        )

