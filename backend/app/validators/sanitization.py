import ipaddress
import os
import re
from pathlib import Path
from urllib.parse import urlparse

# IPs e faixas bloqueadas para evitar SSRF (Server-Side Request Forgery)
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # Privada Classe A
    ipaddress.ip_network("172.16.0.0/12"),     # Privada Classe B
    ipaddress.ip_network("192.168.0.0/16"),    # Privada Classe C
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / AWS Metadata
    ipaddress.ip_network("100.64.0.0/10"),     # CGNAT
    ipaddress.ip_network("fc00::/7"),          # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),         # IPv6 Link-local
    ipaddress.ip_network("::1/128"),           # IPv6 Loopback
]

def is_safe_url(url_str: str) -> bool:
    """Verifica se a URL é segura para chamadas HTTP de saída (prevenção SSRF)."""
    try:
        parsed = urlparse(url_str)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        if hostname.lower() in ("localhost", "local", "internal", "intranet"):
            return False

        # Tentar avaliar se hostname é IP
        try:
            ip = ipaddress.ip_address(hostname)
            for net in BLOCKED_NETWORKS:
                if ip in net:
                    return False
        except ValueError:
            # É nome de domínio, OK
            pass

        return True
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """Higieniza nome de arquivo para evitar path traversal."""
    clean = os.path.basename(filename)
    clean = re.sub(r"[^\w.\-_]", "_", clean)
    return clean[:100]
