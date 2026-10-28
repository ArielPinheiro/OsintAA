import type {
  CategoryInfo,
  FutureModule,
  CatalogSource,
  CatalogStats,
  QueryResponse,
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Falha ao conectar com o backend.');
  return res.json();
}

export async function fetchCategories(): Promise<{
  core_categories: CategoryInfo[];
  future_modules: FutureModule[];
}> {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('Falha ao carregar categorias.');
  return res.json();
}

export async function fetchCatalog(params: {
  q?: string;
  categoria_id?: string;
  input_type?: string;
  tipo_fonte?: string;
  integration_type?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total_returned: number; sources: CatalogSource[] }> {
  const query = new URLSearchParams();
  if (params.q) query.set('q', params.q);
  if (params.categoria_id) query.set('categoria_id', params.categoria_id);
  if (params.input_type) query.set('input_type', params.input_type);
  if (params.tipo_fonte) query.set('tipo_fonte', params.tipo_fonte);
  if (params.integration_type) query.set('integration_type', params.integration_type);
  if (params.limit) query.set('limit', String(params.limit));
  if (params.offset) query.set('offset', String(params.offset));

  const res = await fetch(`${API_BASE}/catalog?${query.toString()}`);
  if (!res.ok) throw new Error('Falha ao carregar catálogo.');
  return res.json();
}

export async function fetchCatalogStats(): Promise<CatalogStats> {
  const res = await fetch(`${API_BASE}/catalog/stats`);
  if (!res.ok) throw new Error('Falha ao obter estatísticas do catálogo.');
  return res.json();
}

export async function runQuery(
  category: string,
  target: string,
  sourceIds?: string[],
  saveHistory: boolean = false
): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      category,
      target,
      source_ids: sourceIds,
      save_history: saveHistory,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Erro na execução da consulta.');
  }
  return res.json();
}

export async function runFileUpload(file: File): Promise<QueryResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/query/file`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Falha ao processar arquivo.');
  }
  return res.json();
}

export async function downloadReport(
  response: QueryResponse,
  format: 'json' | 'csv' | 'html'
): Promise<void> {
  const res = await fetch(`${API_BASE}/report/export?format=${format}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(response),
  });
  if (!res.ok) throw new Error('Falha ao gerar relatório.');

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `dossie_osint_${response.category}_${response.query_id.slice(0, 8)}.${format}`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function fetchHistory(): Promise<{ enabled: boolean; history: any[] }> {
  const res = await fetch(`${API_BASE}/history`);
  if (!res.ok) throw new Error('Falha ao obter histórico.');
  return res.json();
}

export async function toggleHistory(enabled: boolean): Promise<{ enabled: boolean }> {
  const formData = new FormData();
  formData.append('enabled', String(enabled));
  const res = await fetch(`${API_BASE}/history/toggle`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Falha ao alterar preferência de histórico.');
  return res.json();
}

export async function clearHistory(): Promise<void> {
  await fetch(`${API_BASE}/history`, { method: 'DELETE' });
}
