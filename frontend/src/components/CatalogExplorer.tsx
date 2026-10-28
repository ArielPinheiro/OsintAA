import React, { useEffect, useState } from 'react';
import {
  Search,
  ExternalLink,
  Lock,
  AlertTriangle,
  Zap,
  RefreshCw,
} from 'lucide-react';
import type { CatalogSource, CatalogStats } from '../types';
import { fetchCatalog, fetchCatalogStats } from '../services/api';

export const CatalogExplorer: React.FC = () => {
  const [sources, setSources] = useState<CatalogSource[]>([]);
  const [stats, setStats] = useState<CatalogStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedInput, setSelectedInput] = useState('all');
  const [selectedIntegType, setSelectedIntegType] = useState('all');
  const [selectedTipoFonte, setSelectedTipoFonte] = useState('all');

  const loadData = async () => {
    setLoading(true);
    try {
      const [catRes, statsRes] = await Promise.all([
        fetchCatalog({
          q: searchTerm || undefined,
          categoria_id: selectedCategory !== 'all' ? selectedCategory : undefined,
          input_type: selectedInput !== 'all' ? selectedInput : undefined,
          tipo_fonte: selectedTipoFonte !== 'all' ? selectedTipoFonte : undefined,
          integration_type: selectedIntegType !== 'all' ? selectedIntegType : undefined,
          limit: 150,
        }),
        fetchCatalogStats(),
      ]);
      setSources(catRes.sources);
      setStats(statsRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchTerm, selectedCategory, selectedInput, selectedIntegType, selectedTipoFonte]);

  const getIntegrationBadge = (source: CatalogSource) => {
    switch (source.integration_type) {
      case 'integrado_funcional':
        return (
          <span className="badge badge-confirmed" title="Adaptador automatizado implementado no sistema">
            <Zap size={11} /> INTEGRADO FUNCIONAL
          </span>
        );
      case 'api_automatizavel':
        return (
          <span className="badge badge-manual" title="API pública identificada no catálogo">
            <Zap size={11} /> API AUTOMATIZÁVEL
          </span>
        );
      case 'consulta_http_publica':
        return (
          <span className="badge badge-partial" title="Consulta HTTP pública permitida">
            HTTP PÚBLICO
          </span>
        );
      case 'consulta_manual':
        return (
          <span className="badge badge-manual" title="Consulta manual requerida via navegador">
            CONSULTA MANUAL
          </span>
        );
      case 'autenticacao_obrigatoria':
        return (
          <span className="badge badge-crimson" title="Exige login Gov.br ou credencial do usuário">
            <Lock size={11} /> AUTENTICAÇÃO OBRIGATÓRIA
          </span>
        );
      case 'captcha_necessario':
        return (
          <span className="badge badge-partial" title="Exige resolução humana de CAPTCHA">
            <AlertTriangle size={11} /> CAPTCHA EXIGIDO
          </span>
        );
      default:
        return (
          <span className="badge" style={{ backgroundColor: '#1a1f2c', color: '#6e7687' }}>
            NÃO IMPLEMENTADO
          </span>
        );
    }
  };

  return (
    <div style={styles.container}>
      {/* Top Banner / Stats */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>Catálogo de Fontes Abertas Brasileiras</h2>
          <p style={styles.sub}>
            Metadados canônicos extraídos do dataset OSINT Brazuca com classificação de automação e limitações.
          </p>
        </div>

        {stats && (
          <div style={styles.statsBanner}>
            <div style={styles.statBox}>
              <span style={styles.statNum}>{stats.total_sources}</span>
              <span style={styles.statLbl}>Fontes Totais</span>
            </div>
            <div style={styles.statBox}>
              <span style={styles.statNum}>{stats.total_links}</span>
              <span style={styles.statLbl}>Links Oficiais</span>
            </div>
            <div style={styles.statBox}>
              <span style={styles.statNum}>{stats.categories_count}</span>
              <span style={styles.statLbl}>Categorias</span>
            </div>
            <div style={{ ...styles.statBox, borderColor: '#00ff66' }}>
              <span style={{ ...styles.statNum, color: '#00ff66' }}>
                {sources.filter((s) => s.integration_type === 'integrado_funcional').length}
              </span>
              <span style={styles.statLbl}>Conectores Ativos</span>
            </div>
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div style={styles.filterCard}>
        <div style={styles.searchRow}>
          <div style={styles.searchWrap}>
            <Search size={16} color="#8b92a2" />
            <input
              type="text"
              style={styles.searchInput}
              placeholder="Buscar por nome, descrição, órgão ou URL oficial..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <button style={styles.refreshBtn} onClick={loadData} title="Atualizar">
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
          </button>
        </div>

        <div style={styles.filtersRow}>
          <div style={styles.filterGroup}>
            <label style={styles.filterLabel}>Categoria do Catálogo:</label>
            <select
              style={styles.selectInput}
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="all">Todas as categorias</option>
              {Array.from(new Set(sources.map((s) => s.categoria_id))).map((cid) => {
                const s = sources.find((src) => src.categoria_id === cid);
                return (
                  <option key={cid} value={cid}>
                    {s?.categoria || cid}
                  </option>
                );
              })}
            </select>
          </div>

          <div style={styles.filterGroup}>
            <label style={styles.filterLabel}>Tipo de Entrada (Input):</label>
            <select
              style={styles.selectInput}
              value={selectedInput}
              onChange={(e) => setSelectedInput(e.target.value)}
            >
              <option value="all">Todos os identificadores</option>
              {stats?.inputs_supported.map((inp) => (
                <option key={inp} value={inp}>
                  {inp.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.filterGroup}>
            <label style={styles.filterLabel}>Status de Integração:</label>
            <select
              style={styles.selectInput}
              value={selectedIntegType}
              onChange={(e) => setSelectedIntegType(e.target.value)}
            >
              <option value="all">Todas as classificações</option>
              <option value="integrado_funcional">Integrado Funcional (Ativo)</option>
              <option value="api_automatizavel">API Automatizável</option>
              <option value="consulta_http_publica">Consulta HTTP Pública</option>
              <option value="consulta_manual">Consulta Manual</option>
              <option value="autenticacao_obrigatoria">Autenticação Obrigatória</option>
              <option value="captcha_necessario">CAPTCHA Exigido</option>
              <option value="integracao_nao_implementada">Não Implementado</option>
            </select>
          </div>

          <div style={styles.filterGroup}>
            <label style={styles.filterLabel}>Esfera Institucional:</label>
            <select
              style={styles.selectInput}
              value={selectedTipoFonte}
              onChange={(e) => setSelectedTipoFonte(e.target.value)}
            >
              <option value="all">Todas as esferas</option>
              <option value="federal">Federal</option>
              <option value="estadual">Estadual</option>
              <option value="municipal">Municipal</option>
              <option value="judiciario">Judiciário</option>
              <option value="ministerio_publico">Ministério Público</option>
              <option value="legislativo">Legislativo</option>
              <option value="privado">Privado</option>
              <option value="dork">Dork de Busca</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sources Grid / List */}
      <div style={styles.sourcesList}>
        <div style={styles.resultsCountBar}>
          <span>Exibindo <strong>{sources.length}</strong> fontes correspondentes</span>
        </div>

        {sources.map((s) => (
          <div key={s.id} style={styles.sourceCard}>
            <div style={styles.sourceTop}>
              <div>
                <div style={styles.titleLine}>
                  <h3 style={styles.sourceName}>{s.nome}</h3>
                  {getIntegrationBadge(s)}
                </div>
                <span style={styles.sourceCategory}>
                  {s.categoria} • Esfera: {s.tipo_fonte.toUpperCase()} • ID: {s.id}
                </span>
              </div>
            </div>

            {s.descricao && <p style={styles.sourceDesc}>{s.descricao}</p>}

            {s.manual_notice && (
              <div style={styles.manualNoticeBox}>
                <AlertTriangle size={13} color="#ffaa00" />
                <span>{s.manual_notice}</span>
              </div>
            )}

            {/* Inputs & Outputs Tags */}
            <div style={styles.tagsRow}>
              <div style={styles.tagGroup}>
                <span style={styles.tagLabel}>Entrada aceita:</span>
                {s.input.map((inp, idx) => (
                  <span key={idx} style={styles.inputTag}>{inp}</span>
                ))}
              </div>

              <div style={styles.tagGroup}>
                <span style={styles.tagLabel}>Retorna:</span>
                {s.output.map((out, idx) => (
                  <span key={idx} style={styles.outputTag}>{out}</span>
                ))}
              </div>
            </div>

            {/* Direct Links */}
            {s.links.length > 0 && (
              <div style={styles.linksArea}>
                <span style={styles.linkHeaderLabel}>Portais Oficiais:</span>
                <div style={styles.linksGrid}>
                  {s.links.map((link, idx) => (
                    <a
                      key={idx}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.officialLink}
                    >
                      <ExternalLink size={12} />
                      <span>{link.label || link.url.replace(/^https?:\/\//, '').split('/')[0]}</span>
                      {link.uf && <span style={styles.ufBadge}>{link.uf}</span>}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {sources.length === 0 && !loading && (
          <div style={styles.noResults}>
            Nenhuma fonte encontrada com os filtros selecionados.
          </div>
        )}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px 30px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '20px',
    flexWrap: 'wrap',
    gap: '16px',
  },
  title: {
    fontSize: '22px',
    fontWeight: 800,
    color: '#ffffff',
  },
  sub: {
    fontSize: '13px',
    color: '#8b92a2',
    marginTop: '4px',
  },
  statsBanner: {
    display: 'flex',
    gap: '10px',
  },
  statBox: {
    backgroundColor: '#0c0e14',
    border: '1px solid #1c2230',
    padding: '8px 14px',
    borderRadius: '6px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  statNum: {
    fontSize: '16px',
    fontWeight: 800,
    color: '#ffffff',
    fontFamily: 'monospace',
  },
  statLbl: {
    fontSize: '10px',
    color: '#6e7687',
    textTransform: 'uppercase',
  },
  filterCard: {
    backgroundColor: '#0d1017',
    border: '1px solid #280d11',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  searchRow: {
    display: 'flex',
    gap: '10px',
  },
  searchWrap: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: '#07080b',
    border: '1px solid #1c2230',
    borderRadius: '6px',
    padding: '0 12px',
  },
  searchInput: {
    flex: 1,
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#ffffff',
    fontSize: '13px',
    padding: '10px 0',
  },
  refreshBtn: {
    backgroundColor: '#161922',
    border: '1px solid #242c3d',
    color: '#c9d1d9',
    borderRadius: '6px',
    padding: '0 14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  filtersRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '12px',
  },
  filterGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  filterLabel: {
    fontSize: '11px',
    color: '#8b92a2',
  },
  selectInput: {
    backgroundColor: '#07080b',
    border: '1px solid #1c2230',
    borderRadius: '6px',
    color: '#c9d1d9',
    fontSize: '12px',
    padding: '8px 10px',
    outline: 'none',
  },
  sourcesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  resultsCountBar: {
    fontSize: '12px',
    color: '#6e7687',
  },
  sourceCard: {
    backgroundColor: '#0d0f15',
    border: '1px solid #1f2533',
    borderRadius: '8px',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    transition: 'border-color 0.2s ease',
  },
  sourceTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  titleLine: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    flexWrap: 'wrap',
  },
  sourceName: {
    fontSize: '15px',
    fontWeight: 700,
    color: '#ffffff',
  },
  sourceCategory: {
    fontSize: '11px',
    color: '#6e7687',
    fontFamily: 'monospace',
    marginTop: '2px',
    display: 'block',
  },
  sourceDesc: {
    fontSize: '12px',
    color: '#a0a8b9',
    lineHeight: '1.5',
  },
  manualNoticeBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    backgroundColor: '#201608',
    borderLeft: '3px solid #ffaa00',
    padding: '6px 10px',
    fontSize: '11px',
    color: '#ffcc66',
  },
  tagsRow: {
    display: 'flex',
    gap: '20px',
    flexWrap: 'wrap',
    fontSize: '11px',
  },
  tagGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    flexWrap: 'wrap',
  },
  tagLabel: {
    color: '#6e7687',
  },
  inputTag: {
    backgroundColor: '#1b2230',
    color: '#00e5ff',
    padding: '2px 6px',
    borderRadius: '4px',
    fontFamily: 'monospace',
  },
  outputTag: {
    backgroundColor: '#18241d',
    color: '#00ff66',
    padding: '2px 6px',
    borderRadius: '4px',
    fontFamily: 'monospace',
  },
  linksArea: {
    borderTop: '1px solid #161922',
    paddingTop: '8px',
  },
  linkHeaderLabel: {
    fontSize: '10px',
    color: '#555d71',
    textTransform: 'uppercase',
    display: 'block',
    marginBottom: '6px',
  },
  linksGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
  },
  officialLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    backgroundColor: '#07080a',
    border: '1px solid #230b0e',
    color: '#ff6666',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    textDecoration: 'none',
  },
  ufBadge: {
    backgroundColor: '#260609',
    color: '#ffaa00',
    padding: '1px 4px',
    borderRadius: '2px',
    fontSize: '9px',
    fontWeight: 700,
  },
  noResults: {
    padding: '60px',
    textAlign: 'center',
    color: '#555d71',
    fontSize: '14px',
  },
};
