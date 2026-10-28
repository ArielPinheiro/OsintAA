import re
from typing import Tuple

def clean_digits(value: str) -> str:
    """Remove caracteres não numéricos."""
    return re.sub(r"\D", "", value or "")

def validate_cnpj(cnpj: str) -> Tuple[bool, str]:
    """
    Valida número de CNPJ pelos dois dígitos verificadores (Módulo 11).
    Retorna (is_valid, clean_cnpj ou mensagem_erro).
    """
    clean = clean_digits(cnpj)
    if len(clean) != 14:
        return False, "CNPJ deve conter exatamente 14 dígitos numéricos."

    if clean == clean[0] * 14:
        return False, "CNPJ inválido (todos os dígitos são iguais)."

    # Primeiro dígito
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(int(clean[i]) * multiplicadores1[i] for i in range(12))
    resto1 = soma1 % 11
    d1 = 0 if resto1 < 2 else 11 - resto1

    if int(clean[12]) != d1:
        return False, "Dígito verificador 1 do CNPJ inválido."

    # Segundo dígito
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma2 = sum(int(clean[i]) * multiplicadores2[i] for i in range(13))
    resto2 = soma2 % 11
    d2 = 0 if resto2 < 2 else 11 - resto2

    if int(clean[13]) != d2:
        return False, "Dígito verificador 2 do CNPJ inválido."

    return True, clean

def format_cnpj(clean_cnpj: str) -> str:
    """Formata CNPJ no padrão 00.000.000/0001-00."""
    clean = clean_digits(clean_cnpj)
    if len(clean) != 14:
        return clean_cnpj
    return f"{clean[0:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:14]}"
