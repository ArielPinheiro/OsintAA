import re
from typing import Tuple
from urllib.parse import urlparse

DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

BLOCKED_DOMAINS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "internal",
    "local",
    "lan",
    "corp",
}

def clean_domain(raw_input: str) -> str:
    """Extrai o domínio limpo caso o usuário cole uma URL completa."""
    cleaned = (raw_input or "").strip().lower()
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        parsed = urlparse(cleaned)
        cleaned = parsed.netloc or parsed.path
    
    # Remover porta se houver
    if ":" in cleaned:
        cleaned = cleaned.split(":")[0]

    # Remover barra final se sobrou
    cleaned = cleaned.strip("/")
    return cleaned

def validate_domain(domain_str: str) -> Tuple[bool, str]:
    """
    Valida formato de nome de domínio FQDN.
    Retorna (is_valid, domain_normalizado_ou_erro).
    """
    domain = clean_domain(domain_str)
    if not domain:
        return False, "Nome de domínio não pode ser vazio."

    if len(domain) > 253:
        return False, "Domínio excede o tamanho máximo de 253 caracteres."

    if domain in BLOCKED_DOMAINS or domain.endswith(".local") or domain.endswith(".internal"):
        return False, "Domínio interno ou reservado não permitido para consultas públicas."

    if not DOMAIN_REGEX.match(domain):
        return False, f"Formato de domínio inválido: '{domain}'."

    return True, domain
