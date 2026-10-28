import React, { useState } from 'react';
import {
  X,
  Copy,
  Check,
  Download,
  MapPin,
  Users,
  CheckCircle2,
  AlertCircle,
  ShieldAlert,
} from 'lucide-react';
import type { QueryResponse } from '../types';

interface DossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  response: QueryResponse | null;
  onExport: (format: 'json' | 'csv' | 'html') => void;
}

export const DossierModal: React.FC<DossierModalProps> = ({
  isOpen,
  onClose,
  response,
  onExport,
}) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!isOpen || !response) return null;

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const cat = response.category.toLowerCase();
  const results = response.results;
  
  // Buscar o resultado principal com dados
  const primaryResult = results.find((r) => r.status === 'confirmado' && r.data) || results[0];
  const d = primaryResult?.data || {};

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={styles.header}>
          <div style={styles.headerLeft}>
            <div style={styles.tagBadge}>⚡ DOSSIÊ CONSOLIDADO</div>
            <div style={styles.titleRow}>
              <h2 style={styles.title}>Resultado da Investigação</h2>
              <span style={styles.targetPill}>{response.target_masked}</span>
              <span style={styles.catPill}>{response.category.toUpperCase()}</span>
            </div>
          </div>

          <div style={styles.headerRight}>
            <div style={styles.exportGroup}>
              <button
                style={styles.exportBtn}
                onClick={() => onExport('html')}
                title="Exportar Dossiê Pericial em HTML"
              >
                <Download size={13} /> HTML
              </button>
              <button
                style={styles.exportBtn}
                onClick={() => onExport('json')}
                title="Exportar JSON Estruturado"
              >
                <Download size={13} /> JSON
              </button>
            </div>
            <button style={styles.closeBtn} onClick={onClose} title="Fechar modal (Esc)">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div style={styles.body}>
          {/* Quick Metrics Banner */}
          <div style={styles.metricsBanner}>
            <div style={styles.metric}>
              <span style={styles.metricLabel}>Fontes Consultadas:</span>
              <strong style={styles.metricVal}>{response.summary.total_sources}</strong>
            </div>
            <div style={{ ...styles.metric, color: '#00ff66' }}>
              <span style={styles.metricLabel}>Concluídas:</span>
              <strong style={styles.metricVal}>{response.summary.completed}</strong>
            </div>
            <div style={{ ...styles.metric, color: '#ffaa00' }}>
              <span style={styles.metricLabel}>Parciais / Manuais:</span>
              <strong style={styles.metricVal}>{response.summary.partial + response.summary.manual_steps}</strong>
            </div>
            <div style={styles.metric}>
              <span style={styles.metricLabel}>Tempo de Execução:</span>
              <strong style={styles.metricVal}>{response.duration_seconds}s</strong>
            </div>
          </div>

          {/* DADOS CONSOLIDADOS POR CATEGORIA */}

          {/* 1. CNPJ CONSOLIDADO */}
          {cat === 'cnpj' && (
            <div style={styles.section}>
              {d.razao_social ? (
                <>
                  <div style={styles.mainCompanyCard}>
                    <div style={styles.companyTop}>
                      <div>
                        <h3 style={styles.razaoSocial}>{d.razao_social}</h3>
                        <span style={styles.nomeFantasia}>
                          Nome Fantasia: <strong>{d.nome_fantasia || '(Não possui nome fantasia)'}</strong>
                        </span>
                      </div>
                      <div
                        style={{
                          ...styles.situacaoPill,
                          backgroundColor: d.situacao_cadastral === 'ATIVA' ? '#0d2b17' : '#2b0d11',
                          borderColor: d.situacao_cadastral === 'ATIVA' ? '#00ff66' : '#ff4d4d',
                          color: d.situacao_cadastral === 'ATIVA' ? '#00ff66' : '#ff4d4d',
                        }}
                      >
                        ● {d.situacao_cadastral || d.situacao || 'SITUAÇÃO ATIVA'}
                      </div>
                    </div>

                    <div style={styles.grid4}>
                      <div style={styles.infoBlock}>
                        <span style={styles.infoLabel}>CNPJ Formatado:</span>
                        <div style={styles.copyableRow}>
                          <span style={styles.infoValMono}>{d.cnpj}</span>
                          <button
                            style={styles.inlineCopy}
                            onClick={() => copyToClipboard(d.cnpj, 'cnpj')}
                          >
                            {copiedKey === 'cnpj' ? <Check size={12} color="#00ff66" /> : <Copy size={12} />}
                          </button>
                        </div>
                      </div>

                      <div style={styles.infoBlock}>
                        <span style={styles.infoLabel}>Data de Abertura:</span>
                        <span style={styles.infoVal}>{d.data_inicio_atividade || d.data_situacao || '-'}</span>
                      </div>

                      <div style={styles.infoBlock}>
                        <span style={styles.infoLabel}>Porte da Empresa:</span>
                        <span style={styles.infoVal}>{d.porte || '-'}</span>
                      </div>

                      <div style={styles.infoBlock}>
                        <span style={styles.infoLabel}>Capital Social:</span>
                        <span style={styles.infoVal}>
                          {d.capital_social ? `R$ ${Number(d.capital_social).toLocaleString('pt-BR')}` : '-'}
                        </span>
                      </div>
                    </div>

                    {d.natureza_juridica && (
                      <div style={styles.singleRow}>
                        <span style={styles.infoLabel}>Natureza Jurídica:</span>
                        <span style={styles.infoVal}>{d.natureza_juridica}</span>
                      </div>
                    )}

                    {/* Endereço */}
                    {d.endereco && (
                      <div style={styles.addressCard}>
                        <MapPin size={16} color="#ff4d4d" style={{ flexShrink: 0 }} />
                        <div>
                          <strong style={{ color: '#ffffff' }}>Endereço Comercial Cadastrado:</strong>
                          <div style={{ color: '#c9d1d9', fontSize: '13px', marginTop: '2px' }}>
                            {d.endereco.logradouro}, {d.endereco.numero} {d.endereco.complemento || ''} - {d.endereco.bairro}, {d.endereco.municipio}/{d.endereco.uf} - CEP: {d.endereco.cep}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* CNAEs */}
                    {d.cnae_principal && (
                      <div style={styles.cnaeCard}>
                        <strong style={{ color: '#00e5ff', fontSize: '12px' }}>Atividade Econômica Principal (CNAE):</strong>
                        <div style={{ color: '#ffffff', fontSize: '13px', marginTop: '2px' }}>
                          <code>{d.cnae_principal.codigo}</code> — {d.cnae_principal.descricao}
                        </div>
                      </div>
                    )}

                    {/* Quadro Societário (QSA) */}
                    {d.qsa_socios && d.qsa_socios.length > 0 && (
                      <div style={styles.qsaContainer}>
                        <div style={styles.qsaHeadRow}>
                          <Users size={16} color="#00e5ff" />
                          <h4 style={styles.qsaTitle}>
                            Quadro de Sócios e Administradores (QSA) — {d.qsa_total} sócio(s) localizado(s)
                          </h4>
                        </div>

                        <div style={styles.qsaTable}>
                          {d.qsa_socios.map((s: any, idx: number) => (
                            <div key={idx} style={styles.qsaCard}>
                              <div style={styles.qsaCardTop}>
                                <strong style={styles.socioNome}>{s.nome_socio}</strong>
                                <span style={styles.socioCargo}>{s.qualificacao}</span>
                              </div>
                              <div style={styles.qsaCardBottom}>
                                {s.faixa_etaria && <span>Faixa Etária: {s.faixa_etaria}</span>}
                                {s.data_entrada_sociedade && <span>Entrada: {s.data_entrada_sociedade}</span>}
                                {s.pais && <span>País: {s.pais}</span>}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div style={styles.alertCard}>
                  <AlertCircle size={18} color="#ffaa00" />
                  <span>{primaryResult.error_message || 'Nenhum dado cadastral localizado para este CNPJ.'}</span>
                </div>
              )}
            </div>
          )}

          {/* 2. CPF CONSOLIDADO */}
          {cat === 'cpf' && (
            <div style={styles.section}>
              <div style={styles.cpfHeroCard}>
                <div style={styles.cpfHeroTop}>
                  <div>
                    <span style={styles.heroSub}>IDENTIFICADOR VALIDADO (LGPD MASCARADO)</span>
                    <h3 style={styles.cpfDisplay}>{d.cpf_mascarado || response.target_masked}</h3>
                  </div>

                  <div style={styles.validStatusBadge}>
                    <CheckCircle2 size={16} color="#00ff66" />
                    <span>Dígitos Verificadores Válidos (Módulo 11)</span>
                  </div>
                </div>

                <div style={styles.regionInfo}>
                  <strong>Região Fiscal de Origem (9º Dígito):</strong>{' '}
                  <span style={{ color: '#00e5ff' }}>{d.regiao_fiscal_origem || 'Detectada com sucesso'}</span>
                </div>
              </div>

              <div style={styles.officialSectionTitle}>
                <span>PORTAIS GOVERNAMENTAIS OFICIAIS PARA CONSULTA DIRETA</span>
              </div>

              <div style={styles.portalCardsGrid}>
                {d.portais_oficiais_para_consulta?.map((p: any, idx: number) => (
                  <div key={idx} style={styles.portalActionCard}>
                    <div style={styles.portalActionTop}>
                      <strong style={styles.portalActionTitle}>{p.titulo}</strong>
                      <a
                        href={p.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={styles.openPortalBtn}
                      >
                        ↗ Consultar no Portal
                      </a>
                    </div>
                    <p style={styles.portalActionDesc}>{p.descricao}</p>
                    <div style={styles.portalActionReq}>
                      <strong>Requisitos oficiais:</strong> {p.requer}
                    </div>
                  </div>
                ))}
              </div>

              <div style={styles.lgpdNotice}>
                <ShieldAlert size={16} color="#ffaa00" style={{ flexShrink: 0 }} />
                <span>
                  <strong>Aviso de Proteção ao Cidadão:</strong> O Governo Federal exige data de nascimento e desafio CAPTCHA humano para emitir a situação cadastral no CPF. O OSINT Brazuca Ultimate respeita a LGPD e disponibiliza o atalho legítimo sem quebrar barreiras ilegais.
                </span>
              </div>
            </div>
          )}

          {/* 3. DOMÍNIO CONSOLIDADO */}
          {cat === 'dominio' && (
            <div style={styles.section}>
              <div style={styles.mainCompanyCard}>
                <div style={styles.companyTop}>
                  <div>
                    <h3 style={styles.razaoSocial}>{d.dominio || response.target_raw}</h3>
                    <span style={styles.nomeFantasia}>Handle RDAP: {d.handle || '-'}</span>
                  </div>
                  {d.status && (
                    <div style={styles.situacaoPill}>
                      ● {Array.isArray(d.status) ? d.status.join(', ') : d.status}
                    </div>
                  )}
                </div>

                <div style={styles.grid4}>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Data de Registro:</span>
                    <span style={styles.infoVal}>{d.data_criacao ? d.data_criacao.slice(0, 10) : '-'}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Expiração:</span>
                    <span style={styles.infoVal}>{d.data_expiracao ? d.data_expiracao.slice(0, 10) : '-'}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>SPF:</span>
                    <span style={styles.infoVal}>{d.tem_spf ? 'Configurado ✓' : 'Não encontrado'}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>DMARC:</span>
                    <span style={styles.infoVal}>{d.tem_dmarc ? 'Configurado ✓' : 'Não encontrado'}</span>
                  </div>
                </div>

                {/* Subdomínios crt.sh */}
                {results.find((r) => r.source_id === 'tls_cert')?.data?.subdominios && (
                  <div style={styles.subdomainsBox}>
                    <strong style={{ color: '#00ff66', fontSize: '13px' }}>
                      Subdomínios Descobertos via Certificate Transparency ({results.find((r) => r.source_id === 'tls_cert')?.data?.total_subdominios_descobertos}):
                    </strong>
                    <div style={styles.subdomainPills}>
                      {results.find((r) => r.source_id === 'tls_cert')?.data?.subdominios.slice(0, 30).map((sub: string, i: number) => (
                        <span key={i} style={styles.subPill}>{sub}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Servidores DNS */}
                {d.servidores_dns && (
                  <div style={styles.singleRow}>
                    <span style={styles.infoLabel}>Servidores Nameservers (NS):</span>
                    <span style={styles.infoVal}>{d.servidores_dns.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 4. IP E REDE CONSOLIDADO */}
          {cat === 'ip' && (
            <div style={styles.section}>
              <div style={styles.mainCompanyCard}>
                <div style={styles.companyTop}>
                  <div>
                    <h3 style={styles.razaoSocial}>{d.ip || response.target_raw}</h3>
                    <span style={styles.nomeFantasia}>Rede: {d.nome_rede || d.faixa_inicio || '-'}</span>
                  </div>
                </div>

                <div style={styles.grid4}>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Bloco de Endereços:</span>
                    <span style={styles.infoValMono}>{d.faixa_inicio} - {d.faixa_fim}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>ASN / Provedor:</span>
                    <span style={styles.infoVal}>{d.asn || '-'}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>País / Localização:</span>
                    <span style={styles.infoVal}>{d.pais || d.regiao_estado || '-'}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Versão IP:</span>
                    <span style={styles.infoVal}>{d.ip_versao || 'IPv4'}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5. TELEFONE CONSOLIDADO */}
          {cat === 'telefone' && (
            <div style={styles.section}>
              <div style={styles.mainCompanyCard}>
                <div style={styles.companyTop}>
                  <div>
                    <span style={styles.infoLabel}>NÚMERO NORMALIZADO (E.164)</span>
                    <h3 style={styles.razaoSocial}>{d.padrao_e164 || d.telefone_formatado}</h3>
                  </div>
                  <div style={styles.situacaoPill}>
                    ● {d.tipo_terminal || 'Linha Telefônica'}
                  </div>
                </div>

                <div style={styles.grid4}>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>DDD / Código de Área:</span>
                    <span style={styles.infoVal}>{d.ddd}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Região Atendida:</span>
                    <span style={styles.infoVal}>{d.regiao_atendida}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Tipo de Terminal:</span>
                    <span style={styles.infoVal}>{d.tipo_terminal}</span>
                  </div>
                </div>

                <div style={styles.phoneActionsRow}>
                  <a
                    href={`https://wa.me/${(d.padrao_e164 || '').replace(/\D/g, '')}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ ...styles.actionBtn, backgroundColor: '#0d2b17', borderColor: '#00ff66', color: '#00ff66' }}
                  >
                    ↗ Checar Presença no WhatsApp
                  </a>
                  <a
                    href="https://consultanumero.abrtelecom.com.br/consultanumero/"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ ...styles.actionBtn, backgroundColor: '#201608', borderColor: '#ffaa00', color: '#ffaa00' }}
                  >
                    ↗ Consultar Operadora / Portabilidade (ABR Telecom)
                  </a>
                </div>
              </div>
            </div>
          )}

          {/* 6. EMAIL CONSOLIDADO */}
          {cat === 'email' && (
            <div style={styles.section}>
              <div style={styles.mainCompanyCard}>
                <div style={styles.companyTop}>
                  <div>
                    <span style={styles.infoLabel}>E-MAIL MASCARADO:</span>
                    <h3 style={styles.razaoSocial}>{d.email_mascarado || response.target_masked}</h3>
                  </div>
                  <div
                    style={{
                      ...styles.situacaoPill,
                      color: d.dominio_recebe_emails ? '#00ff66' : '#ff4d4d',
                      borderColor: d.dominio_recebe_emails ? '#00ff66' : '#ff4d4d',
                    }}
                  >
                    ● {d.dominio_recebe_emails ? 'DOMÍNIO APTO A RECEBER' : 'SEM MX CONFIGURADO'}
                  </div>
                </div>

                <div style={styles.grid4}>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Domínio:</span>
                    <span style={styles.infoVal}>{d.dominio}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>É Temporário / Descartável:</span>
                    <span style={{ ...styles.infoVal, color: d.e_descartavel ? '#ff4d4d' : '#00ff66' }}>
                      {d.e_descartavel ? 'SIM (Descartável)' : 'NÃO (Provedor Normal)'}
                    </span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Possui SPF:</span>
                    <span style={styles.infoVal}>{d.possui_spf ? 'Configurado ✓' : 'Ausente'}</span>
                  </div>
                  <div style={styles.infoBlock}>
                    <span style={styles.infoLabel}>Possui DMARC:</span>
                    <span style={styles.infoVal}>{d.possui_dmarc ? 'Configurado ✓' : 'Ausente'}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 7. USERNAME CONSOLIDADO */}
          {cat === 'username' && (
            <div style={styles.section}>
              <div style={styles.mainCompanyCard}>
                <h3 style={styles.razaoSocial}>@{d.username_pesquisado || response.target_raw}</h3>
                
                {d.perfis_confirmados && d.perfis_confirmados.length > 0 ? (
                  <div style={{ marginTop: '12px' }}>
                    <strong style={{ color: '#00ff66', fontSize: '13px' }}>Perfis Oficiais Confirmados:</strong>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                      {d.perfis_confirmados.map((p: any, i: number) => (
                        <div key={i} style={styles.profileConfirmedRow}>
                          <CheckCircle2 size={16} color="#00ff66" />
                          <div>
                            <strong>{p.plataforma}:</strong> {p.nome || p.perfil_url}
                            {p.bio && <span style={{ color: '#8b92a2', fontStyle: 'italic' }}> — "{p.bio}"</span>}
                          </div>
                          <a href={p.perfil_url} target="_blank" rel="noopener noreferrer" style={styles.openProfileBtn}>
                            Abrir Perfil
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div style={{ color: '#8b92a2', fontSize: '13px', marginTop: '8px' }}>
                    Nenhum perfil público com este username foi localizado via APIs públicas automáticas.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 8. DOCUMENTOS FORENSE CONSOLIDADO */}
          {cat === 'documentos' && d.hashes && (
            <div style={styles.section}>
              <div style={styles.mainCompanyCard}>
                <h3 style={styles.razaoSocial}>{d.nome_arquivo || 'Arquivo Analisado'}</h3>
                <span style={styles.nomeFantasia}>
                  Tamanho: {d.tamanho_legivel} • Formato: {d.tipo_mime_detectado}
                </span>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '14px' }}>
                  <div style={styles.hashLine}>
                    <strong style={{ width: '80px', color: '#ffaa00' }}>SHA-256:</strong>
                    <code>{d.hashes.sha256}</code>
                    <button style={styles.inlineCopy} onClick={() => copyToClipboard(d.hashes.sha256, 'sha256')}>
                      {copiedKey === 'sha256' ? <Check size={12} color="#00ff66" /> : <Copy size={12} />}
                    </button>
                  </div>
                  <div style={styles.hashLine}>
                    <strong style={{ width: '80px', color: '#00e5ff' }}>MD5:</strong>
                    <code>{d.hashes.md5}</code>
                    <button style={styles.inlineCopy} onClick={() => copyToClipboard(d.hashes.md5, 'md5')}>
                      {copiedKey === 'md5' ? <Check size={12} color="#00ff66" /> : <Copy size={12} />}
                    </button>
                  </div>
                </div>

                <div style={styles.phoneActionsRow}>
                  <a
                    href={`https://www.virustotal.com/gui/file/${d.hashes.sha256}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ ...styles.actionBtn, backgroundColor: '#0d1526', borderColor: '#00e5ff', color: '#00e5ff' }}
                  >
                    ↗ Checar Reputação no VirusTotal
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={styles.footer}>
          <span style={styles.footerNotice}>
            🔒 Consulta realizada estritamente em conformidade com a LGPD e termos oficiais das fontes.
          </span>
          <button style={styles.closeFooterBtn} onClick={onClose}>
            Fechar Dossiê
          </button>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(5, 6, 9, 0.88)',
    backdropFilter: 'blur(6px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
  },
  modal: {
    backgroundColor: '#0c0e15',
    border: '2px solid #8b0000',
    borderRadius: '12px',
    width: '100%',
    maxWidth: '920px',
    maxHeight: '90vh',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 0 35px rgba(229, 9, 20, 0.35)',
    overflow: 'hidden',
    animation: 'fadeIn 0.2s ease-out',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 22px',
    backgroundColor: '#08090d',
    borderBottom: '1px solid #23080b',
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  tagBadge: {
    fontSize: '10px',
    fontWeight: 800,
    color: '#ff3333',
    letterSpacing: '1px',
    fontFamily: 'monospace',
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  title: {
    fontSize: '18px',
    fontWeight: 800,
    color: '#ffffff',
  },
  targetPill: {
    backgroundColor: '#1b2232',
    color: '#00ff66',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: 'monospace',
    fontWeight: 700,
  },
  catPill: {
    backgroundColor: '#260609',
    color: '#ff6666',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '10px',
    fontFamily: 'monospace',
    fontWeight: 700,
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  exportGroup: {
    display: 'flex',
    gap: '6px',
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
    padding: '5px 9px',
    borderRadius: '4px',
  },
  closeBtn: {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#8b92a2',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '4px',
  },
  body: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '18px',
  },
  metricsBanner: {
    display: 'flex',
    gap: '20px',
    backgroundColor: '#08090d',
    border: '1px solid #1a1e28',
    borderRadius: '6px',
    padding: '10px 16px',
    fontSize: '12px',
    flexWrap: 'wrap',
  },
  metric: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  metricLabel: {
    color: '#6e7687',
  },
  metricVal: {
    color: '#ffffff',
    fontFamily: 'monospace',
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  mainCompanyCard: {
    backgroundColor: '#0f121a',
    border: '1px solid #232a3b',
    borderRadius: '8px',
    padding: '18px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  companyTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    borderBottom: '1px solid #1c2230',
    paddingBottom: '12px',
    flexWrap: 'wrap',
    gap: '10px',
  },
  razaoSocial: {
    fontSize: '18px',
    fontWeight: 800,
    color: '#ffffff',
  },
  nomeFantasia: {
    fontSize: '13px',
    color: '#8b92a2',
    marginTop: '2px',
    display: 'block',
  },
  situacaoPill: {
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 700,
    fontFamily: 'monospace',
    border: '1px solid',
  },
  grid4: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '12px',
  },
  infoBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  infoLabel: {
    fontSize: '10px',
    color: '#6e7687',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  infoVal: {
    fontSize: '13px',
    color: '#ffffff',
    fontWeight: 600,
  },
  infoValMono: {
    fontSize: '13px',
    color: '#00ff66',
    fontFamily: 'monospace',
    fontWeight: 700,
  },
  copyableRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  inlineCopy: {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#8b92a2',
    display: 'flex',
    alignItems: 'center',
  },
  singleRow: {
    display: 'flex',
    gap: '8px',
    fontSize: '13px',
  },
  addressCard: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '10px',
    backgroundColor: '#090b10',
    border: '1px solid #1a202e',
    borderRadius: '6px',
    padding: '12px',
  },
  cnaeCard: {
    backgroundColor: '#090b10',
    border: '1px solid #1a202e',
    borderRadius: '6px',
    padding: '10px 12px',
  },
  qsaContainer: {
    backgroundColor: '#090b10',
    border: '1px solid #1c2638',
    borderRadius: '6px',
    padding: '14px',
  },
  qsaHeadRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '10px',
  },
  qsaTitle: {
    fontSize: '13px',
    fontWeight: 700,
    color: '#00e5ff',
  },
  qsaTable: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '8px',
  },
  qsaCard: {
    backgroundColor: '#121622',
    border: '1px solid #1f2738',
    borderRadius: '4px',
    padding: '10px',
  },
  qsaCardTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  socioNome: {
    fontSize: '13px',
    color: '#ffffff',
  },
  socioCargo: {
    fontSize: '11px',
    color: '#ffaa00',
    fontFamily: 'monospace',
  },
  qsaCardBottom: {
    fontSize: '11px',
    color: '#6e7687',
    marginTop: '4px',
    display: 'flex',
    gap: '10px',
  },
  cpfHeroCard: {
    backgroundColor: '#0f121a',
    border: '1px solid #232a3b',
    borderRadius: '8px',
    padding: '18px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  cpfHeroTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  heroSub: {
    fontSize: '10px',
    color: '#6e7687',
    letterSpacing: '0.5px',
  },
  cpfDisplay: {
    fontSize: '22px',
    fontWeight: 800,
    color: '#00ff66',
    fontFamily: 'monospace',
    letterSpacing: '1px',
  },
  validStatusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    backgroundColor: '#0d2b17',
    border: '1px solid #00ff66',
    color: '#00ff66',
    padding: '6px 12px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: 600,
  },
  regionInfo: {
    fontSize: '13px',
    color: '#c9d1d9',
  },
  officialSectionTitle: {
    fontSize: '11px',
    fontWeight: 700,
    color: '#6e7687',
    letterSpacing: '1px',
    marginTop: '6px',
  },
  portalCardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '10px',
  },
  portalActionCard: {
    backgroundColor: '#0a0d14',
    border: '1px solid #1c2230',
    borderRadius: '6px',
    padding: '14px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  portalActionTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  portalActionTitle: {
    fontSize: '13px',
    color: '#ffffff',
  },
  openPortalBtn: {
    color: '#ff4d4d',
    fontSize: '11px',
    fontWeight: 700,
    textDecoration: 'none',
    backgroundColor: '#260609',
    border: '1px solid #8b0000',
    padding: '4px 8px',
    borderRadius: '4px',
    flexShrink: 0,
  },
  portalActionDesc: {
    fontSize: '12px',
    color: '#8b92a2',
  },
  portalActionReq: {
    fontSize: '11px',
    color: '#00e5ff',
    fontFamily: 'monospace',
  },
  lgpdNotice: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: '#1a1408',
    border: '1px solid #ffaa00',
    borderRadius: '6px',
    padding: '10px 14px',
    fontSize: '12px',
    color: '#ffdd99',
    lineHeight: '1.4',
  },
  phoneActionsRow: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
    marginTop: '8px',
  },
  actionBtn: {
    padding: '8px 14px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: 700,
    textDecoration: 'none',
    border: '1px solid',
  },
  subdomainsBox: {
    marginTop: '10px',
  },
  subdomainPills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
    marginTop: '6px',
  },
  subPill: {
    backgroundColor: '#090b10',
    border: '1px solid #1f2738',
    color: '#00e5ff',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontFamily: 'monospace',
  },
  profileConfirmedRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#0a0d14',
    padding: '8px 12px',
    borderRadius: '4px',
    fontSize: '13px',
    color: '#ffffff',
  },
  openProfileBtn: {
    marginLeft: 'auto',
    color: '#00ff66',
    fontSize: '11px',
    fontWeight: 700,
    textDecoration: 'none',
  },
  hashLine: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontFamily: 'monospace',
    fontSize: '12px',
    color: '#c9d1d9',
  },
  alertCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: '#1f1609',
    padding: '14px',
    borderRadius: '6px',
    color: '#ffcc66',
    fontSize: '13px',
  },
  footer: {
    padding: '12px 22px',
    backgroundColor: '#08090d',
    borderTop: '1px solid #1a1e28',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  footerNotice: {
    fontSize: '11px',
    color: '#555d71',
  },
  closeFooterBtn: {
    backgroundColor: '#161922',
    border: '1px solid #283042',
    color: '#ffffff',
    fontSize: '12px',
    fontWeight: 700,
    padding: '6px 14px',
    borderRadius: '4px',
  },
};
