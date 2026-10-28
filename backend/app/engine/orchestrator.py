import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..config import settings
from .models import (
    ConfidenceLevel,
    QueryRequest,
    QueryResponse,
    QuerySummary,
    ResultStatus,
    SourceExecutionResult,
)
from ..adapters.base import BaseAdapter
from ..adapters.cnpj.brasilapi_cnpj import BrasilApiCnpjAdapter
from ..adapters.cnpj.receitaws_cnpj import ReceitaWsCnpjAdapter
from ..adapters.network.rdap_domain import RdapDomainAdapter
from ..adapters.network.dns_records import DnsRecordsAdapter
from ..adapters.network.rdap_ip import RdapIpAdapter
from ..adapters.network.ip_geolocation import IpGeolocationAdapter
from ..adapters.network.tls_cert import TlsCertAdapter
from ..adapters.network.http_probe import HttpProbeAdapter
from ..adapters.cpf.cpf_adapter import CpfOfficialAdapter
from ..adapters.email.email_adapter import EmailAdapter
from ..adapters.phone.phone_adapter import PhoneAdapter
from ..adapters.username.username_adapter import UsernameAdapter
from ..adapters.documents.document_analyzer import DocumentAnalyzerAdapter
from ..adapters.public_data.dados_gov import DadosGovAdapter
from ..adapters.public_data.transparencia import TransparenciaGovAdapter

from ..validators.cpf import validate_cpf, mask_cpf
from ..validators.cnpj import validate_cnpj, format_cnpj
from ..validators.domain import validate_domain
from ..validators.ip import validate_ip
from ..validators.phone import validate_brazilian_phone, mask_phone
from ..validators.email import validate_email, mask_email

class QueryEngine:
    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        self._register_adapters()

    def _register_adapters(self):
        adapter_classes = [
            BrasilApiCnpjAdapter,
            ReceitaWsCnpjAdapter,
            RdapDomainAdapter,
            DnsRecordsAdapter,
            TlsCertAdapter,
            HttpProbeAdapter,
            RdapIpAdapter,
            IpGeolocationAdapter,
            CpfOfficialAdapter,
            EmailAdapter,
            PhoneAdapter,
            UsernameAdapter,
            DocumentAnalyzerAdapter,
            DadosGovAdapter,
            TransparenciaGovAdapter,
        ]
        for cls in adapter_classes:
            instance = cls()
            self._adapters[instance.adapter_id] = instance

    def get_registered_adapters(self) -> Dict[str, BaseAdapter]:
        return self._adapters

    def normalize_target_and_mask(self, category: str, target: str) -> tuple[bool, str, str, str]:
        """
        Valida e normaliza o dado de entrada conforme a categoria.
        Retorna (is_valid, normalized_target, masked_target, error_msg).
        """
        cat = category.lower().strip()
        t = (target or "").strip()

        if not t:
            return False, "", "", "O valor de entrada não pode ser vazio."

        if cat == "cpf":
            valid, res = validate_cpf(t)
            if not valid:
                return False, "", "", res
            return True, res, mask_cpf(res), ""

        elif cat == "cnpj":
            valid, res = validate_cnpj(t)
            if not valid:
                return False, "", "", res
            formatted = format_cnpj(res)
            return True, res, formatted, ""

        elif cat in ("dominio", "domain", "site"):
            valid, res = validate_domain(t)
            if not valid:
                return False, "", "", res
            return True, res, res, ""

        elif cat in ("ip", "rede"):
            valid, res, is_pub = validate_ip(t)
            if not valid:
                return False, "", "", res
            return True, res, res, ""

        elif cat in ("telefone", "phone"):
            valid, res, meta = validate_brazilian_phone(t)
            if not valid:
                return False, "", "", res
            return True, meta["raw_national"], mask_phone(res), ""

        elif cat in ("email", "e-mail"):
            valid, res, meta = validate_email(t)
            if not valid:
                return False, "", "", res
            return True, res, mask_email(res), ""

        elif cat in ("username", "perfil"):
            clean_u = t.lstrip("@").strip()
            if not clean_u:
                return False, "", "", "Username inválido."
            return True, clean_u, clean_u, ""

        elif cat in ("documentos", "arquivos", "hash"):
            return True, t, t[:8] + "..." if len(t) > 20 else t, ""

        elif cat in ("dados_publicos", "public_data", "geral"):
            return True, t, t, ""

        return True, t, t, ""

    def select_adapters(self, category: str, source_ids: Optional[List[str]] = None) -> List[BaseAdapter]:
        """Seleciona adaptadores compatíveis com a categoria solicitada."""
        cat = category.lower().strip()
        category_aliases = {
            "cpf": ["cpf"],
            "cnpj": ["cnpj"],
            "dominio": ["dominio"],
            "domain": ["dominio"],
            "site": ["dominio"],
            "ip": ["ip"],
            "rede": ["ip"],
            "telefone": ["telefone"],
            "phone": ["telefone"],
            "email": ["email"],
            "e-mail": ["email"],
            "username": ["username"],
            "perfil": ["username"],
            "documentos": ["documentos"],
            "arquivos": ["documentos"],
            "dados_publicos": ["dados_publicos"],
            "public_data": ["dados_publicos"],
        }
        
        target_cats = category_aliases.get(cat, [cat])
        matched: List[BaseAdapter] = []

        for adapter in self._adapters.values():
            if adapter.category in target_cats:
                if source_ids is None or adapter.adapter_id in source_ids:
                    matched.append(adapter)

        # Se CNPJ pesquisado em dados públicos, incluir também transparência
        if cat == "cnpj" and "transparencia_gov" in self._adapters:
            matched.append(self._adapters["transparencia_gov"])

        return matched

    async def execute_query(
        self,
        request: QueryRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryResponse:
        """Executa consultas coordenadas com limite de concorrência e isolamento de falhas."""
        query_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()
        start_clock = time.time()

        # Validação
        is_valid, normalized_target, masked_target, err_msg = self.normalize_target_and_mask(
            request.category, request.target
        )

        if not is_valid:
            finished_at = datetime.now(timezone.utc).isoformat()
            duration = round(time.time() - start_clock, 2)
            error_result = SourceExecutionResult(
                source_id="engine_validator",
                source_name="Validador Central",
                category=request.category,
                status=ResultStatus.ERROR,
                timestamp=started_at,
                execution_time_ms=0,
                error_message=err_msg,
                confidence=ConfidenceLevel.HIGH,
            )
            return QueryResponse(
                query_id=query_id,
                category=request.category,
                target_raw=request.target,
                target_masked=request.target,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                summary=QuerySummary(total_sources=1, failed=1),
                results=[error_result],
            )

        # Seleção de adaptadores
        adapters = self.select_adapters(request.category, request.source_ids)

        if not adapters:
            finished_at = datetime.now(timezone.utc).isoformat()
            duration = round(time.time() - start_clock, 2)
            not_impl = SourceExecutionResult(
                source_id="no_adapter",
                source_name="Orquestrador de Consultas",
                category=request.category,
                status=ResultStatus.UNAVAILABLE,
                timestamp=started_at,
                execution_time_ms=0,
                error_message=f"Nenhum adaptador automatizado disponível para a categoria '{request.category}'. Consulte o catálogo de fontes manuais.",
                confidence=ConfidenceLevel.INFO,
            )
            return QueryResponse(
                query_id=query_id,
                category=request.category,
                target_raw=normalized_target,
                target_masked=masked_target,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                summary=QuerySummary(total_sources=1, unavailable=1),
                results=[not_impl],
            )

        # Concorrência controlada por semáforo
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

        async def run_safe(adp: BaseAdapter) -> SourceExecutionResult:
            async with semaphore:
                return await adp.execute(normalized_target, context)

        # Execução concorrente
        tasks = [run_safe(adp) for adp in adapters]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        finished_at = datetime.now(timezone.utc).isoformat()
        duration = round(time.time() - start_clock, 2)

        # Estatísticas
        completed = sum(1 for r in results if r.status in (ResultStatus.CONFIRMED, ResultStatus.NOT_FOUND))
        partial = sum(1 for r in results if r.status == ResultStatus.PARTIAL)
        unavailable = sum(1 for r in results if r.status == ResultStatus.UNAVAILABLE)
        failed = sum(1 for r in results if r.status == ResultStatus.ERROR)
        manual = sum(1 for r in results if r.requires_manual_action)

        summary = QuerySummary(
            total_sources=len(results),
            completed=completed,
            partial=partial,
            unavailable=unavailable,
            failed=failed,
            manual_steps=manual,
        )

        return QueryResponse(
            query_id=query_id,
            category=request.category,
            target_raw=normalized_target,
            target_masked=masked_target,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration,
            summary=summary,
            results=results,
        )

query_engine = QueryEngine()

