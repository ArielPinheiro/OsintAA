export type ResultStatus = 
  | 'confirmado'
  | 'parcial'
  | 'nao_confirmado'
  | 'nao_encontrado'
  | 'erro'
  | 'indisponivel'
  | 'etapa_manual_necessaria';

export type ConfidenceLevel = 'alta' | 'media' | 'baixa' | 'informativo';

export interface SourceExecutionResult {
  source_id: string;
  source_name: string;
  category: string;
  status: ResultStatus;
  data?: Record<string, any> | null;
  timestamp: string;
  execution_time_ms: number;
  verification_url?: string | null;
  error_message?: string | null;
  limitations: string[];
  confidence: ConfidenceLevel;
  requires_manual_action?: boolean;
  action_url?: string | null;
}

export interface QuerySummary {
  total_sources: number;
  completed: number;
  partial: number;
  unavailable: number;
  failed: number;
  manual_steps: number;
}

export interface QueryResponse {
  query_id: string;
  category: string;
  target_raw: string;
  target_masked: string;
  started_at: string;
  finished_at: string;
  duration_seconds: number;
  summary: QuerySummary;
  results: SourceExecutionResult[];
}

export interface CategoryInfo {
  id: string;
  name: string;
  description: string;
  placeholder: string;
  implemented: boolean;
  badge?: string;
}

export interface FutureModule {
  id: string;
  name: string;
  description: string;
}

export interface SourceLink {
  label: string;
  url: string;
  uf?: string | null;
}

export interface CatalogSource {
  id: string;
  nome: string;
  categoria: string;
  categoria_id: string;
  descricao: string;
  tipo_fonte: string;
  classificacao: string;
  input: string[];
  output: string[];
  links: SourceLink[];
  integration_type: string;
  adapter_id?: string | null;
  manual_notice?: string | null;
  requires_auth: boolean;
  requires_captcha: boolean;
}

export interface CatalogStats {
  total_sources: number;
  total_links: number;
  categories_count: number;
  implemented_adapters_count: number;
  inputs_supported: string[];
  outputs_supported: string[];
}

