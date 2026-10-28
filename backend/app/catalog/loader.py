import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from ..config import settings
from .models import CatalogSource, SourceLink, IntegrationType, CatalogStats

logger = logging.getLogger("osint.catalog")

# Mapeamento de fontes do catálogo para adaptadores implementados
KNOWN_ADAPTERS: Dict[str, str] = {
    "apis-publicas-brasileiras/receitaws-api-cnpj": "receitaws_cnpj",
    "apis-publicas-brasileiras/registro-br-api-rdap": "rdap_domain",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/minha-receita-api-publica-de-cnpj": "brasilapi_cnpj",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/consulta-situacao-cadastral-cpf": "cpf_official",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/receita-federal-certidao-de-regularidade-fiscal": "cpf_official",
    "transparencia-publica-e-defesa-do-consumidor/dados-gov-br-portal-brasileiro-de-dados-abertos": "dados_gov",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/ceis-cadastro-de-empresas-inidoneas-e-suspensas": "transparencia_gov",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/cnep-cadastro-nacional-de-empresas-punidas": "transparencia_gov",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/cepim-cadastro-de-entidades-privadas-sem-fins-lucrativos-impedidas": "transparencia_gov",
    "busca-de-informacoes-via-cpf-cnpj-crm-cna/tst-certidao-negativa-de-debitos-trabalhistas-cndt": "cpf_official",
}

class CatalogLoader:
    def __init__(self):
        self._sources: List[CatalogSource] = []
        self._sources_by_id: Dict[str, CatalogSource] = {}
        self._categories: Dict[str, str] = {}
        self._taxonomy: dict = {}
        self._loaded: bool = False

    def load(self) -> bool:
        """Carrega fontes do sources.json e taxonomia do taxonomy.json."""
        sources_path = settings.get_catalog_file("sources.json")
        taxonomy_path = settings.get_catalog_file("taxonomy.json")

        if not sources_path.exists():
            logger.warning(f"sources.json não encontrado em {sources_path}")
            return False

        try:
            with open(sources_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            raw_sources = data.get("sources", [])
            self._sources = []
            self._sources_by_id = {}
            self._categories = {}

            for s in raw_sources:
                sid = s.get("id", "")
                cat_id = s.get("categoria_id", "outros")
                cat_name = s.get("categoria", "Outros")
                self._categories[cat_id] = cat_name

                # Links
                links = [
                    SourceLink(
                        label=l.get("label", ""),
                        url=l.get("url", ""),
                        uf=l.get("uf")
                    )
                    for l in s.get("links", [])
                    if l.get("url")
                ]

                # Determinar status de integração
                integ_type = IntegrationType.NOT_IMPLEMENTED
                adapter_id = KNOWN_ADAPTERS.get(sid)
                requires_auth = False
                requires_captcha = False
                manual_notice = None

                url_str = (links[0].url if links else "").lower()
                desc_str = s.get("descricao", "").lower()
                nome_str = s.get("nome", "").lower()

                if adapter_id:
                    integ_type = IntegrationType.IMPLEMENTED
                elif "gov.br" in url_str and ("acesso" in url_str or "login" in url_str or "meu" in url_str):
                    integ_type = IntegrationType.AUTH_REQUIRED
                    requires_auth = True
                    manual_notice = "Exige autenticação unificada Gov.br (prata/ouro) para acesso aos dados do cidadão."
                elif any(w in desc_str or w in nome_str for w in ["captcha", "certidão", "antecedentes", "sinesp"]):
                    integ_type = IntegrationType.CAPTCHA_REQUIRED
                    requires_captcha = True
                    manual_notice = "Exige resolução manual de desafio CAPTCHA pelo usuário no portal oficial."
                elif s.get("tipo_fonte") == "api" or "api" in nome_str:
                    integ_type = IntegrationType.API_AUTOMATED
                elif s.get("tipo_fonte") == "dork":
                    integ_type = IntegrationType.PUBLIC_HTTP
                elif any(w in desc_str or w in nome_str for w in ["portal", "consulta", "busca"]):
                    integ_type = IntegrationType.MANUAL_ONLY
                    manual_notice = "Consulta manual via navegador no portal oficial."
                else:
                    integ_type = IntegrationType.NOT_IMPLEMENTED

                source = CatalogSource(
                    id=sid,
                    nome=s.get("nome", ""),
                    categoria=cat_name,
                    categoria_id=cat_id,
                    descricao=s.get("descricao", ""),
                    tipo_fonte=s.get("tipo_fonte", "indefinido"),
                    classificacao=s.get("classificacao", "heuristica"),
                    input=s.get("input", []),
                    output=s.get("output", []),
                    links=links,
                    integration_type=integ_type,
                    adapter_id=adapter_id,
                    manual_notice=manual_notice,
                    requires_auth=requires_auth,
                    requires_captcha=requires_captcha
                )
                self._sources.append(source)
                self._sources_by_id[sid] = source

            # Carregar taxonomia se disponível
            if taxonomy_path.exists():
                try:
                    with open(taxonomy_path, "r", encoding="utf-8") as f:
                        self._taxonomy = json.load(f)
                except Exception as ex:
                    logger.warning(f"Erro ao carregar taxonomia: {ex}")

            self._loaded = True
            logger.info(f"Catálogo carregado com {len(self._sources)} fontes e {len(self._categories)} categorias.")
            return True

        except Exception as e:
            logger.error(f"Falha ao carregar catálogo: {e}", exc_info=True)
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def get_all(self) -> List[CatalogSource]:
        if not self._loaded:
            self.load()
        return self._sources

    def get_by_id(self, source_id: str) -> Optional[CatalogSource]:
        if not self._loaded:
            self.load()
        return self._sources_by_id.get(source_id)

    def get_categories(self) -> Dict[str, str]:
        if not self._loaded:
            self.load()
        return self._categories

    def search(
        self,
        query: Optional[str] = None,
        categoria_id: Optional[str] = None,
        input_type: Optional[str] = None,
        tipo_fonte: Optional[str] = None,
        integration_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CatalogSource]:
        """Filtra fontes do catálogo por múltiplos critérios."""
        if not self._loaded:
            self.load()

        results = self._sources
        q = (query or "").strip().lower()

        if q:
            results = [
                s for s in results
                if q in s.nome.lower()
                or q in s.descricao.lower()
                or q in s.id.lower()
                or any(q in l.url.lower() for l in s.links)
            ]

        if categoria_id and categoria_id != "all":
            results = [s for s in results if s.categoria_id == categoria_id]

        if input_type and input_type != "all":
            results = [s for s in results if input_type in s.input]

        if tipo_fonte and tipo_fonte != "all":
            results = [s for s in results if s.tipo_fonte == tipo_fonte]

        if integration_type and integration_type != "all":
            results = [s for s in results if s.integration_type.value == integration_type]

        return results[offset : offset + limit]

    def get_sources_for_input(self, input_type: str) -> List[CatalogSource]:
        """Retorna todas as fontes compatíveis com um dado input (ex: cnpj, cpf, ip, dominio)."""
        if not self._loaded:
            self.load()
        return [s for s in self._sources if input_type in s.input]

    def get_stats(self) -> CatalogStats:
        if not self._loaded:
            self.load()
        total_links = sum(len(s.links) for s in self._sources)
        implemented = sum(1 for s in self._sources if s.integration_type == IntegrationType.IMPLEMENTED)
        
        inputs = set()
        outputs = set()
        for s in self._sources:
            for i in s.input: inputs.add(i)
            for o in s.output: outputs.add(o)

        return CatalogStats(
            total_sources=len(self._sources),
            total_links=total_links,
            categories_count=len(self._categories),
            implemented_adapters_count=implemented,
            inputs_supported=sorted(list(inputs)),
            outputs_supported=sorted(list(outputs))
        )

# Instância global
catalog_loader = CatalogLoader()
