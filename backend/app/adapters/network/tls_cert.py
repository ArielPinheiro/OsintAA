from typing import Any, Dict, List, Optional, Set
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.domain import clean_domain

class TlsCertAdapter(BaseAdapter):
    adapter_id = "tls_cert"
    name = "Certificate Transparency e Subdomínios (crt.sh)"
    category = "dominio"
    description = "Consulta a logs públicos de transparência de certificados TLS (Certificate Transparency) para descoberta de subdomínios e histórico de certificados emitidos."
    official_url = "https://crt.sh"
    supported_inputs = ["dominio"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        domain = clean_domain(target)
        url = f"https://crt.sh/?q=%.{domain}&output=json"

        # crt.sh pode ser lento, usamos timeout adaptado
        async with self.get_client(timeout=8.0) as client:
            try:
                resp = await client.get(url)
            except (httpx.TimeoutException, httpx.HTTPError):
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.UNAVAILABLE,
                    timestamp="",
                    execution_time_ms=0,
                    verification_url=f"https://crt.sh/?q={domain}",
                    error_message="Serviço crt.sh indisponível ou tempo limite esgotado.",
                    confidence=ConfidenceLevel.LOW,
                )

            if resp.status_code != 200 or not resp.text.strip():
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.NOT_FOUND,
                    timestamp="",
                    execution_time_ms=0,
                    verification_url=f"https://crt.sh/?q={domain}",
                    error_message=f"Nenhum certificado público listado no crt.sh para '*.{domain}'.",
                    confidence=ConfidenceLevel.LOW,
                )

            try:
                raw_entries = resp.json()
            except Exception:
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.ERROR,
                    timestamp="",
                    execution_time_ms=0,
                    error_message="Resposta inesperada da base crt.sh.",
                    confidence=ConfidenceLevel.LOW,
                )

            subdomains: Set[str] = set()
            issuers: Set[str] = set()
            recent_certs = []

            for entry in raw_entries[:50]:  # Limite para evitar payload gigante
                name_value = entry.get("name_value", "")
                for sub in name_value.split("\n"):
                    sub_clean = sub.strip().lower()
                    if sub_clean and not sub_clean.startswith("*."):
                        subdomains.add(sub_clean)

                issuer = entry.get("issuer_name", "")
                if issuer:
                    # Extrair O= ou CN=
                    issuers.add(issuer.split("\n")[0][:60])

                if len(recent_certs) < 5:
                    recent_certs.append({
                        "id": entry.get("id"),
                        "logged_at": entry.get("entry_timestamp"),
                        "not_before": entry.get("not_before"),
                        "not_after": entry.get("not_after"),
                        "common_name": entry.get("common_name"),
                    })

            normalized = {
                "dominio_base": domain,
                "total_certificados_amostrados": len(raw_entries),
                "total_subdominios_descobertos": len(subdomains),
                "subdominios": sorted(list(subdomains))[:40],
                "autoridades_certificadoras": sorted(list(issuers))[:5],
                "certificados_recentes": recent_certs,
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                verification_url=f"https://crt.sh/?q={domain}",
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Subdomínios descobertos a partir de certificados TLS previamente emitidos e registrados em logs públicos de CT.",
                    "Pode incluir subdomínios históricos que não estão mais ativos na data atual.",
                ]
            )
