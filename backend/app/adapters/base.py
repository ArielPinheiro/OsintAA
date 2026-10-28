import abc
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from ..config import settings
from ..engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel

class BaseAdapter(abc.ABC):
    adapter_id: str
    name: str
    category: str
    description: str
    official_url: str
    supported_inputs: List[str]
    requires_auth: bool = False
    requires_captcha: bool = False

    def __init__(self):
        pass

    def get_client(self, timeout: Optional[float] = None) -> httpx.AsyncClient:
        """Cria cliente HTTP assíncrono com headers padronizados e timeout seguro."""
        return httpx.AsyncClient(
            timeout=timeout or settings.HTTP_TIMEOUT_SECONDS,
            headers={
                "User-Agent": settings.USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            follow_redirects=True,
            verify=True,  # Nunca desabilitar TLS
        )

    @abc.abstractmethod
    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        """Execução concreta da consulta."""
        pass

    async def execute(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        """Invólucro seguro que captura exceções, mede tempo e padroniza formato."""
        start_time = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        
        try:
            result = await self.run(target, context)
            result.execution_time_ms = round((time.time() - start_time) * 1000, 2)
            result.timestamp = now_iso
            return result
        except httpx.TimeoutException:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.UNAVAILABLE,
                timestamp=now_iso,
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                verification_url=self.official_url,
                error_message="Tempo limite esgotado ao contatar o serviço (Timeout).",
                limitations=["O serviço externo não respondeu dentro do limite seguro estipulado."],
                confidence=ConfidenceLevel.LOW,
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            status = ResultStatus.UNAVAILABLE if status_code >= 500 else ResultStatus.ERROR
            msg = f"Serviço retornou código HTTP {status_code}: {e.response.reason_phrase}"
            if status_code == 429:
                msg = "Limite de requisições excedido no serviço externo (Rate Limit)."
            elif status_code == 403:
                msg = "Acesso negado pela fonte externa (bloqueio ou exigência de autorização)."
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=status,
                timestamp=now_iso,
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                verification_url=self.official_url,
                error_message=msg,
                confidence=ConfidenceLevel.LOW,
            )
        except Exception as e:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp=now_iso,
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                verification_url=self.official_url,
                error_message=f"Falha na execução do adaptador: {str(e)}",
                confidence=ConfidenceLevel.LOW,
            )
