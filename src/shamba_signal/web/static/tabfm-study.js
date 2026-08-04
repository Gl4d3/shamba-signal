const TABFM_MODEL_LABELS = {
  county_mean: 'County historical mean',
  ridge: 'Temporal Ridge',
  weather_ridge: 'Weather Ridge',
  tabfm_temporal: 'TabFM Temporal',
  tabfm_weather: 'TabFM Weather',
};
const TABFM_MODEL_ORDER = [
  'county_mean',
  'ridge',
  'weather_ridge',
  'tabfm_temporal',
  'tabfm_weather',
];

function formatMetric(value, digits = 4) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric.toFixed(digits) : '—';
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function attachTabfmStyles() {
  if (document.querySelector('link[data-tabfm-study]')) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/static/tabfm-study.css?v=1';
  link.dataset.tabfmStudy = 'true';
  document.head.append(link);
}

function insertNavigationLink(container, beforeSelector, label) {
  if (!container || container.querySelector('a[href="#tabfm"]')) return;
  const link = document.createElement('a');
  link.href = '#tabfm';
  link.textContent = label;
  if (container.classList.contains('sidebar-nav')) {
    link.className = 'nav-link';
    link.innerHTML = '<span>04</span>Foundation model';
  }
  const before = container.querySelector(beforeSelector);
  container.insertBefore(link, before || null);
}

function createTabfmShell() {
  const existing = document.querySelector('#tabfm');
  if (existing) return existing;

  insertNavigationLink(
    document.querySelector('.sidebar-nav'),
    'a[href="#method"]',
    'Foundation model',
  );
  insertNavigationLink(
    document.querySelector('.mobile-nav'),
    'a[href="#method"]',
    'Foundation',
  );

  const section = document.createElement('section');
  section.id = 'tabfm';
  section.className = 'dashboard-section section-block tabfm-study';
  section.setAttribute('aria-labelledby', 'tabfm-title');
  section.innerHTML = `
    <header class="section-header tabfm-study__header">
      <div>
        <div class="tabfm-study__eyebrow">
          <p class="kicker">Foundation model study</p>
          <span class="tabfm-study__badge">Exploratory extension</span>
        </div>
        <h2 id="tabfm-title">Can a tabular foundation model beat the simple benchmark?</h2>
        <p>The original bounded weather no-go remains unchanged. This separate study uses expanding temporal folds from 2018–2023.</p>
      </div>
    </header>
    <div class="panel tabfm-study__state" id="tabfm-study-state" role="status" aria-live="polite">
      <span class="tabfm-study__pulse" aria-hidden="true"></span>
      <div>
        <strong>Checking for locally generated TabFM evidence…</strong>
        <p>The completed original dashboard remains available regardless of this optional experiment.</p>
      </div>
    </div>
    <div id="tabfm-study-content" hidden></div>
  `;
  const method = document.querySelector('#method');
  const dashboard = document.querySelector('#dashboard');
  if (method?.parentNode) method.parentNode.insertBefore(section, method);
  else dashboard?.append(section);
  return section;
}

function renderTabfmModelComparison(aggregate) {
  const available = TABFM_MODEL_ORDER.filter((name) => aggregate?.[name]?.pooled);
  const max = Math.max(
    ...available.map((name) => Number(aggregate[name].pooled.mae)),
    0.001,
  );
  const rows = available.map((name, index) => {
    const result = aggregate[name];
    const mae = Number(result.pooled.mae);
    const width = Math.max(4, (mae / max) * 100);
    const isTabfm = name.startsWith('tabfm_');
    return `
      <div class="tabfm-model-row ${isTabfm ? 'is-tabfm' : ''}">
        <div class="tabfm-model-row__label">
          <span>${index + 1}</span>
          <strong>${escapeHtml(TABFM_MODEL_LABELS[name] || name)}</strong>
        </div>
        <div class="tabfm-model-row__track" aria-hidden="true">
          <i style="width:${width.toFixed(2)}%"></i>
        </div>
        <div class="tabfm-model-row__value">
          <strong>${formatMetric(mae)}</strong>
          <small>MAE t/ha</small>
        </div>
      </div>`;
  }).join('');
  return `<div class="tabfm-model-comparison" aria-label="Pooled model MAE comparison">${rows}</div>`;
}

function renderTabfmFoldChart(folds) {
  const years = folds.map((fold) => Number(fold.evaluation_year));
  const seriesNames = ['county_mean', 'tabfm_temporal', 'tabfm_weather'];
  const values = folds.flatMap((fold) =>
    seriesNames.map((name) => Number(fold.metrics?.[name]?.mae)),
  );
  const max = Math.max(...values.filter(Number.isFinite), 0.001);
  const width = 760;
  const height = 280;
  const padding = { left: 54, right: 18, top: 26, bottom: 44 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const xFor = (index) =>
    padding.left + (index * chartWidth) / Math.max(1, years.length - 1);
  const yFor = (value) =>
    padding.top + chartHeight - (value / max) * chartHeight;
  const paths = seriesNames.map((name) => {
    const points = folds.map((fold, index) =>
      `${xFor(index)},${yFor(Number(fold.metrics?.[name]?.mae))}`,
    ).join(' ');
    return `<polyline class="tabfm-fold-chart__line tabfm-fold-chart__line--${name}" points="${points}" fill="none" />`;
  }).join('');
  const labels = years.map((year, index) =>
    `<text x="${xFor(index)}" y="${height - 15}" text-anchor="middle">${year}</text>`,
  ).join('');
  const rows = folds.map((fold) => `
    <tr>
      <th scope="row">${fold.evaluation_year}${fold.evaluation_year === 2023 ? ' · post-hoc' : ''}</th>
      <td>${formatMetric(fold.metrics?.county_mean?.mae)}</td>
      <td>${formatMetric(fold.metrics?.tabfm_temporal?.mae)}</td>
      <td>${formatMetric(fold.metrics?.tabfm_weather?.mae)}</td>
    </tr>`).join('');
  return `
    <div class="tabfm-fold-chart">
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="tabfm-fold-title tabfm-fold-desc">
        <title id="tabfm-fold-title">Rolling temporal MAE by evaluation year</title>
        <desc id="tabfm-fold-desc">County mean, TabFM Temporal, and TabFM Weather MAE for evaluation years ${years.join(', ')}.</desc>
        <line class="tabfm-fold-chart__axis" x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" />
        ${paths}
        ${labels}
      </svg>
      <div class="tabfm-fold-chart__legend" aria-label="Chart legend">
        <span><i class="is-county"></i>County mean</span>
        <span><i class="is-temporal"></i>TabFM Temporal</span>
        <span><i class="is-weather"></i>TabFM Weather</span>
      </div>
      <div class="tabfm-fold-table-wrap">
        <table class="tabfm-fold-table">
          <thead><tr><th>Year</th><th>County mean</th><th>TabFM Temporal</th><th>TabFM Weather</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

function decisionTone(code) {
  if (code === 'strong_go') return 'is-positive';
  if (code === 'no_go') return 'is-negative';
  return 'is-cautious';
}

function renderTabfmStudy(payload) {
  const state = document.querySelector('#tabfm-study-state');
  const content = document.querySelector('#tabfm-study-content');
  const aggregate = payload.aggregate || {};
  const temporalMae = Number(aggregate.tabfm_temporal?.pooled?.mae);
  const weatherMae = Number(aggregate.tabfm_weather?.pooled?.mae);
  const countyMae = Number(aggregate.county_mean?.pooled?.mae);
  const weatherDelta = weatherMae - temporalMae;
  const decision = payload.decision || {};
  const manifest = payload.manifest || {};

  content.innerHTML = `
    <div class="tabfm-kpi-grid">
      <article class="panel tabfm-kpi"><p>County benchmark</p><strong>${formatMetric(countyMae)}</strong><small>Pooled MAE · t/ha</small></article>
      <article class="panel tabfm-kpi tabfm-kpi--model"><p>TabFM Temporal</p><strong>${formatMetric(temporalMae)}</strong><small>Pooled MAE · t/ha</small></article>
      <article class="panel tabfm-kpi tabfm-kpi--model"><p>TabFM Weather</p><strong>${formatMetric(weatherMae)}</strong><small>Pooled MAE · t/ha</small></article>
      <article class="panel tabfm-kpi"><p>Weather contribution</p><strong>${Number.isFinite(weatherDelta) ? `${weatherDelta >= 0 ? '+' : ''}${weatherDelta.toFixed(4)}` : '—'}</strong><small>Weather − temporal MAE</small></article>
    </div>

    <div class="tabfm-study__grid">
      <article class="panel tabfm-study__comparison">
        <div class="panel-heading"><div><p class="kicker">Repeated temporal evidence</p><h3>Pooled model comparison</h3></div><span class="unit-label">lower is better</span></div>
        ${renderTabfmModelComparison(aggregate)}
      </article>
      <aside class="panel tabfm-decision ${decisionTone(decision.code)}">
        <p class="kicker">Generated decision</p>
        <h3>${escapeHtml(decision.headline || 'Decision unavailable')}</h3>
        <p>${escapeHtml(decision.rationale || 'The result artifact did not include a rationale.')}</p>
        <dl>
          <div><dt>Fold wins</dt><dd>${aggregate.tabfm_weather?.fold_wins_vs_county_mean ?? '—'} / ${payload.folds?.length ?? '—'}</dd></div>
          <div><dt>Checkpoint</dt><dd>${escapeHtml(manifest.checkpoint || 'tabfm_v1_0_0')}</dd></div>
          <div><dt>Context policy</dt><dd>${manifest.max_num_rows == null ? 'All available rows' : escapeHtml(manifest.max_num_rows)}</dd></div>
          <div><dt>Seed</dt><dd>${manifest.random_state ?? 42}</dd></div>
        </dl>
      </aside>
    </div>

    <article class="panel tabfm-study__folds">
      <div class="panel-heading"><div><p class="kicker">Stability over time</p><h3>Rolling-origin fold evidence</h3></div><span class="unit-label">2018–2023</span></div>
      ${renderTabfmFoldChart(payload.folds || [])}
    </article>

    <div class="tabfm-study__notes">
      <article class="panel">
        <p class="kicker">Interpretation boundary</p>
        <h3>2023 is post-hoc—not a new untouched test.</h3>
        <p>The original frozen experiment had already inspected provisional 2023. This extension earns credibility from repeated 2018–2022 folds; a genuinely future year would be the stronger confirmation.</p>
      </article>
      <article class="panel">
        <p class="kicker">Checkpoint licence</p>
        <h3>${escapeHtml(payload.checkpoint_license || 'tabfm-non-commercial-v1.0')}</h3>
        <p>The default pretrained weights are restricted to non-commercial, non-production research use. The dashboard loads only generated evidence—not model weights.</p>
      </article>
    </div>
    <p class="tabfm-study__boundary">${escapeHtml(payload.boundary || 'Retrospective county-year benchmark only.')}</p>
  `;
  state.hidden = true;
  content.hidden = false;
}

function renderTabfmUnavailable(message) {
  const state = document.querySelector('#tabfm-study-state');
  const content = document.querySelector('#tabfm-study-content');
  if (!state || !content) return;
  content.hidden = true;
  state.hidden = false;
  state.classList.add('is-unavailable');
  state.innerHTML = `
    <span class="tabfm-study__empty" aria-hidden="true">ƒ</span>
    <div>
      <strong>TabFM evidence has not been generated in this checkout.</strong>
      <p>${escapeHtml(message)} The original completed experiment remains fully available above.</p>
      <code>make tabfm-run TABFM_PANEL=/path/to/modelling_panel.csv TABFM_WEATHER_CACHE=data/raw/open-meteo-era5-batch-v1</code>
    </div>`;
}

async function loadTabfmStudy() {
  try {
    const response = await fetch('/api/v1/tabfm-evaluation');
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(
        error.detail || `TabFM evidence returned HTTP ${response.status}`,
      );
    }
    renderTabfmStudy(await response.json());
  } catch (error) {
    renderTabfmUnavailable(
      error instanceof Error ? error.message : 'Optional evidence is unavailable.',
    );
  }
}

attachTabfmStyles();
createTabfmShell();
loadTabfmStudy();

export { renderTabfmFoldChart, renderTabfmModelComparison, renderTabfmStudy };
