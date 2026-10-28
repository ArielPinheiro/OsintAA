from typing import Any, Dict, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.domain import clean_domain

class RdapDomainAdapter(BaseAdapter):
    adapter_id = "rdap_domain"
    name = "RDAP / WHOIS Oficial de Domínio"
    category = "dominio"
    description = "Consulta oficial ao protocolo RDAP (Registration Data Access Protocol) via Registro.br para domínios .br e ICANN RDAP para domínios internacionais."
    official_url = "https://registro.br"
    supported_inputs = ["dominio"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        domain = clean_domain(target)
        is_br = domain.endswith(".br")
        
        if is_br:
            url = f"https://rdap.registro.br/domain/{domain}"
            official_link = f"https://registro.br/tecnologia/ferramentas/whois?search={domain}"
        else:
            url = f"https://rdap.org/domain/{domain}"
            official_link = f"https://lookup.icann.org/en/lookup?q={domain}"

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
                    verification_url=official_link,
                    error_message=f"Domínio '{domain}' não encontrado ou disponível para registro.",
                    confidence=ConfidenceLevel.HIGH,
                )

            resp.raise_for_status()
            data = resp.json()

            # Extração padronizada de eventos (criação, expiração, alteração)
            events_dict = {}
            for ev in data.get("events", []):
                act = ev.get("eventAction")
                d = ev.get("eventDate")
                if act and d:
                    events_dict[act] = d

            # Servidores DNS
            nameservers = []
            for ns in data.get("nameservers", []):
                ldh = ns.get("ldhName")
                if ldh:
                    nameservers.append(ldh)

            # Entidades (titular, contato técnico, cobrança)
            entities = []
            for ent in data.get("entities", []):
                vcard_entries = {}
                vcard = ent.get("vcardArray", [])
                if len(vcard) > 1 and isinstance(vcard[1], list):
                    for item in vcard[1]:
                        if len(item) >= 4:
                            vcard_entries[item[0]] = item[3]

                roles = ent.get("roles", [])
                entities.append({
                    "handle": ent.get("handle"),
                    "roles": roles,
                    "nome_ou_razao": vcard_entries.get("fn"),
                    "email": vcard_entries.get("email"),
                    "entidade_legal": ent.get("publicIds", []),
                })

            normalized = {
                "dominio": domain,
                "handle": data.get("handle"),
                "status": data.get("status", []),
                "data_criacao": events_dict.get("registration"),
                "data_expiracao": events_dict.get("expiration"),
                "ultima_alteracao": events_dict.get("last changed") or events_dict.get("last update"),
                "servidores_dns": nameservers,
                "entidades_responsaveis": entities,
                "portar_whois": data.get("port43"),
            }

            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data=normalized,
                verification_url=official_link,
                confidence=ConfidenceLevel.HIGH,
                limitations=[
                    "Dados obtidos diretamente do registro autoritativo oficial via protocolo RDAP.",
                    "Certos dados de pessoas físicas podem ser restritos por políticas de privacidade do registrador e LGPD.",
                ]
            )
