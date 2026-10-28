import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Lock,
  Trash2,
  BookOpen,
  Check,
} from 'lucide-react';
import { clearHistory, fetchHistory, toggleHistory } from '../services/api';

interface SettingsViewProps {
  historyEnabled: boolean;
  onUpdateHistoryEnabled: (enabled: boolean) => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  historyEnabled,
  onUpdateHistoryEnabled,
}) => {
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const loadHist = async () => {
    try {
      const res = await fetchHistory();
      setHistoryItems(res.history || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadHist();
  }, [historyEnabled]);

  const handleToggle = async (newVal: boolean) => {
    setLoading(true);
    try {
      const res = await toggleHistory(newVal);
      onUpdateHistoryEnabled(res.enabled);
      setMsg(res.enabled ? 'Histórico ativado.' : 'Histórico desativado (Padrão Seguro).');
      setTimeout(() => setMsg(null), 3000);
    } catch (err: any) {
      alert(`Erro: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!confirm('Deseja realmente limpar todo o histórico de investigações salvas?')) return;
    try {
      await clearHistory();
      setHistoryItems([]);
      setMsg('Histórico excluído com sucesso.');
      setTimeout(() => setMsg(null), 3000);
    } catch (err: any) {
      alert(`Erro: ${err.message}`);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Privacidade & Configurações de Segurança</h2>
        <p style={styles.sub}>
          Diretrizes rígidas de privacidade, conformidade LGPD e controles locais do OSINT Brazuca Ultimate.
        </p>
      </div>

      {msg && (
        <div style={styles.msgBox}>
          <Check size={16} color="#00ff66" />
          <span>{msg}</span>
        </div>
      )}

      {/* Security Manifesto Box */}
      <div style={styles.manifestoCard}>
        <div style={styles.cardHeader}>
          <ShieldCheck size={20} color="#ff3333" />
          <h3 style={styles.cardTitle}>Manifesto de Privacidade & Conformidade Legal</h3>
        </div>
        <p style={styles.manifestoText}>
          O <strong>OSINT Brazuca Ultimate</strong> foi desenhado desde a sua primeira linha de código para garantir segurança jurídica, proteção de privacidade e conformidade estrita com a <strong>Lei Geral de Proteção de Dados (Lei 13.709/2018)</strong>:
        </p>
        <ul style={styles.manifestoList}>
          <li>
            <strong>100% Local:</strong> O backend escuta estritamente no endereço de loopback <code>127.0.0.1</code>. Nenhuma telemetria ou dado de investigação é transmitido para servidores de terceiros.
          </li>
          <li>
            <strong>Sem Armazenamento por Padrão:</strong> Suas pesquisas (CPFs, CNPJs, alvos) NÃO são salvas em disco por padrão.
          </li>
          <li>
            <strong>Mascaramento Obrigatório:</strong> Identificadores de pessoas físicas são mascarados em todas as telas, exportações e logs (ex: <code>***.XXX.XXX-**</code>).
          </li>
          <li>
            <strong>Sem Força Bruta ou Invasão:</strong> O sistema não realiza enumeração indiscriminada nem tenta contornar controles de acesso, credenciais ou paywalls.
          </li>
          <li>
            <strong>Isolamento SSRF:</strong> Consultas de rede bloqueiam endereços IP privados (RFC 1918), serviços de metadados cloud (169.254.169.254) e redes de loopback internas.
          </li>
        </ul>
      </div>

      {/* History Control Card */}
      <div style={styles.sectionCard}>
        <div style={styles.cardHeader}>
          <Lock size={18} color="#ffaa00" />
          <h3 style={styles.cardTitle}>Persistência e Histórico de Consultas</h3>
        </div>
        <p style={styles.sectionDesc}>
          Por padrão ético, o histórico de investigações permanece <strong>DESATIVADO</strong>. Se você ativar a persistência, os dados serão salvos localmente em um banco SQLite criptograficamente contido na máquina do operador com alvos já mascarados.
        </p>

        <div style={styles.toggleRow}>
          <div style={styles.toggleInfo}>
            <strong>Gravar histórico de consultas localmente:</strong>
            <span style={styles.toggleSub}>
              {historyEnabled ? 'Atualmente ATIVADO' : 'Atualmente DESLIGADO (Recomendado)'}
            </span>
          </div>

          <div style={styles.btnGroup}>
            <button
              style={{
                ...styles.toggleBtn,
                ...(historyEnabled ? styles.toggleBtnActive : {}),
              }}
              onClick={() => handleToggle(true)}
              disabled={loading}
            >
              Ativar
            </button>
            <button
              style={{
                ...styles.toggleBtn,
                ...(!historyEnabled ? styles.toggleBtnActive : {}),
              }}
              onClick={() => handleToggle(false)}
              disabled={loading}
            >
              Desativar
            </button>
          </div>
        </div>

        {historyEnabled && (
          <div style={styles.historyListArea}>
            <div style={styles.historyListHeader}>
              <span>Registros Recentes no Histórico Local ({historyItems.length})</span>
              {historyItems.length > 0 && (
                <button style={styles.clearBtn} onClick={handleClear}>
                  <Trash2 size={13} /> Limpar Histórico
                </button>
              )}
            </div>

            {historyItems.length > 0 ? (
              <div style={styles.historyTable}>
                {historyItems.map((h) => (
                  <div key={h.id} style={styles.historyRow}>
                    <span style={styles.histCat}>[{h.category.toUpperCase()}]</span>
                    <strong style={styles.histTarget}>{h.target_masked}</strong>
                    <span style={styles.histDate}>{h.timestamp.slice(0, 19).replace('T', ' ')}</span>
                  </div>
                ))}
              </div>
            ) : (
              <span style={styles.emptyHist}>Nenhuma consulta gravada no histórico.</span>
            )}
          </div>
        )}
      </div>

      {/* Extensibility & Developer Guide */}
      <div style={styles.sectionCard}>
        <div style={styles.cardHeader}>
          <BookOpen size={18} color="#00e5ff" />
          <h3 style={styles.cardTitle}>Guia do Desenvolvedor: Adicionar Novos Adaptadores e Módulos</h3>
        </div>
        <p style={styles.sectionDesc}>
          A arquitetura do <strong>OSINT Brazuca Ultimate</strong> é modular e baseada no padrão Strategy (<code>BaseAdapter</code>). Para plugar uma nova fonte pública:
        </p>
        <div className="terminal-box" style={{ marginTop: '10px' }}>
          <pre>{`// 1. Crie o arquivo em backend/app/adapters/{categoria}/{nome_fonte}.py
class MeuNovoAdapter(BaseAdapter):
    adapter_id = "meu_novo_adapter"
    name = "Nome Oficial da Fonte"
    category = "cnpj" // ou cpf, dominio, ip, etc.
    description = "Descrição clara dos dados fornecidos."
    official_url = "https://fonte.gov.br"
    supported_inputs = ["cnpj"]

    async def run(self, target: str, context: dict = None) -> SourceExecutionResult:
        // Use self.get_client() para requisições seguras com timeout e headers
        async with self.get_client() as client:
            resp = await client.get(f"https://api.fonte.gov.br/{target}")
            // Normalize os dados e retorne SourceExecutionResult
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                data=normalized_data,
                verification_url=self.official_url
            )

// 2. Registre a classe em backend/app/engine/orchestrator.py
// Pronto! A nova fonte será automaticamente executada e exibida no dashboard.`}</pre>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px 30px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  header: {
    marginBottom: '8px',
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
  msgBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#0c2612',
    border: '1px solid #00ff66',
    borderRadius: '6px',
    padding: '10px 14px',
    color: '#a3f7bf',
    fontSize: '13px',
  },
  manifestoCard: {
    backgroundColor: '#0d1017',
    border: '1px solid #3d0c11',
    borderRadius: '8px',
    padding: '20px',
  },
  sectionCard: {
    backgroundColor: '#0d1017',
    border: '1px solid #1c2230',
    borderRadius: '8px',
    padding: '20px',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '12px',
  },
  cardTitle: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#ffffff',
  },
  manifestoText: {
    fontSize: '13px',
    color: '#c9d1d9',
    lineHeight: '1.6',
    marginBottom: '12px',
  },
  manifestoList: {
    marginLeft: '20px',
    fontSize: '13px',
    color: '#a0a8b9',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    lineHeight: '1.5',
  },
  sectionDesc: {
    fontSize: '13px',
    color: '#8b92a2',
    lineHeight: '1.5',
    marginBottom: '14px',
  },
  toggleRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#07080b',
    padding: '12px 16px',
    borderRadius: '6px',
    border: '1px solid #1a1e28',
  },
  toggleInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    fontSize: '13px',
    color: '#ffffff',
  },
  toggleSub: {
    fontSize: '11px',
    color: '#8b92a2',
  },
  btnGroup: {
    display: 'flex',
    gap: '6px',
  },
  toggleBtn: {
    backgroundColor: '#12151e',
    border: '1px solid #202636',
    color: '#8890a4',
    padding: '6px 14px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 600,
  },
  toggleBtnActive: {
    backgroundColor: '#260609',
    borderColor: '#e50914',
    color: '#ffffff',
  },
  historyListArea: {
    marginTop: '16px',
    borderTop: '1px solid #1a1e28',
    paddingTop: '12px',
  },
  historyListHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '12px',
    color: '#8b92a2',
    marginBottom: '8px',
  },
  clearBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#ff6666',
    fontSize: '11px',
    fontWeight: 600,
  },
  historyTable: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  historyRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    backgroundColor: '#07080a',
    padding: '8px 12px',
    borderRadius: '4px',
    border: '1px solid #161a24',
    fontSize: '12px',
  },
  histCat: {
    color: '#00e5ff',
    fontFamily: 'monospace',
    fontSize: '11px',
  },
  histTarget: {
    color: '#ffffff',
    fontFamily: 'monospace',
  },
  histDate: {
    marginLeft: 'auto',
    color: '#6e7687',
    fontSize: '11px',
  },
  emptyHist: {
    fontSize: '12px',
    color: '#555d71',
    fontStyle: 'italic',
  },
};
