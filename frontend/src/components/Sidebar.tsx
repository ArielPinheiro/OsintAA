import React from 'react';
import {
  Crosshair,
  Database,
  Share2,
  ShieldCheck,
  Building2,
  UserCheck,
  Globe,
  Radio,
  Phone,
  Mail,
  User,
  FileCode,
  Landmark,
  Layers,
  Lock,
} from 'lucide-react';
import type { CategoryInfo } from '../types';

interface SidebarProps {
  currentView: 'investigation' | 'catalog' | 'graph' | 'settings';
  onSelectView: (view: 'investigation' | 'catalog' | 'graph' | 'settings') => void;
  selectedCategory: string;
  onSelectCategory: (catId: string) => void;
  categories: CategoryInfo[];
  totalCatalogSources: number;
  historyEnabled: boolean;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  cnpj: <Building2 size={16} />,
  cpf: <UserCheck size={16} />,
  dominio: <Globe size={16} />,
  ip: <Radio size={16} />,
  telefone: <Phone size={16} />,
  email: <Mail size={16} />,
  username: <User size={16} />,
  documentos: <FileCode size={16} />,
  dados_publicos: <Landmark size={16} />,
};

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onSelectView,
  selectedCategory,
  onSelectCategory,
  categories,
  totalCatalogSources,
  historyEnabled,
}) => {
  return (
    <aside style={styles.sidebar}>
      {/* Brand Header */}
      <div style={styles.brandBox}>
        <div style={styles.brandTitleRow}>
          <div style={styles.logoBadge}>⚡</div>
          <div>
            <h1 style={styles.brandName}>OSINT BRAZUCA</h1>
            <span style={styles.brandSub}>ULTIMATE EDITION</span>
          </div>
        </div>
      </div>

      {/* Main Views Navigation */}
      <div style={styles.navSection}>
        <span style={styles.sectionLabel}>MODOS OPERACIONAIS</span>
        <button
          style={{
            ...styles.navBtn,
            ...(currentView === 'investigation' ? styles.navBtnActive : {}),
          }}
          onClick={() => onSelectView('investigation')}
        >
          <Crosshair size={18} color={currentView === 'investigation' ? '#ff3333' : '#8890a4'} />
          <span>Central de Investigação</span>
        </button>

        <button
          style={{
            ...styles.navBtn,
            ...(currentView === 'catalog' ? styles.navBtnActive : {}),
          }}
          onClick={() => onSelectView('catalog')}
        >
          <Database size={18} color={currentView === 'catalog' ? '#ff3333' : '#8890a4'} />
          <span>Catálogo de Fontes</span>
          <span style={styles.counterBadge}>{totalCatalogSources || '515+'}</span>
        </button>

        <button
          style={{
            ...styles.navBtn,
            ...(currentView === 'graph' ? styles.navBtnActive : {}),
          }}
          onClick={() => onSelectView('graph')}
        >
          <Share2 size={18} color={currentView === 'graph' ? '#ff3333' : '#8890a4'} />
          <span>Grafo & Relações</span>
        </button>

        <button
          style={{
            ...styles.navBtn,
            ...(currentView === 'settings' ? styles.navBtnActive : {}),
          }}
          onClick={() => onSelectView('settings')}
        >
          <ShieldCheck size={18} color={currentView === 'settings' ? '#ff3333' : '#8890a4'} />
          <span>Privacidade & Config</span>
        </button>
      </div>

      {/* Categories Selector */}
      <div style={{ ...styles.navSection, flex: 1, overflowY: 'auto' }}>
        <span style={styles.sectionLabel}>VETORES DE CONSULTA</span>
        {categories.map((cat) => {
          const isSelected = selectedCategory === cat.id && currentView === 'investigation';
          return (
            <button
              key={cat.id}
              style={{
                ...styles.categoryBtn,
                ...(isSelected ? styles.categoryBtnActive : {}),
              }}
              onClick={() => {
                onSelectCategory(cat.id);
                if (currentView !== 'investigation') {
                  onSelectView('investigation');
                }
              }}
            >
              <span style={{ color: isSelected ? '#ff3333' : '#8890a4' }}>
                {CATEGORY_ICONS[cat.id] || <Layers size={16} />}
              </span>
              <span style={styles.categoryName}>{cat.name}</span>
              {cat.badge && (
                <span
                  style={{
                    ...styles.catBadge,
                    ...(isSelected ? styles.catBadgeActive : {}),
                  }}
                >
                  {cat.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Privacy Info */}
      <div style={styles.footerInfo}>
        <div style={styles.statusRow}>
          <span style={styles.statusDot}></span>
          <span style={styles.statusText}>127.0.0.1 (Local Only)</span>
        </div>
        <div style={styles.statusRow}>
          <Lock size={12} color={historyEnabled ? '#ffaa00' : '#00ff66'} />
          <span style={styles.statusText}>
            Histórico: {historyEnabled ? 'Ativado' : 'Desligado (Padrão Seguro)'}
          </span>
        </div>
      </div>
    </aside>
  );
};

const styles: Record<string, React.CSSProperties> = {
  sidebar: {
    width: '270px',
    backgroundColor: '#0a0c10',
    borderRight: '1px solid #230b0e',
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    userSelect: 'none',
  },
  brandBox: {
    padding: '20px 18px',
    borderBottom: '1px solid #1f0b0e',
    backgroundColor: '#07080a',
  },
  brandTitleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logoBadge: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    backgroundColor: '#260609',
    border: '1px solid #e50914',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '18px',
    color: '#ff2a2a',
    boxShadow: '0 0 10px rgba(229, 9, 20, 0.3)',
  },
  brandName: {
    fontSize: '15px',
    fontWeight: 800,
    color: '#ffffff',
    letterSpacing: '1px',
    lineHeight: '1.2',
  },
  brandSub: {
    fontSize: '10px',
    fontWeight: 700,
    color: '#e50914',
    letterSpacing: '1.5px',
    fontFamily: 'monospace',
  },
  navSection: {
    padding: '16px 14px',
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  sectionLabel: {
    fontSize: '10px',
    fontWeight: 700,
    color: '#555d71',
    letterSpacing: '1px',
    padding: '0 8px 6px 8px',
  },
  navBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '10px 12px',
    borderRadius: '6px',
    backgroundColor: 'transparent',
    border: '1px solid transparent',
    color: '#c9d1d9',
    fontSize: '13px',
    fontWeight: 600,
    textAlign: 'left',
    transition: 'all 0.15s ease',
  },
  navBtnActive: {
    backgroundColor: '#1d080b',
    border: '1px solid #8b0000',
    color: '#ffffff',
    boxShadow: '0 0 8px rgba(229, 9, 20, 0.15)',
  },
  counterBadge: {
    marginLeft: 'auto',
    backgroundColor: '#1b202c',
    color: '#8b92a2',
    fontSize: '10px',
    fontWeight: 700,
    padding: '2px 6px',
    borderRadius: '10px',
  },
  categoryBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px 10px',
    borderRadius: '6px',
    backgroundColor: 'transparent',
    border: '1px solid transparent',
    color: '#8890a4',
    fontSize: '12px',
    fontWeight: 500,
    textAlign: 'left',
  },
  categoryBtnActive: {
    backgroundColor: '#150608',
    border: '1px solid #5a090e',
    color: '#ffffff',
    fontWeight: 600,
  },
  categoryName: {
    flex: 1,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  catBadge: {
    fontSize: '9px',
    padding: '1px 5px',
    borderRadius: '4px',
    backgroundColor: '#141822',
    color: '#5d667c',
    fontFamily: 'monospace',
  },
  catBadgeActive: {
    backgroundColor: '#300a0e',
    color: '#ff8080',
    border: '1px solid #8b0000',
  },
  footerInfo: {
    padding: '14px 16px',
    backgroundColor: '#060709',
    borderTop: '1px solid #1a080a',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  statusRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  statusDot: {
    width: '7px',
    height: '7px',
    borderRadius: '50%',
    backgroundColor: '#00ff66',
    boxShadow: '0 0 6px #00ff66',
  },
  statusText: {
    fontSize: '11px',
    color: '#70778a',
    fontFamily: 'monospace',
  },
};
