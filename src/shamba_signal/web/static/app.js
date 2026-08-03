const state = {
  payload: null,
  platform: null,
  health: null,
  metric: 'mae_t_per_ha',
  selectedCountyId: null,
  filteredCounties: [],
  highlightedCountyIndex: -1,
  observer: null,
};

const MODEL_COPY = {
  previous_year: {
    short: 'Previous year',
    description: 'Transparent reference using the prior annual observation.',
  },
  county_mean: {
    short: 'County mean',
    description: 'Historical county average and the benchmark to beat.',
  },
  ridge: {
    short: 'Temporal Ridge',
    description: 'Regularized temporal model without the weather feature set.',
  },
  weather_ridge: {
    short: 'Weather Ridge',
    description: 'Temporal Ridge plus the bounded annual ERA5 feature contract.',
  },
};

const MODEL_COLORS = {
  previous_year: '#9a8d78',
  county_mean: '#315f39',
  ridge: '#8aa34f',
  weather_ridge: '#c7832f',
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function countyLabel(countyId) {
  return String(countyId)
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function metricLabel(metric = state.metric) {
  return metric === 'rmse_t_per_ha' ? 'RMSE' : 'MAE';
}

function number(value, digits = 3) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(digits) : '—';
}

function yieldNumber(value) {
  return `${number(value)} t/ha`;
}

function signed(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return '—';
  return `${parsed >= 0 ? '+' : '−'}${Math.abs(parsed).toFixed(3)} t/ha`;
}

function modelById(models, id) {
  return models.find((model) => model.id === id);
}

async function parseResponse(response) {
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch (_error) {
      // The status text remains the most useful available message.
    }
    throw new Error(detail);
  }
  return response.json();
}

function setPageState(nextState, message = '') {
  document.body.dataset.state = nextState;
  $('#loading-state').hidden = nextState !== 'loading';
  $('#error-state').hidden = nextState !== 'error';
  $('#dashboard').hidden = nextState !== 'ready';
  if (message) $('#error-message').textContent = message;
}

async function loadDashboard() {
  setPageState('loading');
  $('#service-status').textContent = 'Connecting…';
  $('#service-status-dot').className = 'status-dot';

  const evaluationPromise = fetch('/api/v1/evaluation').then(parseResponse);
  const platformPromise = fetch('/api/v1/platform/status').then(parseResponse);
  const healthPromise = fetch('/healthz').then(parseResponse);

  const [evaluationResult, platformResult, healthResult] = await Promise.allSettled([
    evaluationPromise,
    platformPromise,
    healthPromise,
  ]);

  if (evaluationResult.status !== 'fulfilled') {
    const reason = evaluationResult.reason instanceof Error
      ? evaluationResult.reason.message
      : 'The private evaluation fixture is unavailable in this checkout.';
    setPageState(
      'error',
      `The private evaluation fixture could not be loaded: ${reason}`,
    );
    renderRuntimeStatus(null, platformResult, healthResult);
    return;
  }

  state.payload = evaluationResult.value;
  state.platform = platformResult.status === 'fulfilled' ? platformResult.value : null;
  state.health = healthResult.status === 'fulfilled' ? healthResult.value : null;
  state.selectedCountyId = state.payload.counties?.[0]?.county_id || null;

  renderOverview(state.payload);
  renderModelComparison(state.payload.models, state.metric);
  renderModelBattlecard(state.payload.models, state.metric);
  renderMethod(state.payload);
  renderQuality(state.payload, state.platform, state.health);
  setupCountyExplorer(state.payload.counties || []);
  renderRuntimeStatus(state.payload, platformResult, healthResult);
  setupSectionObserver();
  setPageState('ready');
}

function renderOverview(payload) {
  const countyMean = modelById(payload.models, 'county_mean');
  const weather = modelById(payload.models, 'weather_ridge');
  const gap = Number(weather?.mae_t_per_ha) - Number(countyMean?.mae_t_per_ha);

  $('#result-statement').textContent = payload.result_statement;
  $('#decision-badge').textContent = payload.result === 'no-go' ? 'No-go' : 'Keep';
  $('#benchmark-mae').textContent = number(countyMean?.mae_t_per_ha);
  $('#weather-mae').textContent = number(weather?.mae_t_per_ha);
  $('#weather-gap').textContent = number(gap);
  $('#weather-gap-label').textContent = gap > 0 ? 'Weather Ridge is behind' : 'Weather Ridge is ahead';
  $('#county-count').textContent = String(payload.counties?.length || 0);
  $('#selection-year').textContent = String(payload.selection_year || '—');
  $('#test-year').textContent = `${payload.provisional_test_year || '—'} provisional`;

  const interpretation = payload.result === 'no-go'
    ? `Weather Ridge improved on the temporal Ridge reference, but remained ${number(gap)} t/ha behind the county historical mean on MAE.`
    : `Weather Ridge beat the county historical mean by ${number(Math.abs(gap))} t/ha on MAE.`;
  $('#model-interpretation').textContent = interpretation;
  $('#interpretation-title').textContent = payload.result === 'no-go'
    ? 'Benchmark retained'
    : 'Weather model retained';
}

function renderModelComparison(models, metric) {
  const root = $('#model-bars');
  const ranked = [...models].sort((left, right) => left[metric] - right[metric]);
  const max = Math.max(...ranked.map((model) => Number(model[metric])));
  const winnerId = ranked[0]?.id;

  root.innerHTML = ranked.map((model) => {
    const width = max > 0 ? (Number(model[metric]) / max) * 100 : 0;
    const classes = [
      'model-bar-row',
      model.id === winnerId ? 'is-winner' : '',
      model.id === 'weather_ridge' ? 'is-weather' : '',
    ].filter(Boolean).join(' ');
    const verdict = model.id === winnerId
      ? 'Best result'
      : model.id === 'weather_ridge'
        ? 'Weather test'
        : 'Reference';

    return `
      <div class="${classes}">
        <div class="model-bar-label">
          <strong>${escapeHtml(model.label)}</strong>
          <small>${verdict}</small>
        </div>
        <div class="model-track" aria-hidden="true">
          <div class="model-fill" style="--bar-width:${width.toFixed(2)}%"></div>
        </div>
        <span class="model-bar-value">${number(model[metric])}</span>
      </div>
    `;
  }).join('');

  root.setAttribute(
    'aria-label',
    `${metricLabel(metric)} model comparison. ${ranked[0]?.label || 'No model'} has the lowest error.`,
  );
}

function renderModelBattlecard(models, metric) {
  const root = $('#model-battlecard');
  const ranked = [...models].sort((left, right) => left[metric] - right[metric]);

  root.innerHTML = ranked.map((model, index) => {
    const copy = MODEL_COPY[model.id] || { description: 'Evaluation model.' };
    return `
      <article class="battlecard ${index === 0 ? 'is-winner' : ''}">
        <span class="rank">${index + 1}</span>
        <h3>${escapeHtml(model.label)}</h3>
        <strong>${number(model[metric])}</strong>
        <p>${metricLabel(metric)} t/ha · ${escapeHtml(copy.description)}</p>
      </article>
    `;
  }).join('');
}

function selectMetric(metric) {
  if (!state.payload || state.metric === metric) return;
  state.metric = metric;
  const maeSelected = metric === 'mae_t_per_ha';
  $('#metric-mae').classList.toggle('is-selected', maeSelected);
  $('#metric-mae').setAttribute('aria-pressed', String(maeSelected));
  $('#metric-rmse').classList.toggle('is-selected', !maeSelected);
  $('#metric-rmse').setAttribute('aria-pressed', String(!maeSelected));
  renderModelComparison(state.payload.models, metric);
  renderModelBattlecard(state.payload.models, metric);
}

function setupCountyExplorer(counties) {
  state.filteredCounties = [...counties];
  renderCountyOptions(state.filteredCounties);
  if (state.selectedCountyId) {
    const firstCounty = counties.find((county) => county.county_id === state.selectedCountyId);
    if (firstCounty) chooseCounty(firstCounty);
  }
}

function filterCounties(query) {
  const normalized = String(query || '').trim().toLowerCase();
  const counties = state.payload?.counties || [];
  state.filteredCounties = counties.filter((county) => {
    const id = county.county_id.toLowerCase();
    return id.includes(normalized) || countyLabel(id).toLowerCase().includes(normalized);
  });
  state.highlightedCountyIndex = state.filteredCounties.length ? 0 : -1;
  renderCountyOptions(state.filteredCounties);
  return state.filteredCounties;
}

function renderCountyOptions(counties) {
  const root = $('#county-options');
  if (!counties.length) {
    root.innerHTML = '<p>No county matches that search.</p>';
    return;
  }
  root.innerHTML = counties.map((county, index) => `
    <button
      type="button"
      role="option"
      data-county-id="${escapeHtml(county.county_id)}"
      aria-selected="${county.county_id === state.selectedCountyId}"
      class="${index === state.highlightedCountyIndex ? 'is-highlighted' : ''}"
    >${escapeHtml(countyLabel(county.county_id))}</button>
  `).join('');
}

function openCountyOptions() {
  $('#county-options').hidden = false;
  $('#county-search').setAttribute('aria-expanded', 'true');
}

function closeCountyOptions() {
  $('#county-options').hidden = true;
  $('#county-search').setAttribute('aria-expanded', 'false');
}

function chooseCounty(county) {
  state.selectedCountyId = county.county_id;
  const label = countyLabel(county.county_id);
  $('#county-search').value = label;
  $('#global-search').value = label;
  renderCounty(county);
  renderCountyOptions(state.filteredCounties);
  closeCountyOptions();
}

function renderCounty(county) {
  const test = county.test;
  const predictionEntries = Object.entries(test.predictions);
  const closest = predictionEntries
    .map(([id, value]) => ({ id, value, error: Number(value) - Number(test.actual_yield_t_per_ha) }))
    .sort((left, right) => Math.abs(left.error) - Math.abs(right.error))[0];

  $('#county-name').textContent = countyLabel(county.county_id);
  $('#county-test-year').textContent = String(test.year);
  $('#county-actual').textContent = yieldNumber(test.actual_yield_t_per_ha);
  $('#county-best-model').textContent = MODEL_COPY[closest.id]?.short || closest.id;
  $('#county-weather').textContent = yieldNumber(test.predictions.weather_ridge);
  $('#county-weather-error').textContent = signed(test.errors_t_per_ha.weather_ridge);
  renderHistoryChart(county.history, test);
  renderCountyPredictions(test);
  renderCountyErrors(test, closest.id);
}

function renderHistoryChart(history, test) {
  const chart = $('#history-chart');
  const usable = history.filter((row) => Number.isFinite(Number(row.actual_yield_t_per_ha)));
  if (!usable.length) {
    chart.innerHTML = '';
    $('#history-summary').textContent = 'No usable annual history is available for this county.';
    return;
  }

  const predictions = Object.entries(test.predictions).map(([id, value]) => ({ id, value: Number(value) }));
  const values = [
    ...usable.map((row) => Number(row.actual_yield_t_per_ha)),
    ...predictions.map((item) => item.value),
  ];
  const rawMin = Math.min(...values);
  const rawMax = Math.max(...values);
  const paddingValue = Math.max(0.1, (rawMax - rawMin) * 0.16);
  const min = Math.max(0, rawMin - paddingValue);
  const max = rawMax + paddingValue;
  const width = 760;
  const height = 300;
  const pad = { left: 48, right: 36, top: 24, bottom: 36 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const x = (index) => pad.left + (index * plotWidth) / Math.max(1, usable.length - 1);
  const y = (value) => pad.top + ((max - value) / Math.max(0.001, max - min)) * plotHeight;
  const latestX = x(usable.length - 1);
  const points = usable
    .map((row, index) => `${x(index).toFixed(2)},${y(Number(row.actual_yield_t_per_ha)).toFixed(2)}`)
    .join(' ');

  const guides = [0, 0.25, 0.5, 0.75, 1].map((fraction) => {
    const guideY = pad.top + fraction * plotHeight;
    const guideValue = max - fraction * (max - min);
    return `<line x1="${pad.left}" y1="${guideY}" x2="${width - pad.right}" y2="${guideY}"></line><text x="${pad.left - 9}" y="${guideY + 4}" text-anchor="end">${guideValue.toFixed(2)}</text>`;
  }).join('');

  const yearLabels = usable.map((row, index) => {
    if (index !== 0 && index !== usable.length - 1 && row.year % 2 !== 0) return '';
    return `<text x="${x(index)}" y="${height - 10}" text-anchor="middle">${row.year}${row.provisional ? '*' : ''}</text>`;
  }).join('');

  const actualDots = usable.map((row, index) => `
    <circle
      class="actual-point ${row.provisional ? 'is-provisional' : ''}"
      cx="${x(index)}"
      cy="${y(Number(row.actual_yield_t_per_ha))}"
      r="${row.provisional ? 5 : 3.4}"
    ><title>${row.year}: ${yieldNumber(row.actual_yield_t_per_ha)}${row.provisional ? ' provisional' : ''}</title></circle>
  `).join('');

  const predictionDots = predictions.map((item, index) => {
    const offset = (index - (predictions.length - 1) / 2) * 7;
    return `
      <line class="prediction-guide" x1="${latestX}" y1="${y(item.value)}" x2="${latestX + offset}" y2="${y(item.value)}"></line>
      <circle class="prediction-point" cx="${latestX + offset}" cy="${y(item.value)}" r="4.5" fill="${MODEL_COLORS[item.id] || '#8aa34f'}">
        <title>${MODEL_COPY[item.id]?.short || item.id}: ${yieldNumber(item.value)}</title>
      </circle>
    `;
  }).join('');

  chart.innerHTML = `
    <g class="chart-grid">${guides}</g>
    <g class="chart-axis">${yearLabels}</g>
    <polyline class="actual-line" points="${points}"></polyline>
    ${actualDots}
    ${predictionDots}
  `;

  const first = usable[0];
  const last = usable[usable.length - 1];
  $('#history-summary').textContent = `${first.year} actual yield was ${yieldNumber(first.actual_yield_t_per_ha)}. ${last.year} provisional actual yield is ${yieldNumber(last.actual_yield_t_per_ha)}; four model predictions are plotted at the final year.`;
}

function renderCountyPredictions(test) {
  const root = $('#county-predictions');
  const rows = [
    { id: 'actual', label: 'Actual yield', value: Number(test.actual_yield_t_per_ha) },
    ...Object.entries(test.predictions).map(([id, value]) => ({
      id,
      label: MODEL_COPY[id]?.short || id,
      value: Number(value),
    })),
  ];
  const max = Math.max(...rows.map((row) => row.value));

  root.innerHTML = rows.map((row) => `
    <div class="prediction-row ${row.id === 'actual' ? 'is-actual' : ''}">
      <span>${escapeHtml(row.label)}</span>
      <div class="prediction-track" aria-hidden="true"><div class="prediction-fill" style="--bar-width:${max > 0 ? ((row.value / max) * 100).toFixed(2) : 0}%"></div></div>
      <b>${number(row.value)}</b>
    </div>
  `).join('');
}

function renderCountyErrors(test, closestId) {
  const root = $('#county-errors');
  root.innerHTML = Object.entries(test.errors_t_per_ha)
    .sort((left, right) => Math.abs(left[1]) - Math.abs(right[1]))
    .map(([id, error]) => `
      <tr class="${id === closestId ? 'is-best' : ''}">
        <td>${escapeHtml(MODEL_COPY[id]?.short || id)}</td>
        <td class="${Number(error) >= 0 ? 'error-positive' : 'error-negative'}">${signed(error)}</td>
        <td>${number(Math.abs(Number(error)))}</td>
      </tr>
    `).join('');
}

function renderMethod(payload) {
  $('#feature-count').textContent = String(payload.feature_definitions?.length || 0);
  $('#feature-list').innerHTML = (payload.feature_definitions || []).map((feature, index) => `
    <li><span>${String(index + 1).padStart(2, '0')}</span><strong>${escapeHtml(feature)}</strong></li>
  `).join('');

  const firstYear = Math.min(
    ...payload.counties.flatMap((county) => county.history.map((row) => Number(row.year))),
  );
  const selectionYear = Number(payload.selection_year);
  const testYear = Number(payload.provisional_test_year);
  $('#split-timeline').innerHTML = `
    <div class="split-phase split-phase--train"><span>Train</span><strong>${firstYear}–${selectionYear - 1}</strong><small>Historical learning period</small></div>
    <div class="split-phase split-phase--select"><span>Select</span><strong>${selectionYear}</strong><small>Choose regularization</small></div>
    <div class="split-phase split-phase--test"><span>Final test</span><strong>${testYear}*</strong><small>Provisional · evaluated once</small></div>
  `;
}

function renderQuality(payload, platform, health) {
  $('#limitation-list').innerHTML = (payload.limitations || [])
    .map((limitation) => `<li>${escapeHtml(limitation)}</li>`)
    .join('');
  $('#fixture-version').textContent = payload.fixture_version || 'Unknown';
  $('#coverage-value').textContent = `${payload.counties?.length || 0} counties`;
  $('#platform-release').textContent = platform?.release || health?.release || 'Unavailable';
  $('#api-health').textContent = health?.status === 'ok' ? 'Operational' : 'Unavailable';
  $('#fixture-health').textContent = 'Loaded';
  $('#platform-health').textContent = platform ? 'Loaded' : 'Unavailable';
}

function renderRuntimeStatus(payload, platformResult, healthResult) {
  const fixtureLive = Boolean(payload);
  const platformLive = platformResult.status === 'fulfilled';
  const apiLive = healthResult.status === 'fulfilled' && healthResult.value?.status === 'ok';
  const allLive = fixtureLive && platformLive && apiLive;
  const anyError = !fixtureLive || !apiLive;

  const serviceText = allLive ? 'All evidence services ready' : anyError ? 'Service degraded' : 'Partially available';
  $('#service-status').textContent = serviceText;
  $('#service-status-dot').className = `status-dot ${allLive ? 'is-live' : anyError ? 'is-error' : ''}`;

  const healthChip = $('#health-chip');
  healthChip.className = `health-chip ${allLive ? 'is-live' : anyError ? 'is-error' : ''}`;
  healthChip.innerHTML = `<span aria-hidden="true"></span>${allLive ? 'API live' : anyError ? 'API degraded' : 'Partial'}`;

  const release = platformResult.status === 'fulfilled'
    ? platformResult.value.release
    : healthResult.status === 'fulfilled'
      ? healthResult.value.release
      : 'unavailable';
  $('#release-chip').textContent = `Release ${release}`;

  const pill = $('#system-health-pill');
  pill.className = `status-pill ${allLive ? 'is-live' : anyError ? 'is-error' : ''}`;
  pill.textContent = allLive ? 'Operational' : anyError ? 'Degraded' : 'Partial';
}

function csvCell(value) {
  const text = String(value ?? '');
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadCountyCsv() {
  if (!state.payload || !state.selectedCountyId) return;
  const county = state.payload.counties.find((item) => item.county_id === state.selectedCountyId);
  if (!county) return;
  const header = [
    'record_type',
    'county_id',
    'year',
    'model',
    'actual_yield_t_per_ha',
    'prediction_t_per_ha',
    'error_t_per_ha',
    'provisional',
  ];
  const rows = county.history.map((row) => [
    'actual',
    county.county_id,
    row.year,
    '',
    row.actual_yield_t_per_ha,
    '',
    '',
    row.provisional,
  ]);
  Object.entries(county.test.predictions).forEach(([model, prediction]) => {
    rows.push([
      'prediction',
      county.county_id,
      county.test.year,
      model,
      county.test.actual_yield_t_per_ha,
      prediction,
      county.test.errors_t_per_ha[model],
      county.test.provisional,
    ]);
  });
  const csv = [header, ...rows].map((row) => row.map(csvCell).join(',')).join('\n');
  downloadBlob(csv, `shamba-signal-${county.county_id}-${county.test.year}.csv`, 'text/csv;charset=utf-8');
}

function downloadEvaluationJson() {
  if (!state.payload) return;
  const json = `${JSON.stringify(state.payload, null, 2)}\n`;
  downloadBlob(json, 'shamba-signal-evaluation.json', 'application/json;charset=utf-8');
}

function setupSectionObserver() {
  if (!('IntersectionObserver' in window)) return;
  state.observer?.disconnect();
  const links = [...$$('.nav-link'), ...$$('.mobile-nav a')];
  const sections = $$('.dashboard-section');
  state.observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];
    if (!visible) return;
    links.forEach((link) => {
      link.classList.toggle('is-active', link.getAttribute('href') === `#${visible.target.id}`);
    });
  }, { rootMargin: '-18% 0px -62% 0px', threshold: [0.05, 0.2, 0.5] });
  sections.forEach((section) => state.observer.observe(section));
}

function handleCountyInput(event) {
  filterCounties(event.target.value);
  openCountyOptions();
}

function handleCountyKeydown(event) {
  if (event.key === 'Escape') {
    closeCountyOptions();
    return;
  }
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault();
    const direction = event.key === 'ArrowDown' ? 1 : -1;
    const maxIndex = state.filteredCounties.length - 1;
    if (maxIndex < 0) return;
    state.highlightedCountyIndex = Math.min(
      maxIndex,
      Math.max(0, state.highlightedCountyIndex + direction),
    );
    renderCountyOptions(state.filteredCounties);
    return;
  }
  if (event.key === 'Enter') {
    const county = state.filteredCounties[state.highlightedCountyIndex] || state.filteredCounties[0];
    if (county) {
      event.preventDefault();
      chooseCounty(county);
    }
  }
}

function selectFromGlobalSearch() {
  const matches = filterCounties($('#global-search').value);
  if (!matches.length) return;
  chooseCounty(matches[0]);
  $('#counties').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setupInteractions() {
  $('#metric-mae').addEventListener('click', () => selectMetric('mae_t_per_ha'));
  $('#metric-rmse').addEventListener('click', () => selectMetric('rmse_t_per_ha'));
  $('#retry-button').addEventListener('click', loadDashboard);
  $('#export-county').addEventListener('click', downloadCountyCsv);
  $('#export-evaluation').addEventListener('click', downloadEvaluationJson);

  $('#county-search').addEventListener('focus', () => {
    filterCounties($('#county-search').value);
    openCountyOptions();
  });
  $('#county-search').addEventListener('input', handleCountyInput);
  $('#county-search').addEventListener('keydown', handleCountyKeydown);
  $('#county-options').addEventListener('click', (event) => {
    const button = event.target.closest('[data-county-id]');
    if (!button || !state.payload) return;
    const county = state.payload.counties.find((item) => item.county_id === button.dataset.countyId);
    if (county) chooseCounty(county);
  });

  $('#global-search').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') selectFromGlobalSearch();
  });
  $('#global-search').addEventListener('search', () => {
    if ($('#global-search').value) selectFromGlobalSearch();
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.county-picker')) closeCountyOptions();
  });
}

setupInteractions();
loadDashboard();
