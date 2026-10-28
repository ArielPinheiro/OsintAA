from typing import Any, Dict, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.cnpj import clean_digits, format_cnpj

class BrasilApiCnpjAdapter(BaseAdapter):
    adapter_id = "brasilapi_cnpj"
    name = "BrasilAPI - Consulta CNPJ e QSA"
    category = "cnpj"
    description = "Consulta pública consolidada da Receita Federal via BrasilAPI, incluindo dados cadastrais, CNAEs e Quadro de Sócios e Administradores (QSA)."
    official_url = "https://brasilapi.com.br"
    supported_inputs = ["cnpj"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        clean = clean_digits(target)
        formatted = format_cnpj(clean)
        url = f"https://brasilapi.com.br/api/cnpj/v1/{clean}"

        async with self.get_client() as client:
            resp = await client.get(url)
            
            if resp.status_code == 404:
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.NOT_FOUND,
                    timestamp="",
                    execution_time_ms=0,
                    verification_url=f"https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp",
                    error_message=f"CNPJ {formatted} não encontrado na base pública da Receita Federal.",
                    confidence=ConfidenceLevel.HIGH,
                )

            resp.raise_for_status()
            data = resp.json()

            # Normalização de dados
            qsa_clean = []
            for socio in data.get("qsa", []):
                qsa_clean.append({
                    "nome_socio": socio.get("nome_socio"),
                    "qualificacao": socio.get("qualificacao_socio"),
                    "faixa_etaria": socio.get("faixa_etaria"),
                    "data_entrada_sociedade": socio.get("data_entrada_sociedade"),
                    "pais": socio.get("pais"),
                })

            normalized = {
                "cnpj": formatted,
                "razao_social": data.get("razao_social"),
                "nome_fantasia": data.get("nome_fantasia") or "(Não informado)",
                "situacao_cadastral": data.get("descricao_situacao_cadastral"),
                "data_situacao_cadastral": data.get("data_situacao_cadastral"),
                "data_inicio_atividade": data.get("data_inicio_atividade"),
                "natureza_juridica": data.get("natureza_juridica"),
                "porte": data.get("porte"),
                "capital_social": data.get("capital_social"),
                "cnae_principal": {
                    "codigo": data.get("cnae_fiscal"),
                    "descricao": data.get("cnae_fiscal_descricao"),
                },
                "cnaes_secundarios": [
                    {"codigo": c.get("codigo"), "descricao": c.get("texto")}
                    for c in data.get("cnaes_secundarios", [])
                ],
                "endereco": {
                    "logradouro": data.get("logradouro"),
                    "numero": data.get("numero"),
                    "complemento": data.get("complemento"),
                    "bairro": data.get("bairro"),
                    "municipio": data.get("municipio"),
                    "uf": data.get("uf"),
                    "cep": data.get("cep"),
                },
                "qsa_socios": qsa_clean,
                "qsa_total": len(qsa_clean),
                "motivo_situacao_cadastral": data.get("descricao_motivo_situacao_cadastral"),
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                verification_url=f"https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp",
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Dados originados da base pública oficial de CNPJ aberta da Receita Federal.",
                    "Atualizado periodicamente conforme repositório de dados públicos do governo.",
                ]
            )
