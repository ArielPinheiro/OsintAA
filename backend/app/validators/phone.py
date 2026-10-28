import re
from typing import Tuple, Optional, Dict

VALID_DDDS: Dict[int, str] = {
    11: "São Paulo (Capital/Metropolitana)",
    12: "São José dos Campos / Vale do Paraíba - SP",
    13: "Santos / Baixada Santista - SP",
    14: "Bauru / Marília - SP",
    15: "Sorocaba / Itapetininga - SP",
    16: "Ribeirão Preto / Franca - SP",
    17: "São José do Rio Preto - SP",
    18: "Presidente Prudente / Araçatuba - SP",
    19: "Campinas / Piracicaba - SP",
    21: "Rio de Janeiro (Capital/Metropolitana)",
    22: "Campos dos Goytacazes / Região dos Lagos - RJ",
    24: "Volta Redonda / Petrópolis - RJ",
    27: "Vitória / Região Metropolitana - ES",
    28: "Cachoeiro de Itapemirim - ES",
    31: "Belo Horizonte / Metropolitana - MG",
    32: "Juiz de Fora - MG",
    33: "Governador Valadares - MG",
    34: "Uberlândia / Triângulo Mineiro - MG",
    35: "Poços de Caldas / Pouso Alegre - MG",
    37: "Divinópolis - MG",
    38: "Montes Claros - MG",
    41: "Curitiba / Metropolitana - PR",
    42: "Ponta Grossa / Guarapuava - PR",
    43: "Londrina / Apucarana - PR",
    44: "Maringá / Campo Mourão - PR",
    45: "Cascavel / Foz do Iguaçu - PR",
    46: "Francisco Beltrão / Pato Branco - PR",
    47: "Joinville / Blumenau - SC",
    48: "Florianópolis / Criciúma - SC",
    49: "Chapecó / Lages - SC",
    51: "Porto Alegre / Metropolitana - RS",
    53: "Pelotas / Rio Grande - RS",
    54: "Caxias do Sul / Passo Fundo - RS",
    55: "Santa Maria / Uruguaiana - RS",
    61: "Brasília / Distrito Federal",
    62: "Goiânia / Metropolitana - GO",
    63: "Palmas / Tocantins",
    64: "Rio Verde / Itumbiara - GO",
    65: "Cuiabá / Metropolitana - MT",
    66: "Rondonópolis / Sinop - MT",
    67: "Campo Grande / Mato Grosso do Sul",
    68: "Rio Branco / Acre",
    69: "Porto Velho / Rondônia",
    71: "Salvador / Metropolitana - BA",
    73: "Ilhéus / Itabuna - BA",
    74: "Juazeiro - BA",
    75: "Feira de Santana - BA",
    77: "Vitória da Conquista / Barreiras - BA",
    79: "Aracaju / Sergipe",
    81: "Recife / Metropolitana - PE",
    82: "Maceió / Alagoas",
    83: "João Pessoa / Campina Grande - PB",
    84: "Natal / Rio Grande do Norte",
    85: "Fortaleza / Metropolitana - CE",
    86: "Teresina / Piauí",
    87: "Petrolina / Caruaru - PE",
    88: "Juazeiro do Norte / Sobral - CE",
    89: "Picos / Floriano - PI",
    91: "Belém / Metropolitana - PA",
    92: "Manaus / Metropolitana - AM",
    93: "Santarém - PA",
    94: "Marabá - PA",
    95: "Boa Vista / Roraima",
    96: "Macapá / Amapá",
    97: "Interior do Amazonas",
    98: "São Luís / Metropolitana - MA",
    99: "Imperatriz - MA",
}

def clean_digits(val: str) -> str:
    return re.sub(r"\D", "", val or "")

def validate_brazilian_phone(phone_str: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Valida e normaliza número de telefone brasileiro no padrão E.164.
    Retorna (is_valid, normalized_ou_erro, metadata_dict).
    """
    digits = clean_digits(phone_str)

    # Remove DDI 55 se fornecido
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]

    # Remove 0 inicial de DDD se digitado ex: 011...
    if digits.startswith("0") and len(digits) in (11, 12):
        digits = digits[1:]

    if len(digits) not in (10, 11):
        return False, f"Número deve conter 10 ou 11 dígitos com DDD (encontrado: {len(digits)} dígitos).", None

    ddd = int(digits[:2])
    if ddd not in VALID_DDDS:
        return False, f"DDD {ddd} não é um código de área brasileiro válido.", None

    number_body = digits[2:]
    is_mobile = len(number_body) == 9
    
    if is_mobile:
        if not number_body.startswith("9"):
            return False, "Celular com 9 dígitos deve iniciar com '9'.", None
        tipo = "Celular (Móvel)"
        formatted = f"+55 ({ddd}) {number_body[:5]}-{number_body[5:]}"
    else:
        if number_body.startswith("9"):
            return False, "Número fixo de 8 dígitos não pode iniciar com '9'.", None
        tipo = "Fixo (Fixo Comutado)"
        formatted = f"+55 ({ddd}) {number_body[:4]}-{number_body[4:]}"

    meta = {
        "e164": f"+55{digits}",
        "raw_national": digits,
        "ddd": ddd,
        "regiao": VALID_DDDS[ddd],
        "tipo": tipo,
        "is_mobile": is_mobile,
        "formatted": formatted,
    }

    return True, formatted, meta

def mask_phone(phone_formatted: str) -> str:
    """Mascara o telefone protegendo dígitos intermediários: +55 (11) 9****-1234."""
    digits = clean_digits(phone_formatted)
    if len(digits) == 13 and digits.startswith("55"):
        # +55 (11) 98765-4321 -> +55 (11) 9****-4321
        return f"+55 ({digits[2:4]}) {digits[4]}****-{digits[9:]}"
    elif len(digits) == 11:
        return f"({digits[0:2]}) {digits[2]}****-{digits[7:]}"
    return phone_formatted
