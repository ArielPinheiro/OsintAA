import pytest
from backend.app.catalog.loader import catalog_loader
from backend.app.catalog.models import IntegrationType

def test_catalog_load_success():
    loaded = catalog_loader.load()
    assert loaded is True
    assert catalog_loader.is_loaded is True

def test_catalog_counts():
    sources = catalog_loader.get_all()
    assert len(sources) >= 500  # Existem 515 fontes no sources.json
    stats = catalog_loader.get_stats()
    assert stats.total_sources >= 500
    assert stats.total_links >= 1000
    assert stats.categories_count >= 30

def test_catalog_search():
    results = catalog_loader.search(query="receita federal")
    assert len(results) > 0
    assert any("receita" in s.nome.lower() or "receita" in s.descricao.lower() for s in results)

def test_catalog_filter_by_input():
    cnpj_sources = catalog_loader.get_sources_for_input("cnpj")
    assert len(cnpj_sources) > 0
    for s in cnpj_sources:
        assert "cnpj" in s.input

def test_catalog_integration_classification():
    # Verifica que fontes possuem tipos de integração válidos atribuídos
    sources = catalog_loader.get_all()
    types_found = {s.integration_type for s in sources}
    assert IntegrationType.NOT_IMPLEMENTED in types_found
    assert IntegrationType.PUBLIC_HTTP in types_found

