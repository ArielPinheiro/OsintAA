import asyncio
from typing import Any, Dict, Optional
import dns.resolver
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.email import validate_email, mask_email

class EmailAdapter(BaseAdapter):
    adapter_id = "email_adapter"
    name = "Validador e Auditoria de E-mail"
    category = "email"
    description = "Validação RFC, análise dos registros MX do provedor de correio, SPF, DMARC e detecção de domínio temporário descartável."
    official_url = "https://www.ietf.org/rfc/rfc5322.txt"
    supported_inputs = ["email"]

    def _check_domain_dns(self, domain: str) -> Dict[str, Any]:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 3.0

        mx_records = []
        try:
            answers = resolver.resolve(domain, "MX")
            for r in answers:
                mx_records.append(str(r.exchange).rstrip("."))
        except Exception:
            pass

        spf_record = None
        try:
            answers = resolver.resolve(domain, "TXT")
            for r in answers:
                s = str(r)
                if "v=spf1" in s:
                    spf_record = s
                    break
        except Exception:
            pass

        dmarc_record = None
        try:
            answers = resolver.resolve(f"_dmarc.{domain}", "TXT")
            for r in answers:
                dmarc_record = str(r)
                break
        except Exception:
            pass

        return {
            "mx_records": mx_records,
            "has_mx": len(mx_records) > 0,
            "spf_record": spf_record,
            "has_spf": spf_record is not None,
            "dmarc_record": dmarc_record,
            "has_dmarc": dmarc_record is not None,
        }

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        is_valid, email_clean, meta = validate_email(target)
        if not is_valid:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message=email_clean,
                confidence=ConfidenceLevel.HIGH,
            )

        domain = meta["domain"]
        user = meta["user"]
        masked = mask_email(email_clean)

        loop = asyncio.get_event_loop()
        dns_res = await loop.run_in_executor(None, self._check_domain_dns, domain)

        normalized = {
            "email_mascarado": masked,
            "usuario_comprimento": len(user),
            "dominio": domain,
            "e_descartavel": meta["is_disposable"],
            "servidores_mx_configurados": dns_res["mx_records"],
            "dominio_recebe_emails": dns_res["has_mx"],
            "possui_spf": dns_res["has_spf"],
            "registro_spf": dns_res["spf_record"],
            "possui_dmarc": dns_res["has_dmarc"],
            "servicos_verificacao_vazamentos": [
                {
                    "nome": "Have I Been Pwned",
                    "url": f"https://haveibeenpwned.com",
                    "tipo": "Verificação oficial e ética de vazamentos públicos",
                }
            ]
        }

        status = ResultStatus.CONFIRMED if dns_res["has_mx"] else ResultStatus.PARTIAL

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=status,
            timestamp="",
            execution_time_ms=0,
            data=normalized,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "NENHUMA mensagem de teste foi enviada à caixa de correio.",
                "A existência de servidores MX comprova que o domínio está apto a receber mensagens, mas a existência da conta específica só pode ser verificada com consentimento.",
            ]
        )
