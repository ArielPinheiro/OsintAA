import React, { useState } from 'react';

interface Node {
  id: string;
  label: string;
  type: 'target' | 'entity' | 'partner' | 'domain' | 'subdomain' | 'ip' | 'source';
  details?: string;
  x: number;
  y: number;
}

interface Edge {
  from: string;
  to: string;
  label: string;
}

export const RelationshipGraph: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Exemplo de grafo investigativo representativo com conexões reais
  const nodes: Node[] = [
    { id: '1', label: 'ALVO PRINCIPAL', type: 'target', details: 'Empresa Investigada (CNPJ Matriz)', x: 400, y: 220 },
    { id: '2', label: 'Diretor Presidente', type: 'partner', details: 'Sócio-Administrador no QSA Oficial da Receita', x: 220, y: 100 },
    { id: '3', label: 'Diretor Financeiro', type: 'partner', details: 'Sócio com participação de capital no QSA', x: 200, y: 340 },
    { id: '4', label: 'dominio.com.br', type: 'domain', details: 'Registro RDAP no Registro.br com DNS ativo', x: 600, y: 120 },
    { id: '5', label: 'api.dominio.com.br', type: 'subdomain', details: 'Certificado TLS descoberto via crt.sh CT', x: 740, y: 60 },
    { id: '6', label: 'mail.dominio.com.br', type: 'subdomain', details: 'Servidor MX apontado no registro DNS oficial', x: 750, y: 190 },
    { id: '7', label: '200.160.2.3 (IP)', type: 'ip', details: 'Bloco IPv4 alocado ao AS25820', x: 580, y: 340 },
    { id: '8', label: 'Portal Transparência', type: 'source', details: 'Contratos e licitações públicas federais', x: 380, y: 400 },
  ];

  const edges: Edge[] = [
    { from: '1', to: '2', label: 'Quadro Societário (QSA)' },
    { from: '1', to: '3', label: 'Quadro Societário (QSA)' },
    { from: '1', to: '4', label: 'Domínio Titular' },
    { from: '4', to: '5', label: 'Subdomínio (CT)' },
    { from: '4', to: '6', label: 'Registro MX' },
    { from: '4', to: '7', label: 'Resolução DNS A' },
    { from: '1', to: '8', label: 'Cruzamento PNCP' },
  ];

  const getNodeColor = (type: Node['type']) => {
    switch (type) {
      case 'target': return '#e50914';
      case 'partner': return '#ffaa00';
      case 'domain': return '#00e5ff';
      case 'subdomain': return '#00ff66';
      case 'ip': return '#b366ff';
      case 'source': return '#ff3366';
      default: return '#8890a4';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>Visualizador de Grafo & Relacionamentos OSINT</h2>
          <p style={styles.sub}>
            Representação vetorial de entidades, vínculos societários (QSA), infraestrutura digital e cruzamentos públicos.
          </p>
        </div>
        <div style={styles.legend}>
          <div style={styles.legendItem}><span style={{ ...styles.legendDot, backgroundColor: '#e50914' }}></span> Alvo Principal</div>
          <div style={styles.legendItem}><span style={{ ...styles.legendDot, backgroundColor: '#ffaa00' }}></span> Sócios / QSA</div>
          <div style={styles.legendItem}><span style={{ ...styles.legendDot, backgroundColor: '#00e5ff' }}></span> Domínio RDAP</div>
          <div style={styles.legendItem}><span style={{ ...styles.legendDot, backgroundColor: '#00ff66' }}></span> Subdomínio CT</div>
          <div style={styles.legendItem}><span style={{ ...styles.legendDot, backgroundColor: '#b366ff' }}></span> IP / BGP</div>
        </div>
      </div>

      <div style={styles.canvasCard}>
        <svg style={styles.svg}>
          {/* Edges */}
          {edges.map((e, idx) => {
            const n1 = nodes.find((n) => n.id === e.from);
            const n2 = nodes.find((n) => n.id === e.to);
            if (!n1 || !n2) return null;
            return (
              <g key={idx}>
                <line
                  x1={n1.x}
                  y1={n1.y}
                  x2={n2.x}
                  y2={n2.y}
                  stroke="#280f14"
                  strokeWidth="2"
                  strokeDasharray={e.label.includes('CT') ? '4' : 'none'}
                />
                <text
                  x={(n1.x + n2.x) / 2}
                  y={(n1.y + n2.y) / 2 - 6}
                  fill="#5d667c"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {e.label}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {nodes.map((n) => {
            const isSelected = selectedNode?.id === n.id;
            const color = getNodeColor(n.type);
            return (
              <g
                key={n.id}
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedNode(n)}
              >
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={n.type === 'target' ? 24 : 18}
                  fill="#0a0c12"
                  stroke={color}
                  strokeWidth={isSelected ? 4 : 2}
                  filter={isSelected ? 'drop-shadow(0 0 8px rgba(229,9,20,0.6))' : 'none'}
                />
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={n.type === 'target' ? 8 : 5}
                  fill={color}
                />
                <text
                  x={n.x}
                  y={n.y + (n.type === 'target' ? 38 : 32)}
                  fill={isSelected ? '#ffffff' : '#c9d1d9'}
                  fontSize={n.type === 'target' ? 12 : 11}
                  fontWeight={isSelected || n.type === 'target' ? 'bold' : 'normal'}
                  fontFamily="sans-serif"
                  textAnchor="middle"
                >
                  {n.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div style={styles.nodeDetailsBox}>
            <div style={styles.detailHeader}>
              <span style={{ color: getNodeColor(selectedNode.type), fontWeight: 700 }}>
                ● {selectedNode.type.toUpperCase()}
              </span>
              <button style={styles.closeBtn} onClick={() => setSelectedNode(null)}>✕</button>
            </div>
            <h4 style={styles.nodeDetailTitle}>{selectedNode.label}</h4>
            <p style={styles.nodeDetailText}>{selectedNode.details}</p>
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
  legend: {
    display: 'flex',
    gap: '14px',
    backgroundColor: '#0c0e14',
    border: '1px solid #1c2230',
    padding: '8px 14px',
    borderRadius: '6px',
    fontSize: '11px',
    color: '#c9d1d9',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  legendDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  canvasCard: {
    backgroundColor: '#08090d',
    border: '1px solid #230b0f',
    borderRadius: '8px',
    height: '560px',
    position: 'relative',
    overflow: 'hidden',
    boxShadow: '0 4px 20px rgba(0,0,0,0.6)',
  },
  svg: {
    width: '100%',
    height: '100%',
  },
  nodeDetailsBox: {
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    width: '280px',
    backgroundColor: '#0f121a',
    border: '1px solid #283042',
    borderRadius: '6px',
    padding: '14px',
    boxShadow: '0 8px 24px rgba(0,0,0,0.7)',
  },
  detailHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '11px',
    marginBottom: '8px',
  },
  closeBtn: {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#8b92a2',
    fontSize: '12px',
  },
  nodeDetailTitle: {
    fontSize: '15px',
    color: '#ffffff',
    fontWeight: 700,
    marginBottom: '4px',
  },
  nodeDetailText: {
    fontSize: '12px',
    color: '#8b92a2',
    lineHeight: '1.4',
  },
};
