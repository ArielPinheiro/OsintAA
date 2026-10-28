import ipaddress
from typing import Tuple

def validate_ip(ip_str: str) -> Tuple[bool, str, bool]:
    """
    Valida um endereço IPv4 ou IPv6.
    Retorna (is_valid, ip_normalizado_ou_erro, is_public).
    Bloqueia entradas malformadas e sinaliza redes privadas/locais para prevenção de SSRF.
    """
    cleaned = (ip_str or "").strip()
    try:
        ip_obj = ipaddress.ip_address(cleaned)
    except ValueError:
        return False, "Endereço IP inválido (não é IPv4 nem IPv6 válido).", False

    is_public = ip_obj.is_global and not ip_obj.is_private and not ip_obj.is_loopback and not ip_obj.is_reserved

    return True, str(ip_obj), is_public

def is_safe_public_ip(ip_str: str) -> bool:
    """Verifica se o IP é seguro para consultas externas (não privado/loopback)."""
    valid, _, is_public = validate_ip(ip_str)
    return valid and is_public
