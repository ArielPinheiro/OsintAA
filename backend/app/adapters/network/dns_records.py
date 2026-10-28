import asyncio
from typing import Any, Dict, List, Optional
import dns.resolver
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.domain import clean_domain

class DnsRecordsAdapter(BaseAdapter):
    adapter_id = "dns_records"
    name = "Resolução DNS e Infraestrutura de Rede"
    category = "dominio"
    description = "Resolução de registros DNS oficiais (A, AAAA, MX, NS, TXT, CNAME, SOA) e verificação de políticas de e-mail (SPF, DMARC)."
    official_url = "https://www.iana.org/domains/root"
    supported_inputs = ["dominio"]

    def _resolve_sync(self, domain: str) -> Dict[str, Any]:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 3.0

        records: Dict[str, List[str]] = {
            "A": [],
            "AAAA": [],
            "MX": [],
            "NS": [],
            "TXT": [],
            "CNAME": [],
            "SOA": [],
        }

        for qtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
            try:
                answers = resolver.resolve(domain, qtype)
                for rdata in answers:
                    records[qtype].append(str(rdata))
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
                pass
            except Exception:
                pass

        # Verificar DMARC (_dmarc.domain)
        dmarc_records = []
        try:
            answers = resolver.resolve(f"_dmarc.{domain}", "TXT")
            for rdata in answers:
                dmarc_records.append(str(rdata))
        except Exception:
            pass

        # Detecção de políticas
        spf_found = [txt for txt in records["TXT"] if "v=spf1" in txt]

        return {
            "dominio": domain,
            "registros_a": records["A"],
            "registros_aaaa": records["AAAA"],
            "servidores_mx": records["MX"],
            "servidores_ns": records["NS"],
            "registros_txt": records["TXT"],
            "cname": records["CNAME"],
            "soa": records["SOA"],
            "dmarc": dmarc_records,
            "tem_spf": len(spf_found) > 0,
            "spf_conteudo": spf_found[0] if spf_found else None,
            "tem_dmarc": len(dmarc_records) > 0,
        }

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        domain = clean_domain(target)
        loop = asyncio.get_event_loop()
        dns_data = await loop.run_in_executor(None, self._resolve_sync, domain)

        has_any = any(
            dns_data[k] for k in ["registros_a", "registros_aaaa", "servidores_mx", "servidores_ns", "registros_txt", "cname"]
        )

        if not has_any:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.NOT_FOUND,
                timestamp="",
                execution_time_ms=0,
                error_message=f"Nenhum registro DNS localizado para o domínio '{domain}'.",
                confidence=ConfidenceLevel.MEDIUM,
            )

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=ResultStatus.CONFIRMED,
            timestamp="",
            execution_time_ms=0,
            data=dns_data,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Resoluções efetuadas diretamente contra servidores DNS recursivos confiáveis.",
            ]
        )
