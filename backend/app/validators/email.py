import re
from typing import Tuple, Optional

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Amostra de provedores de e-mail descartável conhecidos
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "sharklasers.com", "throwawaymail.com", "yopmail.com", "trashmail.com",
    "dispostable.com", "getairmail.com", "mohmal.com", "temp-mail.org",
    "crazymailing.com", "fakeinbox.com", "fakemailgenerator.com"
}

def validate_email(email_str: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Valida sintaxe de endereço de e-mail.
    Retorna (is_valid, email_normalizado_ou_erro, metadados).
    """
    cleaned = (email_str or "").strip().lower()
    if not cleaned:
        return False, "E-mail não pode ser vazio.", None

    if len(cleaned) > 254:
        return False, "E-mail excede tamanho máximo de 254 caracteres.", None

    if not EMAIL_REGEX.match(cleaned):
        return False, "Formato de e-mail inválido.", None

    user_part, domain_part = cleaned.split("@", 1)
    is_disposable = domain_part in DISPOSABLE_DOMAINS

    meta = {
        "user": user_part,
        "domain": domain_part,
        "is_disposable": is_disposable,
    }

    return True, cleaned, meta

def mask_email(email: str) -> str:
    """Mascara e-mail para exibição segura: j****n@d****n.com."""
    if "@" not in email:
        return email
    user, domain = email.split("@", 1)
    
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = user[0] + "*" * (len(user) - 2) + user[-1]

    if "." in domain:
        domain_name, tld = domain.split(".", 1)
        if len(domain_name) <= 2:
            masked_domain = domain_name[0] + "*" + "." + tld
        else:
            masked_domain = domain_name[0] + "*" * (len(domain_name) - 2) + domain_name[-1] + "." + tld
    else:
        masked_domain = domain

    return f"{masked_user}@{masked_domain}"
