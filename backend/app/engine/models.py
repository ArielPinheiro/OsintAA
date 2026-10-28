from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ResultStatus(str, Enum):
    CONFIRMED = "confirmado"
    PARTIAL = "parcial"
    UNCONFIRMED = "nao_confirmado"
    NOT_FOUND = "nao_encontrado"
    ERROR = "erro"
    UNAVAILABLE = "indisponivel"
    MANUAL_STEP = "etapa_manual_necessaria"

class ConfidenceLevel(str, Enum):
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baixa"
    INFO = "informativo"

class SourceExecutionResult(BaseModel):
    source_id: str
    source_name: str
    category: str
    status: ResultStatus
    data: Optional[Dict[str, Any]] = None
    timestamp: str
    execution_time_ms: float
    verification_url: Optional[str] = None
    error_message: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.INFO
    requires_manual_action: bool = False
    action_url: Optional[str] = None

class QueryRequest(BaseModel):
    category: str = Field(..., description="Categoria de busca (ex: cnpj, cpf, dominio, ip, telefone, email, username, dados_publicos)")
    target: str = Field(..., description="Valor a pesquisar")
    source_ids: Optional[List[str]] = Field(default=None, description="Filtrar por fontes específicas (opcional)")
    save_history: bool = Field(default=False, description="Salvar no histórico local (desativado por padrão)")

class QuerySummary(BaseModel):
    total_sources: int = 0
    completed: int = 0
    partial: int = 0
    unavailable: int = 0
    failed: int = 0
    manual_steps: int = 0

class QueryResponse(BaseModel):
    query_id: str
    category: str
    target_raw: str
    target_masked: str
    started_at: str
    finished_at: str
    duration_seconds: float
    summary: QuerySummary
    results: List[SourceExecutionResult]
