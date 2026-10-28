import pytest
from backend.app.validators.cpf import validate_cpf, mask_cpf, format_cpf
from backend.app.validators.cnpj import validate_cnpj, format_cnpj
from backend.app.validators.domain import validate_domain, clean_domain
from backend.app.validators.ip import validate_ip, is_safe_public_ip
from backend.app.validators.phone import validate_brazilian_phone, mask_phone
from backend.app.validators.email import validate_email, mask_email
from backend.app.validators.sanitization import is_safe_url, sanitize_filename

# --- Testes de CPF ---
def test_cpf_valid():
    # CPFs matematicamente válidos (dígitos verificadores corretos)
    valid_cpfs = [
        "52998224725",
        "11144477735",
        "00000000191",
    ]
    for cpf in valid_cpfs:
        ok, res = validate_cpf(cpf)
        assert ok is True
        assert len(res) == 11

def test_cpf_invalid_repeated_digits():
    ok, err = validate_cpf("11111111111")
    assert ok is False
    assert "iguais" in err

def test_cpf_invalid_check_digit():
    ok, err = validate_cpf("52998224726") # último dígito errado
    assert ok is False
    assert "Dígito verificador" in err

def test_cpf_masking():
    masked = mask_cpf("52998224725")
    assert masked == "***.982.247-**"
    assert "529" not in masked
    assert "25" not in masked

# --- Testes de CNPJ ---
def test_cnpj_valid():
    # CNPJ válido de teste (Petrobras e Banco do Brasil)
    valid_cnpjs = [
        "33.000.167/0001-01",
        "00000000000191",
    ]
    for cnpj in valid_cnpjs:
        ok, clean = validate_cnpj(cnpj)
        assert ok is True
        assert len(clean) == 14

def test_cnpj_invalid_check_digit():
    ok, err = validate_cnpj("33000167000109")
    assert ok is False
    assert "Dígito verificador" in err

def test_cnpj_format():
    fmt = format_cnpj("33000167000101")
    assert fmt == "33.000.167/0001-01"

# --- Testes de Domínio ---
def test_domain_valid():
    ok, d = validate_domain("https://www.registro.br/sub/path?q=1")
    assert ok is True
    assert d == "www.registro.br"

    ok2, d2 = validate_domain("globo.com")
    assert ok2 is True
    assert d2 == "globo.com"

def test_domain_invalid_or_internal():
    ok, err = validate_domain("localhost")
    assert ok is False

    ok2, err2 = validate_domain("server.internal")
    assert ok2 is False

# --- Testes de IP e Prevenção de SSRF ---
def test_ip_validation():
    ok, ip_str, is_pub = validate_ip("8.8.8.8")
    assert ok is True
    assert is_pub is True

    # Loopback
    ok2, ip_str2, is_pub2 = validate_ip("127.0.0.1")
    assert ok2 is True
    assert is_pub2 is False

    # Rede privada RFC1918
    ok3, ip_str3, is_pub3 = validate_ip("192.168.1.1")
    assert ok3 is True
    assert is_pub3 is False

def test_ssrf_url_protection():
    assert is_safe_url("http://127.0.0.1:8000") is False
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    assert is_safe_url("http://10.0.0.5") is False
    assert is_safe_url("http://localhost:3000") is False
    assert is_safe_url("https://registro.br") is True
    assert is_safe_url("https://brasilapi.com.br") is True

# --- Testes de Telefone ---
def test_phone_valid_mobile():
    ok, fmt, meta = validate_brazilian_phone("11987654321")
    assert ok is True
    assert fmt == "+55 (11) 98765-4321"
    assert meta["is_mobile"] is True
    assert "São Paulo" in meta["regiao"]

def test_phone_valid_landline():
    ok, fmt, meta = validate_brazilian_phone("2123456789")
    assert ok is True
    assert fmt == "+55 (21) 2345-6789"
    assert meta["is_mobile"] is False

def test_phone_masking():
    masked = mask_phone("+55 (11) 98765-4321")
    assert masked == "+55 (11) 9****-4321"

def test_phone_invalid_ddd():
    ok, err, _ = validate_brazilian_phone("05999999999")
    assert ok is False

# --- Testes de E-mail ---
def test_email_valid():
    ok, clean, meta = validate_email("investigador@osintbrazuca.com.br")
    assert ok is True
    assert meta["domain"] == "osintbrazuca.com.br"
    assert meta["is_disposable"] is False

def test_email_disposable_detection():
    ok, clean, meta = validate_email("teste@mailinator.com")
    assert ok is True
    assert meta["is_disposable"] is True

def test_email_masking():
    masked = mask_email("rodrigo@exemplo.com.br")
    assert masked.startswith("r")
    assert masked.endswith("@e*****o.com.br")

# --- Testes de Sanitização de Arquivos ---
def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\boot.ini") == "boot.ini"
    assert sanitize_filename("relatorio final 2026.pdf") == "relatorio_final_2026.pdf"

