import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["name"] == "OSINT Brazuca Ultimate"
    assert data["adapters_count"] >= 10

def test_api_categories():
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.json()
    assert "core_categories" in data
    assert "future_modules" in data
    ids = [c["id"] for c in data["core_categories"]]
    assert "cnpj" in ids
    assert "cpf" in ids
    assert "dominio" in ids

def test_api_catalog():
    res = client.get("/api/catalog?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total_returned"] <= 10
    assert len(data["sources"]) > 0

def test_api_catalog_search():
    res = client.get("/api/catalog?q=registro")
    assert res.status_code == 200
    data = res.json()
    assert data["total_returned"] > 0

def test_api_query_validation_error():
    # Enviar CPF inválido
    payload = {"category": "cpf", "target": "123"}
    res = client.post("/api/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["failed"] == 1
    assert "CPF deve conter exatamente 11 dígitos" in data["results"][0]["error_message"]

def test_api_file_upload_analysis():
    # Enviar arquivo de teste multipart
    files = {"file": ("alvo_analise.txt", b"CONTEUDO FORENSE DE TESTE 2026", "text/plain")}
    res = client.post("/api/query/file", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "documentos"
    assert data["results"][0]["status"] == "confirmado"
    assert "sha256" in data["results"][0]["data"]["hashes"]

