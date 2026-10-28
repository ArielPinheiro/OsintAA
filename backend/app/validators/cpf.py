import re
from typing import Tuple

def clean_digits(value: str) -> str:
    """Remove todos os caracteres não numéricos."""
    return re.sub(r"\D", "", value or "")

def validate_cpf(cpf: str) -> Tuple[bool, str]:
    """
    Valida número de CPF pelo algoritmo dos dígitos verificadores (Módulo 11).
    Retorna (is_valid, clean_cpf ou mensagem_erro).
    """
    clean = clean_digits(cpf)
    if len(clean) != 11:
        return False, "CPF deve conter exatamente 11 dígitos numéricos."

    # Bloqueia números com todos os dígitos iguais (ex: 111.111.111-11)
    if clean == clean[0] * 11:
        return False, "CPF inválido (todos os dígitos são iguais)."

    # Primeiro dígito verificador
    soma = sum(int(clean[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    d1 = 0 if resto == 10 else resto

    if int(clean[9]) != d1:
        return False, "Dígito verificador 1 do CPF inválido."

    # Segundo dígito verificador
    soma = sum(int(clean[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    d2 = 0 if resto == 10 else resto

    if int(clean[10]) != d2:
        return False, "Dígito verificador 2 do CPF inválido."

    return True, clean

def format_cpf(clean_cpf: str) -> str:
    """Formata CPF no padrão 000.000.000-00."""
    clean = clean_digits(clean_cpf)
    if len(clean) != 11:
        return clean_cpf
    return f"{clean[0:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:11]}"

def mask_cpf(cpf: str) -> str:
    """
    Mascara CPF preservando apenas os dígitos intermediários ou de controle conforme padrão LGPD.
    Ex: ***.456.789-** ou 123.***.***-00. Padrão escolhido: ***.XXX.XXX-**
    """
    clean = clean_digits(cpf)
    if len(clean) != 11:
        return "***.***.***-**"
    return f"***.{clean[3:6]}.{clean[6:9]}-**"
