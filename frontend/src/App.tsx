import React, { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { InvestigationPanel } from './components/InvestigationPanel';
import { CatalogExplorer } from './components/CatalogExplorer';
import { RelationshipGraph } from './components/RelationshipGraph';
import { SettingsView } from './components/SettingsModal';
import type { CategoryInfo } from './types';
import { fetchCategories, fetchCatalogStats, fetchHealth } from './services/api';

export function App() {
  const [currentView, setCurrentView] = useState<'investigation' | 'catalog' | 'graph' | 'settings'>('investigation');
  const [selectedCategory, setSelectedCategory] = useState<string>('cnpj');
  const [categories, setCategories] = useState<CategoryInfo[]>([]);
  const [totalCatalogSources, setTotalCatalogSources] = useState<number>(515);
  const [historyEnabled, setHistoryEnabled] = useState<boolean>(false);
  const [backendOnline, setBackendOnline] = useState<boolean>(true);

  useEffect(() => {
    const initApp = async () => {
      try {
        const [healthRes, catRes, statsRes] = await Promise.all([
          fetchHealth().catch(() => null),
          fetchCategories().catch(() => null),
          fetchCatalogStats().catch(() => null),
        ]);

        if (healthRes) {
          setBackendOnline(true);
          setHistoryEnabled(healthRes.history_enabled);
        } else {
          setBackendOnline(false);
        }

        if (catRes && catRes.core_categories) {
          setCategories(catRes.core_categories);
        }

        if (statsRes && statsRes.total_sources) {
          setTotalCatalogSources(statsRes.total_sources);
        }
      } catch (err) {
        console.error('Falha na inicialização:', err);
      }
    };

    initApp();
  }, []);

  return (
    <div style={styles.appContainer}>
      <Sidebar
        currentView={currentView}
        onSelectView={setCurrentView}
        selectedCategory={selectedCategory}
        onSelectCategory={(catId) => {
          setSelectedCategory(catId);
          setCurrentView('investigation');
        }}
        categories={categories}
        totalCatalogSources={totalCatalogSources}
        historyEnabled={historyEnabled}
      />

      <main style={styles.mainContent}>
        {/* Top Operational Status Header */}
        <header style={styles.topBar}>
          <div style={styles.topBarLeft}>
            <span style={styles.breadcrumbView}>
              VISÃO ATIVA: <strong>{currentView.toUpperCase()}</strong>
            </span>
            {currentView === 'investigation' && (
              <span style={styles.breadcrumbCategory}>
                / {selectedCategory.toUpperCase()}
              </span>
            )}
          </div>

          <div style={styles.topBarRight}>
            <div style={styles.healthBadge}>
              <span
                style={{
                  ...styles.healthDot,
                  backgroundColor: backendOnline ? '#00ff66' : '#ff3333',
                  boxShadow: backendOnline ? '0 0 8px #00ff66' : '0 0 8px #ff3333',
                }}
              ></span>
              <span style={styles.healthText}>
                {backendOnline ? 'BACKEND CONECTADO' : 'BACKEND DESCONECTADO (Inicie na porta 8000)'}
              </span>
            </div>

            <div style={styles.privacyShieldPill}>
              <span>LGPD & PRIVACIDADE: ATIVO</span>
            </div>
          </div>
        </header>

        {/* View Switcher */}
        <div style={styles.viewContainer}>
          {currentView === 'investigation' && (
            <InvestigationPanel
              selectedCategory={selectedCategory}
              categories={categories}
              historyEnabled={historyEnabled}
            />
          )}

          {currentView === 'catalog' && <CatalogExplorer />}

          {currentView === 'graph' && <RelationshipGraph />}

          {currentView === 'settings' && (
            <SettingsView
              historyEnabled={historyEnabled}
              onUpdateHistoryEnabled={setHistoryEnabled}
            />
          )}
        </div>
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  appContainer: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    backgroundColor: '#07080b',
    overflow: 'hidden',
  },
  mainContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    backgroundColor: '#0a0c10',
  },
  topBar: {
    height: '46px',
    backgroundColor: '#07080a',
    borderBottom: '1px solid #1f0b0e',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    flexShrink: 0,
  },
  topBarLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '11px',
    color: '#8b92a2',
    fontFamily: 'monospace',
  },
  breadcrumbView: {
    letterSpacing: '0.5px',
  },
  breadcrumbCategory: {
    color: '#ff4d4d',
    fontWeight: 700,
  },
  topBarRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
  },
  healthBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '11px',
    fontFamily: 'monospace',
  },
  healthDot: {
    width: '7px',
    height: '7px',
    borderRadius: '50%',
  },
  healthText: {
    color: '#a0a8b9',
  },
  privacyShieldPill: {
    backgroundColor: '#1b090b',
    border: '1px solid #8b0000',
    color: '#ff6666',
    fontSize: '10px',
    fontWeight: 700,
    padding: '3px 8px',
    borderRadius: '4px',
    fontFamily: 'monospace',
    letterSpacing: '0.5px',
  },
  viewContainer: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
};

export default App;
