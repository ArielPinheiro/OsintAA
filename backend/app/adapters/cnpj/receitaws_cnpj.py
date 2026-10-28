from typing import Any, Dict, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.cnpj import clean_digits, format_cnpj

class ReceitaWsCnpjAdapter(BaseAdapter):
    adapter_id = "receitaws_cnpj"
    name = "ReceitaWS - Consulta Pública Complementar"
    category = "cnpj"
    description = "Consulta complementar de informações cadastrais e contatos públicos de pessoas jurídicas."
    official_url = "https://www.receitaws.com.br"
    supported_inputs = ["cnpj"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        clean = clean_digits(target)
        formatted = format_cnpj(clean)
        url = f"https://www.receitaws.com.br/v1/cnpj/{clean}"

        async with self.get_client() as client:
            resp = await client.get(url)
            
            if resp.status_code == 429:
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.UNAVAILABLE,
                    timestamp="",
                    execution_time_ms=0,
                    verification_url=self.official_url,
                    error_message="Limite de consultas por minuto da API pública atingido (3 consultas/min).",
                    confidence=ConfidenceLevel.LOW,
                )

            resp.raise_for_status()
            data = resp.json()

            if data.get("status") == "ERROR":
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.NOT_FOUND,
                    timestamp="",
                    execution_time_ms=0,
                    verification_url=self.official_url,
                    error_message=data.get("message", "CNPJ não localizado."),
                    confidence=ConfidenceLevel.MEDIUM,
                )

            normalized = {
                "cnpj": formatted,
                "razao_social": data.get("nome"),
                "fantasia": data.get("fantasia"),
                "situacao": data.get("situacao"),
                "motivo_situacao": data.get("motivo_situacao"),
                "data_situacao": data.get("data_situacao"),
                "tipo": data.get("tipo"),
                "porte": data.get("porte"),
                "email_publico": data.get("email"),
                "telefone_publico": data.get("telefone"),
                "ultima_atualizacao": data.get("ultima_atualizacao"),
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                verification_url=f"https://www.receitaws.com.br/cnpj/{clean}",
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Informações cadastrais públicas mantidas pelo serviço ReceitaWS.",
                ]
            )
