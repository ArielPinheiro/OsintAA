import csv
import io
import json
from typing import Any, Dict
from ..engine.models import QueryResponse

def export_to_json(response: QueryResponse) -> str:
    """Exporta dossiê completo de investigação em JSON limpo e estruturado."""
    # Preserva o mascaramento no dump JSON
    data = response.model_dump()
    data.pop("target_raw", None)  # NUNCA expor target_raw desnecessário no relatório
    return json.dumps(data, ensure_ascii=False, indent=2)

def export_to_csv(response: QueryResponse) -> str:
    """Exporta resumo tabular das fontes consultadas em formato CSV."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Cabeçalho
    writer.writerow([
        "ID_Consulta",
        "Categoria",
        "Alvo_Mascarado",
        "Data_Hora_UTC",
        "Fonte_ID",
        "Fonte_Nome",
        "Status",
        "Tempo_Execucao_ms",
        "URL_Verificacao",
        "Confianca",
        "Erro_Indisponibilidade",
        "Resumo_Dados"
    ])

    for res in response.results:
        dados_resumo = ""
        if res.data:
            # Amostra resumida em formato chave-valor simples
            chaves = list(res.data.keys())[:5]
            dados_resumo = "; ".join(f"{k}: {res.data[k]}" for k in chaves)

        writer.writerow([
            response.query_id,
            response.category,
            response.target_masked,
            res.timestamp,
            res.source_id,
            res.source_name,
            res.status.value,
            res.execution_time_ms,
            res.verification_url or "",
            res.confidence.value,
            res.error_message or "",
            dados_resumo[:200]
        ])

    return output.getvalue()

def export_to_html(response: QueryResponse) -> str:
    """Exporta dossiê pericial em HTML com estética escura de investigação (OSINT Brazuca Ultimate)."""
    results_html = []

    for r in response.results:
        status_color = "#00ff66" if r.status.value == "confirmado" else (
            "#ffaa00" if r.status.value in ("parcial", "nao_confirmado", "etapa_manual_necessaria") else "#ff3333"
        )
        
        data_block = ""
        if r.data:
            data_block = f"""
            <div class="data-block">
                <pre>{json.dumps(r.data, ensure_ascii=False, indent=2)}</pre>
            </div>
            """

        error_block = ""
        if r.error_message:
            error_block = f"""
            <div class="error-notice">
                <strong>Alerta / Motivo:</strong> {r.error_message}
            </div>
            """

        limitations_block = ""
        if r.limitations:
            lims = "".join(f"<li>{l}</li>" for l in r.limitations)
            limitations_block = f"""
            <div class="limitations-box">
                <span class="sub-label">Limitações Legais / Técnicas:</span>
                <ul>{lims}</ul>
            </div>
            """

        verification_btn = ""
        if r.verification_url:
            verification_btn = f"""
            <a href="{r.verification_url}" target="_blank" class="verify-link">
                ↗ Acessar Fonte Original
            </a>
            """

        card = f"""
        <div class="source-card">
            <div class="source-header">
                <div>
                    <h3 class="source-title">{r.source_name}</h3>
                    <span class="source-meta">ID: {r.source_id} | Categoria: {r.category} | Tempo: {r.execution_time_ms}ms</span>
                </div>
                <div class="status-badge" style="border-color: {status_color}; color: {status_color};">
                    ● {r.status.value.upper()}
                </div>
            </div>
            {error_block}
            {data_block}
            {limitations_block}
            <div class="source-footer">
                <span class="conf-badge">Nível de Confiança: {r.confidence.value.upper()}</span>
                {verification_btn}
            </div>
        </div>
        """
        results_html.append(card)

    cards_joined = "\n".join(results_html)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dossiê OSINT Brazuca Ultimate - {response.target_masked}</title>
    <style>
        :root {{
            --bg-dark: #08090c;
            --bg-card: #101218;
            --border-red: #3a1014;
            --red-accent: #e50914;
            --red-glow: rgba(229, 9, 20, 0.2);
            --text-main: #e2e4e9;
            --text-dim: #8b92a2;
            --code-bg: #050608;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-dark);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            line-height: 1.6;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            border-bottom: 2px solid var(--border-red);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .brand {{
            font-size: 26px;
            font-weight: 800;
            color: var(--red-accent);
            letter-spacing: 1px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .dossier-tag {{
            font-size: 11px;
            background: #20080a;
            border: 1px solid var(--red-accent);
            color: #ff6666;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-red);
            padding: 16px;
            border-radius: 8px;
        }}
        .meta-item .label {{
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.5px;
        }}
        .meta-item .val {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text-main);
            font-family: monospace;
        }}
        .summary-banner {{
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .summary-pill {{
            background: #141720;
            border: 1px solid #232736;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
        }}
        .summary-pill strong {{ color: var(--red-accent); }}
        .source-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-red);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.4);
        }}
        .source-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid #1a1e28;
            padding-bottom: 12px;
            margin-bottom: 14px;
        }}
        .source-title {{
            font-size: 17px;
            font-weight: 700;
            color: #ffffff;
        }}
        .source-meta {{
            font-size: 12px;
            color: var(--text-dim);
            font-family: monospace;
        }}
        .status-badge {{
            font-size: 11px;
            font-weight: 700;
            border: 1px solid;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: monospace;
            letter-spacing: 0.5px;
        }}
        .data-block {{
            background: var(--code-bg);
            border: 1px solid #1b1e2a;
            border-radius: 6px;
            padding: 12px;
            overflow-x: auto;
            margin: 12px 0;
        }}
        pre {{
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
            color: #c9d1d9;
        }}
        .error-notice {{
            background: #250b0f;
            border-left: 3px solid var(--red-accent);
            padding: 10px 14px;
            font-size: 13px;
            margin: 10px 0;
            color: #ff9999;
        }}
        .limitations-box {{
            background: #0d0f14;
            padding: 10px 14px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 12px;
            color: var(--text-dim);
        }}
        .limitations-box ul {{
            margin-left: 18px;
            margin-top: 5px;
        }}
        .source-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 14px;
            padding-top: 10px;
            border-top: 1px solid #181c26;
        }}
        .conf-badge {{
            font-size: 11px;
            color: var(--text-dim);
            text-transform: uppercase;
        }}
        .verify-link {{
            color: #ff4d4d;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
        }}
        .verify-link:hover {{ text-decoration: underline; }}
        .legal-notice {{
            margin-top: 40px;
            padding: 20px;
            background: #0a0b0e;
            border: 1px dashed var(--border-red);
            border-radius: 8px;
            font-size: 12px;
            color: #727a8c;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="brand">
                <span>⚡ OSINT Brazuca Ultimate</span>
                <span class="dossier-tag">DOSSIÊ PERICIAL</span>
            </div>
            <div class="meta-grid">
                <div class="meta-item">
                    <div class="label">ID da Investigação</div>
                    <div class="val">{response.query_id[:16]}...</div>
                </div>
                <div class="meta-item">
                    <div class="label">Categoria</div>
                    <div class="val">{response.category.upper()}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Alvo Pesquisado (Protegido)</div>
                    <div class="val">{response.target_masked}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Data / Hora (UTC)</div>
                    <div class="val">{response.started_at[:19].replace('T', ' ')}</div>
                </div>
            </div>
            <div class="summary-banner">
                <div class="summary-pill">Fontes: <strong>{response.summary.total_sources}</strong></div>
                <div class="summary-pill">Concluídas: <strong>{response.summary.completed}</strong></div>
                <div class="summary-pill">Parciais: <strong>{response.summary.partial}</strong></div>
                <div class="summary-pill">Indisponíveis: <strong>{response.summary.unavailable}</strong></div>
                <div class="summary-pill">Falhas: <strong>{response.summary.failed}</strong></div>
                <div class="summary-pill">Duração: <strong>{response.duration_seconds}s</strong></div>
            </div>
        </header>

        <main>
            {cards_joined}
        </main>

        <footer class="legal-notice">
            <strong>DECLARAÇÃO DE CONFORMIDADE E PRIVACIDADE:</strong> Este relatório foi gerado automaticamente pelo OSINT Brazuca Ultimate exclusivamente através de consultas legítimas a fontes públicas e bases autorizadas. Identificadores sensíveis foram mascarados nos termos da Lei Geral de Proteção de Dados (Lei 13.709/2018). As conclusões devem ser confirmadas na fonte original.
        </footer>
    </div>
</body>
</html>
"""
    return html_content

