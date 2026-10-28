import re
from typing import Any, Dict, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.domain import clean_domain
from ...validators.sanitization import is_safe_url

TITLE_REGEX = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)

class HttpProbeAdapter(BaseAdapter):
    adapter_id = "http_probe"
    name = "Sondagem HTTP / HTTPS e Cabeçalhos"
    category = "dominio"
    description = "Verificação passiva de disponibilidade web, redirecionamentos, título de página e cabeçalhos de servidor."
    official_url = "https://developer.mozilla.org/pt-BR/docs/Web/HTTP"
    supported_inputs = ["dominio"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        domain = clean_domain(target)
        target_url = f"https://{domain}"

        if not is_safe_url(target_url):
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message="Destino bloqueado por políticas de segurança SSRF.",
                confidence=ConfidenceLevel.LOW,
            )

        async with self.get_client(timeout=6.0) as client:
            resp = None
            used_protocol = "https"
            try:
                resp = await client.get(target_url)
            except Exception:
                # Tentar http puro se https falhou
                try:
                    target_url = f"http://{domain}"
                    resp = await client.get(target_url)
                    used_protocol = "http"
                except Exception as e:
                    return SourceExecutionResult(
                        source_id=self.adapter_id,
                        source_name=self.name,
                        category=self.category,
                        status=ResultStatus.NOT_FOUND,
                        timestamp="",
                        execution_time_ms=0,
                        error_message=f"Servidor web não respondeu em HTTP/HTTPS: {str(e)}",
                        confidence=ConfidenceLevel.MEDIUM,
                    )

            title = None
            if resp and "text/html" in resp.headers.get("content-type", ""):
                match = TITLE_REGEX.search(resp.text[:4096])
                if match:
                    title = match.group(1).strip()

            headers_sample = {}
            for h in ["server", "content-type", "x-powered-by", "strict-transport-security", "x-frame-options"]:
                if h in resp.headers:
                    headers_sample[h] = resp.headers[h]

            normalized = {
                "url_final": str(resp.url),
                "protocolo": used_protocol,
                "status_code": resp.status_code,
                "titulo_pagina": title,
                "cabecalhos_identificados": headers_sample,
                "redirecionamentos": [str(r.url) for r in resp.history],
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                verification_url=str(resp.url),
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Sondagem HTTP passiva e legítima respeitando cabeçalho padrão de requisição.",
                ]
            )
