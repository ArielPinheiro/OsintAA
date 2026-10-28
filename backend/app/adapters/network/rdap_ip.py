from typing import Any, Dict, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.ip import validate_ip

class RdapIpAdapter(BaseAdapter):
    adapter_id = "rdap_ip"
    name = "RDAP IP / ASN Oficial (Registro.br / RIR)"
    category = "ip"
    description = "Consulta de blocos de endereçamento IP, ASN e entidade detentora via protocolo RDAP oficial."
    official_url = "https://registro.br"
    supported_inputs = ["ip"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        is_valid, ip_str, is_public = validate_ip(target)
        if not is_valid:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message=ip_str,
                confidence=ConfidenceLevel.LOW,
            )

        if not is_public:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.PARTIAL,
                timestamp="",
                execution_time_ms=0,
                error_message="O IP informado pertence a uma faixa privada, reservada ou de loopback. Consultas públicas externas não são aplicáveis.",
                confidence=ConfidenceLevel.INFO,
                limitations=["IP de uso interno não publicado em registros públicos da Internet (RFC 1918 / RFC 5737)."]
            )

        # Tentativa primária no Registro.br (LACNIC / Brasil), fallback para rdap.org
        primary_url = f"https://rdap.registro.br/ip/{ip_str}"
        fallback_url = f"https://rdap.org/ip/{ip_str}"

        async with self.get_client() as client:
            resp = None
            try:
                resp = await client.get(primary_url)
                if resp.status_code != 200:
                    resp = await client.get(fallback_url)
            except Exception:
                resp = await client.get(fallback_url)

            if resp.status_code == 404:
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.NOT_FOUND,
                    timestamp="",
                    execution_time_ms=0,
                    error_message=f"Registro RDAP não localizado para o IP {ip_str}.",
                    confidence=ConfidenceLevel.MEDIUM,
                )

            resp.raise_for_status()
            data = resp.json()

            # Extração de entidades
            entities = []
            for ent in data.get("entities", []):
                roles = ent.get("roles", [])
                vcard = ent.get("vcardArray", [])
                fn = None
                if len(vcard) > 1 and isinstance(vcard[1], list):
                    for item in vcard[1]:
                        if len(item) >= 4 and item[0] == "fn":
                            fn = item[3]
                entities.append({
                    "handle": ent.get("handle"),
                    "nome_entidade": fn,
                    "roles": roles,
                })

            normalized = {
                "ip": ip_str,
                "handle": data.get("handle"),
                "faixa_inicio": data.get("startAddress"),
                "faixa_fim": data.get("endAddress"),
                "ip_versao": data.get("ipVersion"),
                "nome_rede": data.get("name"),
                "tipo_rede": data.get("type"),
                "pais": data.get("country"),
                "entidades_responsaveis": entities,
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Dados institucionais obtidos do Registro Regional da Internet (RIR) correspondente.",
                ]
            )
