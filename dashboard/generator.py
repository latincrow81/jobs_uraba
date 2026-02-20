"""Generate a self-contained interactive HTML dashboard with Plotly charts."""

import json
import logging
from typing import List

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from data_schema import JobPosting

logger = logging.getLogger(__name__)

# ── Color palette ─────────────────────────────────────────────────
COLORS = {
    "primary": "#4f46e5",
    "secondary": "#7c3aed",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#dc2626",
    "info": "#0284c7",
}
PALETTE = px.colors.qualitative.Set2


class DashboardGenerator:
    def __init__(self, jobs: List[JobPosting]):
        self.jobs = jobs
        self.df = pd.DataFrame([j.to_dict() for j in jobs])

    # ── Stats ─────────────────────────────────────────────────────
    def _stats(self) -> dict:
        df = self.df
        avg_sal = None
        if not df.empty and "salary_min" in df.columns:
            sal_data = df.dropna(subset=["salary_min"])
            if not sal_data.empty:
                avg_sal = sal_data[["salary_min", "salary_max"]].mean().mean()

        return {
            "total_jobs": len(df),
            "zones": int(df["zone"].nunique()) if not df.empty else 0,
            "companies": int(df["company"].nunique()) if not df.empty else 0,
            "permanent": int((df["contract_type"] == "permanente").sum()) if not df.empty else 0,
            "temporal": int((df["contract_type"] == "temporal").sum()) if not df.empty else 0,
            "avg_salary": avg_sal,
            "sources": int(df["source"].nunique()) if not df.empty else 0,
        }

    # ── Charts ────────────────────────────────────────────────────
    def _chart_jobs_by_zone(self) -> str:
        counts = self.df["zone"].value_counts().head(15)
        fig = go.Figure(go.Bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            marker_color=COLORS["primary"],
        ))
        fig.update_layout(
            title="Empleos por Municipio / Zona",
            xaxis_title="Cantidad",
            yaxis_title="",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=40, b=30),
            height=400,
        )
        return fig.to_json()

    def _chart_contract_types(self) -> str:
        counts = self.df["contract_type"].value_counts()
        fig = go.Figure(go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.4,
            marker_colors=PALETTE,
        ))
        fig.update_layout(
            title="Tipo de Contrato",
            margin=dict(l=10, r=10, t=40, b=30),
            height=400,
        )
        return fig.to_json()

    def _chart_salary_distribution(self) -> str:
        sal = self.df.dropna(subset=["salary_max"])
        if sal.empty:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos de salario disponibles", showarrow=False)
            fig.update_layout(title="Distribución Salarial por Zona", height=400)
            return fig.to_json()

        fig = go.Figure()
        top_zones = sal["zone"].value_counts().head(8).index
        for zone in top_zones:
            zone_data = sal[sal["zone"] == zone]
            fig.add_trace(go.Box(
                y=zone_data["salary_max"],
                name=zone,
                boxmean="sd",
            ))
        fig.update_layout(
            title="Distribución Salarial por Zona (COP)",
            yaxis_title="Salario máximo (COP)",
            margin=dict(l=10, r=10, t=40, b=30),
            height=400,
            showlegend=False,
        )
        return fig.to_json()

    def _chart_sources(self) -> str:
        counts = self.df["source"].value_counts()
        fig = go.Figure(go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=PALETTE[:len(counts)],
        ))
        fig.update_layout(
            title="Empleos por Fuente",
            xaxis_title="Portal",
            yaxis_title="Cantidad",
            margin=dict(l=10, r=10, t=40, b=30),
            height=400,
        )
        return fig.to_json()

    def _chart_relevance(self) -> str:
        fig = go.Figure(go.Histogram(
            x=self.df["relevance_score"],
            nbinsx=10,
            marker_color=COLORS["secondary"],
        ))
        fig.update_layout(
            title="Distribución de Relevancia para Urabá",
            xaxis_title="Puntaje de Relevancia",
            yaxis_title="Cantidad",
            margin=dict(l=10, r=10, t=40, b=30),
            height=400,
        )
        return fig.to_json()

    def _chart_top_companies(self) -> str:
        counts = self.df["company"].value_counts().head(10)
        fig = go.Figure(go.Bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            marker_color=COLORS["info"],
        ))
        fig.update_layout(
            title="Top 10 Empresas con Más Vacantes",
            xaxis_title="Cantidad",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=40, b=30),
            height=400,
        )
        return fig.to_json()

    # ── HTML Generation ───────────────────────────────────────────
    def generate(self, output_path: str):
        """Build and write the complete dashboard HTML file."""
        stats = self._stats()
        charts = {
            "jobs_by_zone": self._chart_jobs_by_zone(),
            "contract_types": self._chart_contract_types(),
            "salary_distribution": self._chart_salary_distribution(),
            "sources": self._chart_sources(),
            "relevance": self._chart_relevance(),
            "top_companies": self._chart_top_companies(),
        }

        # Prepare table data (JSON-serializable)
        table_data = json.dumps(
            [j.to_dict() for j in self.jobs],
            ensure_ascii=False,
            default=str,
        )

        html = self._build_html(stats, charts, table_data)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("Dashboard written to %s", output_path)

    def _build_html(self, stats: dict, charts: dict, table_json: str) -> str:
        avg_sal_display = "N/A"
        if stats["avg_salary"]:
            avg_sal_display = f"${stats['avg_salary']:,.0f}"

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Urabá Job Market Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
.container {{ max-width: 1500px; margin: 0 auto; padding: 20px; }}

/* Header */
header {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    color: white; padding: 35px 30px; border-radius: 12px; margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
}}
header h1 {{ font-size: 2.2em; margin-bottom: 6px; }}
header .subtitle {{ opacity: 0.9; font-size: 1em; }}
header .meta {{ margin-top: 12px; display: flex; gap: 20px; font-size: 0.9em; opacity: 0.85; }}

/* Stats */
.stats-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px; margin-bottom: 25px;
}}
.stat-card {{
    background: white; padding: 20px; border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06); text-align: center;
    transition: transform 0.2s;
}}
.stat-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
.stat-card .label {{ font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280; margin-bottom: 8px; }}
.stat-card .value {{ font-size: 2em; font-weight: 700; color: #4f46e5; }}

/* Charts */
.charts-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 20px; margin-bottom: 25px;
}}
.chart-box {{
    background: white; padding: 15px; border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}}

/* Filters */
.filters {{
    background: white; padding: 18px 20px; border-radius: 10px;
    margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}}
.filter-row {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }}
.filter-group {{ display: flex; flex-direction: column; gap: 4px; }}
.filter-group label {{ font-size: 0.8em; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.3px; }}
.filter-group select, .filter-group input {{
    padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9em; min-width: 160px; background: white;
}}
.filter-group select:focus, .filter-group input:focus {{ outline: none; border-color: #4f46e5; box-shadow: 0 0 0 2px rgba(79,70,229,0.15); }}
.btn {{
    padding: 8px 18px; border: none; border-radius: 6px; cursor: pointer;
    font-weight: 600; font-size: 0.9em; transition: all 0.2s;
}}
.btn-primary {{ background: #4f46e5; color: white; }}
.btn-primary:hover {{ background: #4338ca; }}
.btn-outline {{ background: white; color: #4f46e5; border: 1px solid #4f46e5; }}
.btn-outline:hover {{ background: #f5f3ff; }}

/* Table */
.table-wrapper {{
    background: white; border-radius: 10px; overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}}
.table-header {{ padding: 15px 20px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
.table-header h2 {{ font-size: 1.1em; color: #1f2937; }}
.table-header .count {{ font-size: 0.9em; color: #6b7280; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.88em; }}
th {{
    background: #f9fafb; padding: 12px 14px; text-align: left; font-weight: 600;
    color: #374151; border-bottom: 2px solid #e5e7eb; cursor: pointer; white-space: nowrap;
    user-select: none;
}}
th:hover {{ background: #f3f4f6; }}
th .arrow {{ font-size: 0.7em; margin-left: 4px; opacity: 0.4; }}
th.sorted .arrow {{ opacity: 1; color: #4f46e5; }}
td {{ padding: 10px 14px; border-bottom: 1px solid #f3f4f6; }}
tr:hover {{ background: #faf5ff; }}
.badge {{
    display: inline-block; padding: 3px 8px; border-radius: 4px;
    font-size: 0.8em; font-weight: 600;
}}
.badge-high {{ background: #d1fae5; color: #065f46; }}
.badge-medium {{ background: #fef3c7; color: #92400e; }}
.badge-low {{ background: #fee2e2; color: #991b1b; }}
.badge-permanente {{ background: #dbeafe; color: #1e40af; }}
.badge-temporal {{ background: #fce7f3; color: #9d174d; }}
.badge-sin {{ background: #f3f4f6; color: #6b7280; }}
.salary {{ font-weight: 600; color: #059669; }}
a.job-link {{ color: #4f46e5; text-decoration: none; font-weight: 500; }}
a.job-link:hover {{ text-decoration: underline; }}
.empty-state {{ padding: 40px; text-align: center; color: #9ca3af; }}

/* Responsive */
@media (max-width: 768px) {{
    .charts-grid {{ grid-template-columns: 1fr; }}
    header h1 {{ font-size: 1.6em; }}
    .filter-row {{ flex-direction: column; }}
    .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
    table {{ font-size: 0.8em; }}
}}
</style>
</head>
<body>
<div class="container">

<header>
    <h1>Mercado Laboral de Urabá</h1>
    <p class="subtitle">Dashboard interactivo de ofertas de empleo en la región de Urabá, Antioquia</p>
    <div class="meta">
        <span>Actualizado: <strong id="ts"></strong></span>
        <span>Fuentes: <strong>{stats['sources']}</strong> portales</span>
    </div>
</header>

<!-- Stats Cards -->
<div class="stats-grid">
    <div class="stat-card"><div class="label">Total Empleos</div><div class="value">{stats['total_jobs']}</div></div>
    <div class="stat-card"><div class="label">Municipios</div><div class="value">{stats['zones']}</div></div>
    <div class="stat-card"><div class="label">Empresas</div><div class="value">{stats['companies']}</div></div>
    <div class="stat-card"><div class="label">Permanentes</div><div class="value">{stats['permanent']}</div></div>
    <div class="stat-card"><div class="label">Temporales</div><div class="value">{stats['temporal']}</div></div>
    <div class="stat-card"><div class="label">Salario Prom.</div><div class="value" style="font-size:1.3em">{avg_sal_display}</div></div>
</div>

<!-- Charts -->
<div class="charts-grid">
    <div class="chart-box"><div id="c1"></div></div>
    <div class="chart-box"><div id="c2"></div></div>
    <div class="chart-box"><div id="c3"></div></div>
    <div class="chart-box"><div id="c4"></div></div>
    <div class="chart-box"><div id="c5"></div></div>
    <div class="chart-box"><div id="c6"></div></div>
</div>

<!-- Filters -->
<div class="filters">
    <div class="filter-row">
        <div class="filter-group">
            <label>Zona</label>
            <select id="fZone"><option value="">Todas</option></select>
        </div>
        <div class="filter-group">
            <label>Tipo Contrato</label>
            <select id="fContract">
                <option value="">Todos</option>
                <option value="permanente">Permanente</option>
                <option value="temporal">Temporal</option>
                <option value="sin especificar">Sin especificar</option>
            </select>
        </div>
        <div class="filter-group">
            <label>Fuente</label>
            <select id="fSource"><option value="">Todas</option></select>
        </div>
        <div class="filter-group">
            <label>Buscar</label>
            <input type="text" id="fSearch" placeholder="Título, empresa...">
        </div>
        <div class="filter-group">
            <label>Relevancia mín.</label>
            <select id="fRelevance">
                <option value="0">Cualquiera</option>
                <option value="0.5">≥ 50%</option>
                <option value="0.8">≥ 80%</option>
                <option value="0.9">≥ 90%</option>
            </select>
        </div>
        <button class="btn btn-outline" onclick="resetFilters()">Limpiar</button>
    </div>
</div>

<!-- Table -->
<div class="table-wrapper">
    <div class="table-header">
        <h2>Listado de Ofertas</h2>
        <span class="count" id="rowCount"></span>
    </div>
    <table>
        <thead>
            <tr>
                <th onclick="sortBy('title')">Cargo <span class="arrow">⇅</span></th>
                <th onclick="sortBy('company')">Empresa <span class="arrow">⇅</span></th>
                <th onclick="sortBy('zone')">Zona <span class="arrow">⇅</span></th>
                <th onclick="sortBy('contract_type')">Contrato <span class="arrow">⇅</span></th>
                <th onclick="sortBy('salary_max')">Salario <span class="arrow">⇅</span></th>
                <th onclick="sortBy('relevance_score')">Relevancia <span class="arrow">⇅</span></th>
                <th>Fuente</th>
                <th>Ver</th>
            </tr>
        </thead>
        <tbody id="tbody"></tbody>
    </table>
    <div class="empty-state" id="emptyState" style="display:none">No se encontraron resultados con los filtros aplicados.</div>
</div>

</div><!-- /container -->

<script>
const DATA = {table_json};
const CHARTS = {{
    c1: {charts['jobs_by_zone']},
    c2: {charts['contract_types']},
    c3: {charts['salary_distribution']},
    c4: {charts['sources']},
    c5: {charts['relevance']},
    c6: {charts['top_companies']},
}};

let filtered = [...DATA];
let sortCol = null, sortAsc = true;

function init() {{
    document.getElementById('ts').textContent = new Date().toLocaleString('es-CO');

    // Render charts
    for (const [id, spec] of Object.entries(CHARTS)) {{
        const s = typeof spec === 'string' ? JSON.parse(spec) : spec;
        Plotly.newPlot(id, s.data, {{...s.layout, paper_bgcolor:'transparent', plot_bgcolor:'transparent'}}, {{responsive:true}});
    }}

    // Populate filter dropdowns
    const zones = [...new Set(DATA.map(j => j.zone))].sort();
    const sources = [...new Set(DATA.map(j => j.source))].sort();
    const zSel = document.getElementById('fZone');
    zones.forEach(z => {{ const o = document.createElement('option'); o.value = z; o.textContent = z; zSel.appendChild(o); }});
    const sSel = document.getElementById('fSource');
    sources.forEach(s => {{ const o = document.createElement('option'); o.value = s; o.textContent = s; sSel.appendChild(o); }});

    // Listeners
    ['fZone','fContract','fSource','fRelevance'].forEach(id => document.getElementById(id).addEventListener('change', applyFilters));
    document.getElementById('fSearch').addEventListener('input', applyFilters);

    renderTable(DATA);
}}

function applyFilters() {{
    const zone = document.getElementById('fZone').value;
    const contract = document.getElementById('fContract').value;
    const source = document.getElementById('fSource').value;
    const search = document.getElementById('fSearch').value.toLowerCase();
    const minRel = parseFloat(document.getElementById('fRelevance').value);

    filtered = DATA.filter(j =>
        (!zone || j.zone === zone) &&
        (!contract || j.contract_type === contract) &&
        (!source || j.source === source) &&
        (j.relevance_score >= minRel) &&
        (!search || (j.title + ' ' + j.company).toLowerCase().includes(search))
    );
    renderTable(filtered);
}}

function resetFilters() {{
    ['fZone','fContract','fSource','fRelevance'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('fSearch').value = '';
    filtered = [...DATA];
    renderTable(DATA);
}}

function sortBy(col) {{
    if (sortCol === col) sortAsc = !sortAsc;
    else {{ sortCol = col; sortAsc = true; }}
    filtered.sort((a, b) => {{
        let av = a[col], bv = b[col];
        if (av == null) av = sortAsc ? Infinity : -Infinity;
        if (bv == null) bv = sortAsc ? Infinity : -Infinity;
        if (typeof av === 'string') return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
        return sortAsc ? av - bv : bv - av;
    }});
    renderTable(filtered);
}}

function renderTable(data) {{
    const tbody = document.getElementById('tbody');
    const empty = document.getElementById('emptyState');
    document.getElementById('rowCount').textContent = data.length + ' ofertas';

    if (!data.length) {{ tbody.innerHTML = ''; empty.style.display = 'block'; return; }}
    empty.style.display = 'none';

    tbody.innerHTML = data.map(j => `
        <tr>
            <td><strong>${{esc(j.title)}}</strong></td>
            <td>${{esc(j.company)}}</td>
            <td>${{esc(j.zone)}}</td>
            <td><span class="badge badge-${{j.contract_type === 'permanente' ? 'permanente' : j.contract_type === 'temporal' ? 'temporal' : 'sin'}}">${{esc(j.contract_type)}}</span></td>
            <td class="salary">${{j.salary_max ? fmtSal(j.salary_max) : 'N/A'}}</td>
            <td><span class="badge badge-${{j.relevance_score >= 0.8 ? 'high' : j.relevance_score >= 0.5 ? 'medium' : 'low'}}">${{Math.round(j.relevance_score * 100)}}%</span></td>
            <td>${{esc(j.source)}}</td>
            <td>${{j.url ? `<a class="job-link" href="${{j.url}}" target="_blank" rel="noopener">Abrir →</a>` : '—'}}</td>
        </tr>
    `).join('');
}}

function fmtSal(v) {{
    return '$' + new Intl.NumberFormat('es-CO', {{maximumFractionDigits:0}}).format(v);
}}
function esc(t) {{
    if (!t) return '';
    const d = document.createElement('div'); d.textContent = t; return d.innerHTML;
}}

window.addEventListener('load', init);
</script>
</body>
</html>"""
