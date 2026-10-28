import os
from pathlib import Path
from typing import List

class Settings:
    PROJECT_NAME: str = "OSINT Brazuca Ultimate"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Central de Investigação por Fontes Abertas Brasileiras"
    
    # Rede e Segurança - Sempre local por padrão
    LISTEN_HOST: str = os.getenv("OSINT_HOST", "127.0.0.1")
    LISTEN_PORT: int = int(os.getenv("OSINT_PORT", "8000"))
    
    # Privacidade: NUNCA salvar histórico por padrão
    ENABLE_HISTORY: bool = os.getenv("OSINT_ENABLE_HISTORY", "false").lower() in ("true", "1", "yes")
    LOG_SENSITIVE_DATA: bool = False
    
    # Concorrência e Timeouts
    HTTP_TIMEOUT_SECONDS: float = float(os.getenv("OSINT_TIMEOUT", "12.0"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("OSINT_MAX_CONCURRENCY", "5"))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("OSINT_MAX_UPLOAD_MB", "15"))
    
    # User-Agent ético e transparente (puro ASCII para conformidade HTTP)
    USER_AGENT: str = os.getenv(
        "OSINT_USER_AGENT",
        "OSINT-Brazuca-Ultimate/1.0 (Pesquisa Legitima em Fontes Abertas; contato@osintbrazuca.local)"
    )
    
    # Caminhos para o Catálogo de Dados
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    @classmethod
    def get_catalog_file(cls, filename: str) -> Path:
        """Busca o arquivo de catálogo em múltiplos locais possíveis."""
        candidates = [
            cls.BASE_DIR / "data" / filename,
            cls.BASE_DIR / "osint-brazuca-main" / "data" / filename,
            Path("data") / filename,
            Path("osint-brazuca-main") / "data" / filename,
            Path("..") / "osint-brazuca-main" / "data" / filename,
            Path("..") / "data" / filename,
        ]
        for c in candidates:
            if c.exists():
                return c.resolve()
        # Fallback para o primeiro candidato
        return (cls.BASE_DIR / "osint-brazuca-main" / "data" / filename).resolve()

settings = Settings()
