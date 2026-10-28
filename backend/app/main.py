import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, File, Form, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from .config import settings
from .catalog.loader import catalog_loader
from .catalog.models import CatalogSource, CatalogStats
from .engine.models import QueryRequest, QueryResponse
from .engine.orchestrator import query_engine
from .reports.exporter import export_to_csv, export_to_html, export_to_json
from .history.storage import history_storage
from .validators.sanitization import sanitize_filename

# Configuração de Logs Segura (sem dados sensíveis)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("osint.app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}...")
    logger.info(f"Escutando em {settings.LISTEN_HOST}:{settings.LISTEN_PORT} (Local Only)")
    logger.info(f"Modo de Privacidade: Histórico {'ATIVADO' if settings.ENABLE_HISTORY else 'DESATIVADO (Padrão Seguro)'}")
    # Carregar catálogo na inicialização
    catalog_loader.load()
    yield
    logger.info("Encerrando OSINT Brazuca Ultimate...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

# CORS seguro restrito para desenvolvimento e consumo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "history_enabled": history_storage.is_enabled(),
        "host": settings.LISTEN_HOST,
        "adapters_count": len(query_engine.get_registered_adapters()),
        "catalog_sources_count": len(catalog_loader.get_all()),
    }

@app.get("/api/categories")
async def get_categories():
    """Retorna categorias principais e os módulos futuros preparados."""
    core = [
        {
            "id": "cnpj",
            "name": "CNPJ",
            "description": "Situação cadastral, razão social, CNAEs, quadro societário (QSA) e endereços.",
            "placeholder": "Ex: 00.000.000/0001-91",
            "implemented": True,
            "badge": "Automático + QSA"
        },
        {
            "id": "cpf",
            "name": "CPF",
            "description": "Validação algorítmica, região fiscal emissora e emissão guiada de certidões oficiais.",
            "placeholder": "Ex: 000.000.000-00",
            "implemented": True,
            "badge": "Oficial + Mascarado"
        },
        {
            "id": "dominio",
            "name": "Domínio e Site",
            "description": "RDAP oficial Registro.br/ICANN, registros DNS completos, CT crt.sh e sondagem HTTP.",
            "placeholder": "Ex: registro.br",
            "implemented": True,
            "badge": "RDAP + DNS + CT"
        },
        {
            "id": "ip",
            "name": "IP e Rede",
            "description": "RDAP de blocos IP, ASN detentor, DNS reverso e geolocalização de infraestrutura.",
            "placeholder": "Ex: 200.160.2.3",
            "implemented": True,
            "badge": "RDAP + BGP + Geo"
        },
        {
            "id": "telefone",
            "name": "Telefone",
            "description": "Normalização E.164, prefixo geográfico, identificação de operadora e portabilidade.",
            "placeholder": "Ex: (11) 98765-4321",
            "implemented": True,
            "badge": "E.164 + Anatel"
        },
        {
            "id": "email",
            "name": "E-mail",
            "description": "Validação de sintaxe, auditoria de servidores MX, políticas SPF/DMARC e descartáveis.",
            "placeholder": "Ex: contato@empresa.com.br",
            "implemented": True,
            "badge": "MX + SPF + DMARC"
        },
        {
            "id": "username",
            "name": "Username e Perfis",
            "description": "Pesquisa em APIs oficiais (GitHub, GitLab) e verificação em redes públicas.",
            "placeholder": "Ex: octocat",
            "implemented": True,
            "badge": "APIs Oficiais"
        },
        {
            "id": "documentos",
            "name": "Documentos e Arquivos",
            "description": "Cálculo local de SHA-256, MD5, SHA-1, metadados EXIF e checagem de integridade.",
            "placeholder": "Envie um arquivo ou digite um hash SHA-256",
            "implemented": True,
            "badge": "100% Local"
        },
        {
            "id": "dados_publicos",
            "name": "Dados Públicos Federais",
            "description": "Portal da Transparência, Compras.gov.br, Dados.gov.br e Diários Oficiais.",
            "placeholder": "Ex: Petrobras ou termo de pesquisa",
            "implemented": True,
            "badge": "Governo Federal"
        },
    ]

    future = [
        {"id": "marcas_patentes", "name": "Marcas e Patentes (INPI)", "description": "Titularidade publicada e marcas registradas na base do INPI."},
        {"id": "licitacoes_contratos", "name": "Licitações e Contratos", "description": "Cruzamento aprofundado com PNCP e empenhos governamentais."},
        {"id": "processos_certidoes", "name": "Processos Judiciais Públicos", "description": "Pesquisa unificada em tribunais via DataJud e PJe com respeito a segredo de justiça."},
        {"id": "vulnerabilidades_cves", "name": "Vulnerabilidades e CVEs", "description": "Consulta ao NVD (NIST) e MITRE para CVEs de tecnologias identificadas."},
        {"id": "repositorios_codigo", "name": "Repositórios de Código", "description": "Busca avançada de repositórios públicos e chaves expostas acidentalmente."},
        {"id": "blockchain", "name": "Blockchain e Criptoativos", "description": "Rastreamento de transações em ledgers públicos (Bitcoin, Ethereum)."},
        {"id": "analise_imagens", "name": "Análise Técnica de Imagens", "description": "Análise de ruído, ELA (Error Level Analysis) e metadados forenses."},
        {"id": "monitoramento_ativos", "name": "Monitoramento de Ativos", "description": "Acompanhamento contínuo de alterações em registros DNS e certificados."},
    ]

    return {"core_categories": core, "future_modules": future}

@app.get("/api/catalog")
async def get_catalog(
    q: Optional[str] = Query(None, description="Busca textual livre"),
    categoria_id: Optional[str] = Query(None, description="Filtrar por categoria_id"),
    input_type: Optional[str] = Query(None, description="Filtrar por tipo de dado de entrada"),
    tipo_fonte: Optional[str] = Query(None, description="Filtrar por tipo de fonte"),
    integration_type: Optional[str] = Query(None, description="Filtrar por status de integração"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    sources = catalog_loader.search(
        query=q,
        categoria_id=categoria_id,
        input_type=input_type,
        tipo_fonte=tipo_fonte,
        integration_type=integration_type,
        limit=limit,
        offset=offset,
    )
    return {
        "total_returned": len(sources),
        "limit": limit,
        "offset": offset,
        "sources": sources,
    }

@app.get("/api/catalog/stats", response_model=CatalogStats)
async def get_catalog_stats():
    return catalog_loader.get_stats()

@app.get("/api/catalog/categories")
async def get_catalog_categories():
    return catalog_loader.get_categories()

@app.get("/api/adapters")
async def get_adapters():
    """Lista todos os adaptadores automatizados registrados."""
    adapters = query_engine.get_registered_adapters()
    return [
        {
            "adapter_id": a.adapter_id,
            "name": a.name,
            "category": a.category,
            "description": a.description,
            "official_url": a.official_url,
            "supported_inputs": a.supported_inputs,
            "requires_captcha": a.requires_captcha,
            "requires_auth": a.requires_auth,
        }
        for a in adapters.values()
    ]

@app.post("/api/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """Executa consultas automatizadas no motor central."""
    response = await query_engine.execute_query(request)
    
    # Salvar no histórico SOMENTE se ativado
    if request.save_history or history_storage.is_enabled():
        history_storage.save(response)

    return response

@app.post("/api/query/file", response_model=QueryResponse)
async def run_file_query(file: UploadFile = File(...)):
    """Recebe um arquivo enviado pelo usuário e realiza análise de integridade e hashes localmente."""
    clean_name = sanitize_filename(file.filename or "upload.bin")
    contents = await file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite máximo permitido ({settings.MAX_UPLOAD_SIZE_MB}MB)."
        )

    req = QueryRequest(
        category="documentos",
        target=clean_name,
        source_ids=["document_analyzer"]
    )

    context = {
        "file_bytes": contents,
        "filename": clean_name,
    }

    response = await query_engine.execute_query(req, context=context)
    return response

@app.post("/api/report/export")
async def export_report(
    response: QueryResponse,
    format: str = Query("json", pattern="^(json|csv|html)$")
):
    """Gera o dossiê pericial exportado no formato solicitado."""
    if format == "json":
        return Response(
            content=export_to_json(response),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=dossie_{response.query_id[:8]}.json"}
        )
    elif format == "csv":
        return Response(
            content=export_to_csv(response),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=dossie_{response.query_id[:8]}.csv"}
        )
    elif format == "html":
        return HTMLResponse(
            content=export_to_html(response),
            headers={"Content-Disposition": f"attachment; filename=dossie_{response.query_id[:8]}.html"}
        )

@app.get("/api/history")
async def get_history(limit: int = 50):
    return {
        "enabled": history_storage.is_enabled(),
        "history": history_storage.get_all(limit=limit),
    }

@app.post("/api/history/toggle")
async def toggle_history(enabled: bool = Form(...)):
    history_storage.set_enabled(enabled)
    return {"enabled": history_storage.is_enabled()}

@app.delete("/api/history")
async def clear_history():
    history_storage.clear()
    return {"message": "Histórico limpo com sucesso."}

# Servir Frontend React compilado (SPA)
from fastapi.staticfiles import StaticFiles
FRONTEND_DIST = settings.BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

