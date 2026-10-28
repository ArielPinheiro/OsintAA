from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class IntegrationType(str, Enum):
    API_AUTOMATED = "api_automatizavel"
    PUBLIC_HTTP = "consulta_http_publica"
    MANUAL_ONLY = "consulta_manual"
    AUTH_REQUIRED = "autenticacao_obrigatoria"
    CAPTCHA_REQUIRED = "captcha_necessario"
    NOT_IMPLEMENTED = "integracao_nao_implementada"
    IMPLEMENTED = "integrado_funcional"
    UNAVAILABLE = "indisponivel"

class SourceLink(BaseModel):
    label: str = ""
    url: str
    uf: Optional[str] = None

class CatalogSource(BaseModel):
    id: str
    nome: str
    categoria: str
    categoria_id: str
    descricao: str = ""
    tipo_fonte: str = "indefinido"
    classificacao: str = "heuristica"
    input: List[str] = Field(default_factory=list)
    output: List[str] = Field(default_factory=list)
    links: List[SourceLink] = Field(default_factory=list)
    integration_type: IntegrationType = IntegrationType.NOT_IMPLEMENTED
    adapter_id: Optional[str] = None
    manual_notice: Optional[str] = None
    requires_auth: bool = False
    requires_captcha: bool = False

class CatalogStats(BaseModel):
    total_sources: int
    total_links: int
    categories_count: int
    implemented_adapters_count: int
    inputs_supported: List[str]
    outputs_supported: List[str]
