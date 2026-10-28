import React, { useState } from 'react';
import {
  Search,
  Upload,
  Download,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle2,
  Clock,
  Copy,
  Check,
  Users,
  MapPin,
  Maximize2,
} from 'lucide-react';
import type {
  CategoryInfo,
  QueryResponse,
  ResultStatus,
  SourceExecutionResult,
} from '../types';
import { downloadReport, runFileUpload, runQuery } from '../services/api';
import { DossierModal } from './DossierModal';

interface InvestigationPanelProps {
  selectedCategory: string;
  categories: CategoryInfo[];
  historyEnabled: boolean;
}

export const InvestigationPanel: React.FC<InvestigationPanelProps> = ({
  selectedCategory,
  categories,
  historyEnabled,
}) => {
  const currentCat = categories.find((c) => c.id === selectedCategory) || categories[0];
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [expandedJson, setExpandedJson] = useState<Record<string, boolean>>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!target.trim()) return;

    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await runQuery(selectedCategory, target.trim(), undefined, historyEnabled);
      setResponse(res);
      setIsModalOpen(true); // Abre modal automaticamente ao concluir
    } catch (err: any) {
      setErrorMsg(err.message || 'Erro ao executar consulta.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await runFileUpload(file);
      setResponse(res);
      setTarget(file.name);
      setIsModalOpen(true); // Abre modal automaticamente ao concluir
    } catch (err: any) {
      setErrorMsg(err.message || 'Erro no envio do arquivo.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'json' | 'csv' | 'html') => {
    if (!response) return;
    try {
      await downloadReport(response, format);
    } catch (err: any) {
      alert(`Falha ao exportar relatório: ${err.message}`);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const toggleJson = (id: string) => {
    setExpandedJson((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  // Filtragem dos resultados
  const filteredResults = (response?.results || []).filter((r) => {
    if (statusFilter === 'all') return true;
    if (statusFilter === 'confirmado') return r.status === 'confirmado';
    if (statusFilter === 'parcial') return r.status === 'parcial';
    if (statusFilter === 'manual') return r.status === 'etapa_manual_necessaria' || r.requires_manual_action;
    if (statusFilter === 'problemas') return r.status === 'erro' || r.status === 'indisponivel' || r.status === 'nao_encontrado';
    return true;
  });

  return (
    <div style={styles.container}>
      {/* Header Info */}
      <div style={styles.header}>
        <div style={styles.titleGroup}>
          <h2 style={styles.catTitle}>{currentCat?.name || 'Investigação'}</h2>
          <p style={styles.catDesc}>{currentCat?.description}</p>
        </div>
      </div>

      {/* Target Input & Actions Form */}
      <form onSubmit={handleSearch} style={styles.searchCard}>
        <div style={styles.inputWrapper}>
          <Search size={18} color="#8890a4" style={styles.searchIcon} />
          <input
            type="text"
            style={styles.searchInput}
            placeholder={currentCat?.placeholder || 'Informe o dado a ser consultado...'}
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            disabled={loading}
          />
        </div>

        {selectedCategory === 'documentos' && (
          <label style={styles.uploadBtn}>
            <Upload size={16} />
            <span>Enviar Arquivo</span>
            <input
              type="file"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              disabled={loading}
            />
          </label>
        )}

        <button
          type="submit"
          style={{
            ...styles.executeBtn,
            ...(loading ? styles.executeBtnDisabled : {}),
          }}
          disabled={loading || !target.trim()}
        >
          {loading ? (
            <>
              <div style={styles.spinner}></div>
              <span>Consultando...</span>
            </>
          ) : (
            <>
              <span>Executar Consulta</span>
            </>
          )}
        </button>
      </form>

      {/* Error Message Banner */}
      {errorMsg && (
        <div style={styles.errorBanner}>
          <AlertCircle size={18} color="#ff4d4d" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Results Section */}
      {response && (
        <div style={styles.resultsArea}>
          {/* Big Instant Dossier Modal Action Banner */}
          <div style={styles.modalBanner}>
            <div style={styles.modalBannerLeft}>
              <span style={styles.modalBannerBadge}>⚡ DOSSIÊ UNIFICADO</span>
              <div>
                <strong style={styles.modalBannerTitle}>Resultado Consolidado em Modal</strong>
                <p style={styles.modalBannerSub}>Dados essenciais sintetizados para visualização imediata sem procura.</p>
              </div>
            </div>
            <button
              type="button"
              style={styles.openModalBtn}
              onClick={() => setIsModalOpen(true)}
            >
              <Maximize2 size={15} />
              <span>Abrir Informações em Modal</span>
            </button>
          </div>

          {/* Summary Metric Ribbon */}
          <div style={styles.summaryRibbon}>
            <div style={styles.targetBadge}>
              <span style={styles.summaryLabel}>ALVO (MASCARADO):</span>
              <strong style={styles.summaryVal}>{response.target_masked}</strong>
            </div>

            <div style={styles.metricsGroup}>
              <div style={styles.metricItem}>
                <span>Fontes:</span> <strong>{response.summary.total_sources}</strong>
              </div>
              <div style={{ ...styles.metricItem, color: '#00ff66' }}>
                <span>Concluídas:</span> <strong>{response.summary.completed}</strong>
              </div>
              <div style={{ ...styles.metricItem, color: '#ffaa00' }}>
                <span>Parciais:</span> <strong>{response.summary.partial}</strong>
              </div>
              <div style={{ ...styles.metricItem, color: '#00e5ff' }}>
                <span>Etapas Manuais:</span> <strong>{response.summary.manual_steps}</strong>
              </div>
              <div style={{ ...styles.metricItem, color: '#ff4d4d' }}>
                <span>Indisponíveis:</span> <strong>{response.summary.unavailable + response.summary.failed}</strong>
              </div>
              <div style={styles.metricItem}>
                <Clock size={12} />
                <span>{response.duration_seconds}s</span>
              </div>
            </div>

            {/* Export Toolbar */}
            <div style={styles.exportToolbar}>
              <span style={styles.exportLabel}>Exportar Dossiê:</span>
              <button
                type="button"
                style={styles.exportBtn}
                onClick={() => handleExport('html')}
                title="Dossiê HTML Completo com Estética de Investigação"
              >
                <Download size={13} /> HTML
              </button>
              <button
                type="button"
                style={styles.exportBtn}
                onClick={() => handleExport('json')}
                title="JSON Estruturado"
              >
                <Download size={13} /> JSON
              </button>
              <button
                type="button"
                style={styles.exportBtn}
                onClick={() => handleExport('csv')}
                title="CSV Tabular"
              >
                <Download size={13} /> CSV
              </button>
            </div>
          </div>

          {/* Results Filters */}
          <div style={styles.filterBar}>
            <span style={styles.filterTitle}>Filtrar Respostas:</span>
            {[
              { id: 'all', label: `Todos (${response.results.length})` },
              { id: 'confirmado', label: `Confirmados (${response.summary.completed})` },
              { id: 'parcial', label: `Parciais (${response.summary.partial})` },
              { id: 'manual', label: `Manuais / Portais (${response.summary.manual_steps})` },
              { id: 'problemas', label: `Indisponíveis (${response.summary.unavailable + response.summary.failed})` },
            ].map((f) => (
              <button
                key={f.id}
                style={{
                  ...styles.filterPill,
                  ...(statusFilter === f.id ? styles.filterPillActive : {}),
                }}
                onClick={() => setStatusFilter(f.id)}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Result Cards List */}
          <div style={styles.cardsList}>
            {filteredResults.map((r) => (
              <ResultCard
                key={r.source_id}
                result={r}
                isExpanded={!!expandedJson[r.source_id]}
                onToggleJson={() => toggleJson(r.source_id)}
                copiedKey={copiedKey}
                onCopy={copyToClipboard}
              />
            ))}

            {filteredResults.length === 0 && (
              <div style={styles.emptyFiltered}>
                Nenhum resultado corresponde ao filtro selecionado.
              </div>
            )}
          </div>

          <DossierModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            response={response}
            onExport={handleExport}
          />
        </div>
      )}
    </div>
  );
};

interface ResultCardProps {
  result: SourceExecutionResult;
  isExpanded: boolean;
  onToggleJson: () => void;
  copiedKey: string | null;
  onCopy: (text: string, key: string) => void;
}

const ResultCard: React.FC<ResultCardProps> = ({
  result,
  isExpanded,
  onToggleJson,
  copiedKey,
  onCopy,
}) => {
  const getStatusBadge = (status: ResultStatus) => {
    switch (status) {
      case 'confirmado':
        return <span className="badge badge-confirmed">● CONFIRMADO</span>;
      case 'parcial':
        return <span className="badge badge-partial">◐ PARCIAL</span>;
      case 'etapa_manual_necessaria':
        return <span className="badge badge-manual">▲ ETAPA MANUAL REQUERIDA</span>;
      case 'nao_encontrado':
        return <span className="badge badge-partial">○ NÃO LOCALIZADO</span>;
      case 'indisponivel':
        return <span className="badge badge-unavailable">✕ INDISPONÍVEL</span>;
      case 'erro':
        return <span className="badge badge-unavailable">✕ ERRO NA FONTE</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  const d = result.data;

  return (
    <div style={styles.card}>
      {/* Card Header */}
      <div style={styles.cardHeader}>
        <div>
          <div style={styles.cardTitleRow}>
            <h3 style={styles.cardTitle}>{result.source_name}</h3>
            {getStatusBadge(result.status)}
          </div>
          <span style={styles.cardMeta}>
            ID: {result.source_id} • Categoria: {result.category} • {result.execution_time_ms}ms
          </span>
        </div>

        <div style={styles.headerRight}>
          <span style={styles.confText}>Confiança: {result.confidence.toUpperCase()}</span>
          {result.verification_url && (
            <a
              href={result.verification_url}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.verifyBtn}
            >
              <ExternalLink size={13} />
              <span>Verificar na Fonte</span>
            </a>
          )}
        </div>
      </div>

      {/* Error message notice */}
      {result.error_message && (
        <div style={styles.errorNoticeBox}>
          <AlertCircle size={15} color="#ff6666" />
          <span>{result.error_message}</span>
        </div>
      )}

      {/* Specialized Formatted Data View */}
      {d && (
        <div style={styles.dataContentArea}>
          {/* 1. CNPJ Formatted View */}
          {result.category === 'cnpj' && d.razao_social && (
            <div style={styles.cnpjView}>
              <div style={styles.entityTitleRow}>
                <div>
                  <h4 style={styles.entityName}>{d.razao_social}</h4>
                  <span style={styles.entitySub}>Nome Fantasia: {d.nome_fantasia || '(Não informado)'}</span>
                </div>
                <div style={styles.situacaoPill}>
                  Situação: <strong>{d.situacao_cadastral || d.situacao || 'ATIVA'}</strong>
                </div>
              </div>

              <div style={styles.detailGrid}>
                <div><strong>CNPJ:</strong> {d.cnpj}</div>
                <div><strong>Data de Abertura:</strong> {d.data_inicio_atividade || d.data_situacao || '-'}</div>
                <div><strong>Natureza Jurídica:</strong> {d.natureza_juridica || '-'}</div>
                <div><strong>Porte:</strong> {d.porte || '-'}</div>
              </div>

              {d.cnae_principal && (
                <div style={styles.cnaeBox}>
                  <strong>CNAE Principal:</strong> {d.cnae_principal.codigo} - {d.cnae_principal.descricao}
                </div>
              )}

              {d.endereco && (
                <div style={styles.addressBox}>
                  <MapPin size={14} color="#ff6666" />
                  <span>
                    {d.endereco.logradouro}, {d.endereco.numero} {d.endereco.complemento || ''} - {d.endereco.bairro}, {d.endereco.municipio}/{d.endereco.uf} - CEP {d.endereco.cep}
                  </span>
                </div>
              )}

              {/* Quadro Societário (QSA) */}
              {d.qsa_socios && d.qsa_socios.length > 0 && (
                <div style={styles.qsaBox}>
                  <div style={styles.qsaHeader}>
                    <Users size={14} color="#00e5ff" />
                    <strong>Quadro de Sócios e Administradores (QSA) - {d.qsa_total} sócio(s)</strong>
                  </div>
                  <div style={styles.qsaList}>
                    {d.qsa_socios.map((s: any, idx: number) => (
                      <div key={idx} style={styles.socioItem}>
                        <span style={styles.socioName}>{s.nome_socio}</span>
                        <span style={styles.socioRole}>{s.qualificacao}</span>
                        {s.faixa_etaria && <span style={styles.socioAge}>({s.faixa_etaria})</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 2. CPF Official Portals View */}
          {result.category === 'cpf' && d.portais_oficiais_para_consulta && (
            <div style={styles.cpfView}>
              <div style={styles.cpfHeader}>
                <div>
                  <span style={styles.fieldLabel}>CPF REGULARMENTE FORMATADO & MASCARADO:</span>
                  <h4 style={styles.cpfNumber}>{d.cpf_mascarado}</h4>
                </div>
                <div style={styles.fiscalBadge}>
                  {d.regiao_fiscal_origem}
                </div>
              </div>

              <div style={styles.officialLinksGrid}>
                {d.portais_oficiais_para_consulta.map((link: any, idx: number) => (
                  <div key={idx} style={styles.officialPortalCard}>
                    <div style={styles.portalHead}>
                      <strong>{link.titulo}</strong>
                      <a href={link.url} target="_blank" rel="noopener noreferrer" style={styles.portalLink}>
                        ↗ Acessar Portal
                      </a>
                    </div>
                    <p style={styles.portalDesc}>{link.descricao}</p>
                    <span style={styles.portalReq}>Requer: {link.requer}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 3. Domínio e DNS View */}
          {result.category === 'dominio' && (
            <div style={styles.domainView}>
              {d.data_criacao && (
                <div style={styles.datesBar}>
                  <div><strong>Criação:</strong> {d.data_criacao.slice(0, 10)}</div>
                  {d.data_expiracao && <div><strong>Expiração:</strong> {d.data_expiracao.slice(0, 10)}</div>}
                  {d.servidores_dns && (
                    <div><strong>Nameservers:</strong> {d.servidores_dns.join(', ')}</div>
                  )}
                </div>
              )}

              {d.subdominios && d.subdominios.length > 0 && (
                <div style={styles.subdomainsBox}>
                  <strong>Subdomínios Descobertos ({d.total_subdominios_descobertos}):</strong>
                  <div style={styles.subdomainPills}>
                    {d.subdominios.map((sub: string, i: number) => (
                      <span key={i} style={styles.subPill}>{sub}</span>
                    ))}
                  </div>
                </div>
              )}

              {d.registros_a && (
                <div style={styles.dnsRecordsGrid}>
                  <div><strong>IPs (A):</strong> {d.registros_a.join(', ') || 'Nenhum'}</div>
                  <div><strong>Servidores MX:</strong> {d.servidores_mx.join(', ') || 'Nenhum'}</div>
                  {d.tem_spf && <div><strong>SPF:</strong> Configurado ✓</div>}
                  {d.tem_dmarc && <div><strong>DMARC:</strong> Configurado ✓</div>}
                </div>
              )}
            </div>
          )}

          {/* 4. IP e Rede View */}
          {result.category === 'ip' && (
            <div style={styles.ipView}>
              <div style={styles.ipMetrics}>
                {d.nome_rede && <div><strong>Rede / Bloco:</strong> {d.nome_rede} ({d.faixa_inicio} - {d.faixa_fim})</div>}
                {d.asn && <div><strong>ASN / Provedor:</strong> {d.asn} ({d.provedor_isp || d.organizacao || ''})</div>}
                {d.cidade && <div><strong>Localização da Rede (PoP):</strong> {d.cidade}, {d.regiao_estado} - {d.pais}</div>}
              </div>
            </div>
          )}

          {/* 5. Telefone View */}
          {result.category === 'telefone' && (
            <div style={styles.phoneView}>
              <div style={styles.phoneHeader}>
                <div>
                  <span style={styles.fieldLabel}>TELEFONE MASCARADO:</span>
                  <h4 style={styles.phoneNumber}>{d.telefone_mascarado}</h4>
                </div>
                <div style={styles.tipoTerminalBadge}>
                  {d.tipo_terminal} ({d.regiao_atendida})
                </div>
              </div>
              <div style={styles.phoneLinksRow}>
                {d.fontes_oficiais?.map((f: any, i: number) => (
                  <a key={i} href={f.url} target="_blank" rel="noopener noreferrer" style={styles.phoneLinkBtn}>
                    ↗ {f.titulo}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* 6. Username View */}
          {result.category === 'username' && (
            <div style={styles.usernameView}>
              {d.perfis_confirmados?.length > 0 && (
                <div style={styles.confirmedProfiles}>
                  <strong>Perfis Públicos Confirmados:</strong>
                  {d.perfis_confirmados.map((p: any, i: number) => (
                    <div key={i} style={styles.profileItem}>
                      <CheckCircle2 size={16} color="#00ff66" />
                      <div>
                        <strong>{p.plataforma}:</strong> {p.nome || p.perfil_url}
                        {p.bio && <span style={styles.profileBio}> - "{p.bio}"</span>}
                      </div>
                      <a href={p.perfil_url} target="_blank" rel="noopener noreferrer" style={styles.profileLink}>
                        Abrir Perfil
                      </a>
                    </div>
                  ))}
                </div>
              )}

              {d.links_para_verificacao_manual?.length > 0 && (
                <div style={styles.targetProfilesBox}>
                  <span style={styles.subLabel}>Links para Conferência Manual em Outras Redes:</span>
                  <div style={styles.targetLinksGrid}>
                    {d.links_para_verificacao_manual.map((tl: any, i: number) => (
                      <a key={i} href={tl.url} target="_blank" rel="noopener noreferrer" style={styles.targetLinkPill}>
                        ↗ {tl.plataforma}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 7. Documentos Forense View */}
          {result.category === 'documentos' && d.hashes && (
            <div style={styles.docView}>
              <div style={styles.docHashes}>
                <div style={styles.hashRow}>
                  <strong>SHA-256:</strong>
                  <code>{d.hashes.sha256}</code>
                  <button
                    style={styles.copyBtn}
                    onClick={() => onCopy(d.hashes.sha256, 'sha256')}
                  >
                    {copiedKey === 'sha256' ? <Check size={12} color="#00ff66" /> : <Copy size={12} />}
                  </button>
                </div>
                <div style={styles.hashRow}>
                  <strong>MD5:</strong>
                  <code>{d.hashes.md5}</code>
                  <button
                    style={styles.copyBtn}
                    onClick={() => onCopy(d.hashes.md5, 'md5')}
                  >
                    {copiedKey === 'md5' ? <Check size={12} color="#00ff66" /> : <Copy size={12} />}
                  </button>
                </div>
                <div style={styles.hashRow}>
                  <strong>Tamanho / Tipo:</strong>
                  <span>{d.tamanho_legivel} ({d.tipo_mime_detectado})</span>
                </div>
              </div>
            </div>
          )}

          {/* 8. Dados Públicos View */}
          {result.category === 'dados_publicos' && d.conjuntos_dados && (
            <div style={styles.dadosPubView}>
              <strong>Conjuntos de Dados Governamentais Encontrados ({d.total_conjuntos_encontrados}):</strong>
              <div style={styles.datasetList}>
                {d.conjuntos_dados.map((c: any, i: number) => (
                  <div key={i} style={styles.datasetItem}>
                    <strong>{c.titulo}</strong>
                    <span style={styles.datasetOrgao}>Órgão: {c.orgao || 'Governo Federal'}</span>
                    <a href={c.link_detalhes} target="_blank" rel="noopener noreferrer" style={styles.datasetLink}>
                      Acessar Dados
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.category === 'dados_publicos' && d.portais_oficiais_estruturados && (
            <div style={styles.portalLinksGrid}>
              {d.portais_oficiais_estruturados.map((p: any, i: number) => (
                <div key={i} style={styles.portalOfficialCard}>
                  <div style={styles.portalHead}>
                    <strong>{p.sistema}</strong>
                    <a href={p.url} target="_blank" rel="noopener noreferrer" style={styles.portalLink}>
                      ↗ Consultar
                    </a>
                  </div>
                  <span style={styles.portalDesc}>{p.tipo}</span>
                  <span style={styles.portalReq}>{p.orgao}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Limitations and Disclaimers */}
      {result.limitations?.length > 0 && (
        <div style={styles.limitationsBox}>
          <span style={styles.limLabel}>Avisos Legais & Técnicos:</span>
          <ul>
            {result.limitations.map((lim, idx) => (
              <li key={idx}>{lim}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Expandable Raw JSON Drawer */}
      <div style={styles.jsonDrawerArea}>
        <button style={styles.jsonToggleBtn} onClick={onToggleJson}>
          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          <span>{isExpanded ? 'Ocultar JSON Bruto' : 'Inspecionar JSON Bruto da Fonte'}</span>
        </button>

        {isExpanded && (
          <div className="terminal-box" style={{ marginTop: '8px' }}>
            <pre>{JSON.stringify(result.data || {}, null, 2)}</pre>
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
    marginBottom: '20px',
  },
  titleGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  catTitle: {
    fontSize: '22px',
    fontWeight: 800,
    color: '#ffffff',
    letterSpacing: '0.5px',
  },
  catDesc: {
    fontSize: '13px',
    color: '#8b92a2',
  },
  searchCard: {
    display: 'flex',
    gap: '12px',
    backgroundColor: '#0d1017',
    border: '1px solid #280d11',
    borderRadius: '8px',
    padding: '12px 16px',
    boxShadow: '0 4px 18px rgba(0,0,0,0.5)',
    marginBottom: '24px',
  },
  inputWrapper: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: '#07080b',
    border: '1px solid #1c2230',
    borderRadius: '6px',
    padding: '0 12px',
  },
  searchIcon: {
    flexShrink: 0,
  },
  searchInput: {
    flex: 1,
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#ffffff',
    fontSize: '14px',
    padding: '10px 0',
  },
  uploadBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    backgroundColor: '#1b202c',
    border: '1px solid #2f374a',
    borderRadius: '6px',
    padding: '0 14px',
    color: '#c9d1d9',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
  },
  executeBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#e50914',
    border: 'none',
    borderRadius: '6px',
    padding: '0 20px',
    color: '#ffffff',
    fontSize: '14px',
    fontWeight: 700,
    boxShadow: '0 0 12px rgba(229, 9, 20, 0.4)',
  },
  executeBtnDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  spinner: {
    width: '14px',
    height: '14px',
    border: '2px solid rgba(255,255,255,0.3)',
    borderTop: '2px solid #ffffff',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
  errorBanner: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: '#26090c',
    border: '1px solid #e50914',
    borderRadius: '6px',
    padding: '12px 16px',
    color: '#ff8080',
    fontSize: '13px',
    marginBottom: '20px',
  },
  resultsArea: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  modalBanner: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#180709',
    border: '2px solid #e50914',
    borderRadius: '8px',
    padding: '14px 18px',
    boxShadow: '0 0 16px rgba(229, 9, 20, 0.35)',
    flexWrap: 'wrap',
    gap: '12px',
  },
  modalBannerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
  },
  modalBannerBadge: {
    backgroundColor: '#e50914',
    color: '#ffffff',
    fontSize: '11px',
    fontWeight: 800,
    padding: '4px 8px',
    borderRadius: '4px',
    fontFamily: 'monospace',
    letterSpacing: '0.5px',
  },
  modalBannerTitle: {
    fontSize: '15px',
    color: '#ffffff',
    display: 'block',
  },
  modalBannerSub: {
    fontSize: '12px',
    color: '#ff9999',
    marginTop: '2px',
  },
  openModalBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#260609',
    border: '1px solid #ff3333',
    color: '#ffffff',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: 700,
    boxShadow: '0 0 10px rgba(255, 42, 42, 0.3)',
    cursor: 'pointer',
  },
  summaryRibbon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#0c0e14',
    border: '1px solid #280d11',
    borderRadius: '8px',
    padding: '12px 16px',
    flexWrap: 'wrap',
    gap: '12px',
  },
  targetBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  summaryLabel: {
    fontSize: '11px',
    color: '#8b92a2',
    fontFamily: 'monospace',
  },
  summaryVal: {
    fontSize: '14px',
    color: '#ff4d4d',
    fontFamily: 'monospace',
  },
  metricsGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
    fontSize: '12px',
    color: '#c9d1d9',
  },
  metricItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  exportToolbar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  exportLabel: {
    fontSize: '11px',
    color: '#6e7687',
  },
  exportBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    backgroundColor: '#161a24',
    border: '1px solid #283042',
    color: '#c9d1d9',
    fontSize: '11px',
    fontWeight: 700,
    padding: '5px 10px',
    borderRadius: '4px',
  },
  filterBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flexWrap: 'wrap',
  },
  filterTitle: {
    fontSize: '11px',
    color: '#6e7687',
    fontWeight: 700,
    textTransform: 'uppercase',
  },
  filterPill: {
    backgroundColor: '#12141c',
    border: '1px solid #202432',
    color: '#8b92a2',
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 600,
  },
  filterPillActive: {
    backgroundColor: '#26070a',
    borderColor: '#e50914',
    color: '#ffffff',
  },
  cardsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  card: {
    backgroundColor: '#0d0f15',
    border: '1px solid #260d10',
    borderRadius: '8px',
    padding: '18px 20px',
    boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    borderBottom: '1px solid #1a1e28',
    paddingBottom: '12px',
    marginBottom: '14px',
    flexWrap: 'wrap',
    gap: '10px',
  },
  cardTitleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '4px',
  },
  cardTitle: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#ffffff',
  },
  cardMeta: {
    fontSize: '11px',
    color: '#6e7687',
    fontFamily: 'monospace',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  confText: {
    fontSize: '10px',
    color: '#6e7687',
    fontFamily: 'monospace',
  },
  verifyBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    backgroundColor: '#1a080a',
    border: '1px solid #8b0000',
    color: '#ff6666',
    fontSize: '11px',
    fontWeight: 600,
    padding: '4px 8px',
    borderRadius: '4px',
    textDecoration: 'none',
  },
  errorNoticeBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#260a0e',
    borderLeft: '3px solid #e50914',
    padding: '8px 12px',
    fontSize: '12px',
    color: '#ff9999',
    marginBottom: '12px',
  },
  dataContentArea: {
    marginBottom: '12px',
  },
  cnpjView: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  entityTitleRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#12151e',
    padding: '10px 14px',
    borderRadius: '6px',
  },
  entityName: {
    fontSize: '15px',
    fontWeight: 700,
    color: '#ffffff',
  },
  entitySub: {
    fontSize: '12px',
    color: '#8b92a2',
  },
  situacaoPill: {
    backgroundColor: '#0d2818',
    border: '1px solid #00ff66',
    color: '#00ff66',
    fontSize: '11px',
    padding: '3px 8px',
    borderRadius: '4px',
    fontFamily: 'monospace',
  },
  detailGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '8px',
    fontSize: '12px',
    color: '#c9d1d9',
  },
  cnaeBox: {
    fontSize: '12px',
    color: '#b0b8c8',
    backgroundColor: '#0a0c10',
    padding: '8px 12px',
    borderRadius: '4px',
    border: '1px solid #1a1e28',
  },
  addressBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px',
    color: '#b0b8c8',
    backgroundColor: '#0a0c10',
    padding: '8px 12px',
    borderRadius: '4px',
    border: '1px solid #1a1e28',
  },
  qsaBox: {
    backgroundColor: '#080a0f',
    border: '1px solid #1a2232',
    borderRadius: '6px',
    padding: '10px 14px',
  },
  qsaHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '12px',
    color: '#00e5ff',
    marginBottom: '8px',
  },
  qsaList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  socioItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '12px',
    borderBottom: '1px dashed #141822',
    paddingBottom: '4px',
  },
  socioName: {
    color: '#ffffff',
    fontWeight: 600,
  },
  socioRole: {
    color: '#ffaa00',
    fontSize: '11px',
  },
  socioAge: {
    color: '#6e7687',
    fontSize: '11px',
  },
  cpfView: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  cpfHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#141822',
    padding: '12px 14px',
    borderRadius: '6px',
  },
  fieldLabel: {
    fontSize: '10px',
    color: '#8b92a2',
    letterSpacing: '0.5px',
  },
  cpfNumber: {
    fontSize: '16px',
    color: '#00ff66',
    fontFamily: 'monospace',
  },
  fiscalBadge: {
    fontSize: '11px',
    color: '#ffaa00',
    backgroundColor: '#261a00',
    border: '1px solid #664400',
    padding: '4px 8px',
    borderRadius: '4px',
    fontFamily: 'monospace',
  },
  officialLinksGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '10px',
  },
  officialPortalCard: {
    backgroundColor: '#0a0c10',
    border: '1px solid #202636',
    borderRadius: '6px',
    padding: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  portalHead: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '13px',
    color: '#ffffff',
  },
  portalLink: {
    color: '#ff4d4d',
    fontSize: '11px',
    fontWeight: 700,
    textDecoration: 'none',
  },
  portalDesc: {
    fontSize: '11px',
    color: '#8b92a2',
  },
  portalReq: {
    fontSize: '10px',
    color: '#00e5ff',
    fontFamily: 'monospace',
  },
  domainView: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  datesBar: {
    display: 'flex',
    gap: '20px',
    fontSize: '12px',
    color: '#c9d1d9',
    backgroundColor: '#12151e',
    padding: '8px 12px',
    borderRadius: '4px',
    flexWrap: 'wrap',
  },
  subdomainsBox: {
    fontSize: '12px',
  },
  subdomainPills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
    marginTop: '6px',
  },
  subPill: {
    backgroundColor: '#141822',
    border: '1px solid #242c3d',
    color: '#00e5ff',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontFamily: 'monospace',
  },
  dnsRecordsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '6px',
    fontSize: '12px',
    color: '#c9d1d9',
  },
  ipView: {
    fontSize: '12px',
    color: '#c9d1d9',
  },
  ipMetrics: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  phoneView: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  phoneHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#141822',
    padding: '10px 14px',
    borderRadius: '6px',
  },
  phoneNumber: {
    fontSize: '16px',
    color: '#00ff66',
    fontFamily: 'monospace',
  },
  tipoTerminalBadge: {
    fontSize: '11px',
    color: '#00e5ff',
    fontFamily: 'monospace',
  },
  phoneLinksRow: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  phoneLinkBtn: {
    color: '#ff6666',
    backgroundColor: '#1a080a',
    border: '1px solid #5a0a0f',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    textDecoration: 'none',
    fontWeight: 600,
  },
  usernameView: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  confirmedProfiles: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    fontSize: '12px',
  },
  profileItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#10171e',
    border: '1px solid #1a2a38',
    padding: '8px 12px',
    borderRadius: '4px',
    color: '#ffffff',
  },
  profileBio: {
    color: '#8b92a2',
    fontStyle: 'italic',
  },
  profileLink: {
    marginLeft: 'auto',
    color: '#00ff66',
    fontSize: '11px',
    fontWeight: 700,
    textDecoration: 'none',
  },
  targetProfilesBox: {
    marginTop: '6px',
  },
  subLabel: {
    fontSize: '11px',
    color: '#8b92a2',
  },
  targetLinksGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
    marginTop: '4px',
  },
  targetLinkPill: {
    backgroundColor: '#12141a',
    border: '1px solid #202432',
    color: '#c9d1d9',
    fontSize: '11px',
    padding: '3px 8px',
    borderRadius: '4px',
    textDecoration: 'none',
  },
  docView: {
    fontSize: '12px',
  },
  docHashes: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    backgroundColor: '#08090d',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #1b1e2a',
  },
  hashRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontFamily: 'monospace',
    fontSize: '12px',
  },
  copyBtn: {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#8b92a2',
    display: 'flex',
    alignItems: 'center',
  },
  dadosPubView: {
    fontSize: '12px',
  },
  datasetList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    marginTop: '6px',
  },
  datasetItem: {
    backgroundColor: '#0a0c10',
    border: '1px solid #1c2230',
    padding: '8px 12px',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  datasetOrgao: {
    fontSize: '11px',
    color: '#6e7687',
  },
  datasetLink: {
    marginLeft: 'auto',
    color: '#ff4d4d',
    fontSize: '11px',
    fontWeight: 700,
    textDecoration: 'none',
  },
  portalLinksGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '8px',
  },
  portalOfficialCard: {
    backgroundColor: '#0a0c10',
    border: '1px solid #202636',
    borderRadius: '4px',
    padding: '10px',
    display: 'flex',
    flexDirection: 'column',
    gap: '3px',
  },
  limitationsBox: {
    backgroundColor: '#080a0e',
    borderLeft: '3px solid #ffaa00',
    padding: '8px 12px',
    fontSize: '11px',
    color: '#8b92a2',
    marginBottom: '10px',
  },
  limLabel: {
    fontWeight: 700,
    color: '#ffaa00',
    marginBottom: '4px',
    display: 'block',
  },
  jsonDrawerArea: {
    borderTop: '1px solid #161a24',
    paddingTop: '8px',
  },
  jsonToggleBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#6e7687',
    fontSize: '11px',
    padding: 0,
  },
  emptyFiltered: {
    padding: '40px',
    textAlign: 'center',
    color: '#555d71',
    fontSize: '13px',
  },
};
