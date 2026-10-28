from typing import Any, Dict, Optional
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.phone import validate_brazilian_phone, mask_phone

class PhoneAdapter(BaseAdapter):
    adapter_id = "phone_adapter"
    name = "Plano de Numeração e Consulta Telefônica Oficial"
    category = "telefone"
    description = "Normalização padrão E.164, identificação de área geográfica (DDD), tipo de terminal (móvel/fixo) e portais legítimos de operadora e portabilidade."
    official_url = "https://consultanumero.abrtelecom.com.br"
    supported_inputs = ["telefone"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        is_valid, formatted_or_err, meta = validate_brazilian_phone(target)
        if not is_valid:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message=formatted_or_err,
                confidence=ConfidenceLevel.HIGH,
            )

        e164 = meta["e164"]
        raw_digits = meta["raw_national"]
        masked = mask_phone(formatted_or_err)

        links = [
            {
                "titulo": "ABR Telecom - Consulta de Operadora e Portabilidade",
                "url": "https://consultanumero.abrtelecom.com.br/consultanumero/",
                "descricao": "Base oficial das operadoras brasileiras (Claro, Vivo, TIM, etc.) para verificar prestadora atual e histórico de portabilidade.",
                "requer": "Resolução de CAPTCHA manual",
            },
            {
                "titulo": "Anatel - Sistema de Gestão de Numeração",
                "url": "https://sistemas.anatel.gov.br",
                "descricao": "Atribuição oficial de faixas de prefixos por operadora e localidade no Brasil.",
                "requer": "Consulta pública no portal",
            },
            {
                "titulo": "WhatsApp Web - Verificação de Presença na Rede",
                "url": f"https://wa.me/{e164.lstrip('+')}",
                "descricao": "Verificação legítima se o terminal possui conta ativa registrada no WhatsApp.",
                "requer": "Abertura no navegador",
            }
        ]

        normalized = {
            "telefone_formatado": formatted_or_err,
            "telefone_mascarado": masked,
            "padrao_e164": e164,
            "ddd": meta["ddd"],
            "regiao_atendida": meta["regiao"],
            "tipo_terminal": meta["tipo"],
            "e_celular": meta["is_mobile"],
            "fontes_oficiais": links,
        }

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=ResultStatus.CONFIRMED,
            timestamp="",
            execution_time_ms=0,
            data=normalized,
            verification_url=self.official_url,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Conformidade Legal: Não é realizada busca reversa de titularidade em bases vazadas ou clandestinas.",
                "A identificação de titular requer procedimento legal ou consulta a cadastros autorizados pelo titular.",
            ]
        )
