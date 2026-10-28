from typing import Any, Dict, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.ip import validate_ip

class IpGeolocationAdapter(BaseAdapter):
    adapter_id = "ip_geolocation"
    name = "Geolocalização e Roteamento de Rede IP"
    category = "ip"
    description = "Consulta de geolocalização aproximada do ponto de presença (PoP) de rede, provedor e ASN."
    official_url = "https://ip-api.com"
    supported_inputs = ["ip"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        is_valid, ip_str, is_public = validate_ip(target)
        if not is_valid or not is_public:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.PARTIAL,
                timestamp="",
                execution_time_ms=0,
                error_message="IP privado ou inválido para geolocalização pública.",
                confidence=ConfidenceLevel.INFO,
            )

        url = f"http://ip-api.com/json/{ip_str}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"

        async with self.get_client() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") == "fail":
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.NOT_FOUND,
                    timestamp="",
                    execution_time_ms=0,
                    error_message=data.get("message", "IP não localizado na base geo."),
                    confidence=ConfidenceLevel.LOW,
                )

            normalized = {
                "ip": ip_str,
                "pais": data.get("country"),
                "codigo_pais": data.get("countryCode"),
                "regiao_estado": data.get("regionName"),
                "cidade": data.get("city"),
                "cep_aproximado": data.get("zip"),
                "coordenadas_aproximadas": {
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon"),
                },
                "fuso_horario": data.get("timezone"),
                "provedor_isp": data.get("isp"),
                "organizacao": data.get("org"),
                "asn": data.get("as"),
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                confidence=ConfidenceLevel.MEDIUM,
                limitations=[
                    "ATENÇÃO DE PRECISÃO: Geolocalização de IP reflete apenas o Ponto de Presença (PoP) ou data center do provedor de acesso/rede.",
                    "NUNCA indica a residência, equipamento ou localização física exata de uma pessoa.",
                ]
            )
