const number = (value) => `${Number(value).toFixed(3)} t/ha`;
const signed = (value) => `${value >= 0 ? '+' : '−'}${Math.abs(value).toFixed(3)} t/ha`;

function modelById(models, id) {
  return models.find((model) => model.id === id);
}

function renderModels(models) {
  const root = document.querySelector('#data-model-metrics');
  root.innerHTML = models.map((model) => `
    <article class="model-row ${model.id === 'county_mean' ? 'model-row--winner' : ''}">
      <div><span class="model-dot"></span><h3>${model.label}</h3></div>
      <p><strong>${number(model.mae_t_per_ha)}</strong><span>MAE</span></p>
      <p><strong>${number(model.rmse_t_per_ha)}</strong><span>RMSE</span></p>
      <span class="model-verdict">${model.id === 'county_mean' ? 'Benchmark retained' : model.id === 'weather_ridge' ? 'More signal, still behind' : 'Reference'}</span>
    </article>
  `).join('');
}

function renderChart(history) {
  const chart = document.querySelector('#history-chart');
  const usable = history.filter((row) => Number.isFinite(row.actual_yield_t_per_ha));
  const values = usable.map((row) => row.actual_yield_t_per_ha);
  const min = Math.max(0, Math.min(...values) - 0.15);
  const max = Math.max(...values) + 0.15;
  const width = 720; const height = 270; const pad = { left: 22, right: 16, top: 18, bottom: 25 };
  const x = (index) => pad.left + index * ((width - pad.left - pad.right) / Math.max(1, usable.length - 1));
  const y = (value) => height - pad.bottom - ((value - min) / Math.max(0.01, max - min)) * (height - pad.top - pad.bottom);
  const points = usable.map((row, index) => `${x(index)},${y(row.actual_yield_t_per_ha)}`).join(' ');
  const guides = [0.25, 0.5, 0.75].map((fraction) => {
    const guide = pad.top + fraction * (height - pad.top - pad.bottom);
    return `<line x1="${pad.left}" y1="${guide}" x2="${width - pad.right}" y2="${guide}" />`;
  }).join('');
  const dots = usable.map((row, index) => `<circle class="${row.provisional ? 'provisional-dot' : ''}" cx="${x(index)}" cy="${y(row.actual_yield_t_per_ha)}" r="${row.provisional ? 5 : 3.4}"><title>${row.year}: ${number(row.actual_yield_t_per_ha)}${row.provisional ? ' (provisional)' : ''}</title></circle>`).join('');
  chart.innerHTML = `<g class="chart-guides">${guides}</g><polyline points="${points}" />${dots}<text x="${pad.left}" y="14">${max.toFixed(2)}</text><text x="${pad.left}" y="${height - 4}">${min.toFixed(2)}</text>`;
}

function renderCounty(county) {
  const test = county.test;
  document.querySelector('#county-name').textContent = county.county_id.replaceAll('_', ' ');
  document.querySelector('#county-actual').textContent = number(test.actual_yield_t_per_ha);
  document.querySelector('#county-baseline').textContent = number(test.predictions.county_mean);
  document.querySelector('#county-weather').textContent = number(test.predictions.weather_ridge);
  document.querySelector('#county-error').textContent = signed(test.errors_t_per_ha.weather_ridge);
  renderChart(county.history);
}

function renderDashboard(payload) {
  const countyMean = modelById(payload.models, 'county_mean');
  const weather = modelById(payload.models, 'weather_ridge');
  document.querySelector('#result-statement').textContent = payload.result_statement;
  document.querySelector('#benchmark-mae').textContent = number(countyMean.mae_t_per_ha);
  document.querySelector('#weather-mae').textContent = number(weather.mae_t_per_ha);
  document.querySelector('#weather-delta').textContent = `${(weather.mae_t_per_ha - countyMean.mae_t_per_ha).toFixed(3)} t/ha behind the benchmark`;
  renderModels(payload.models);
  document.querySelector('#feature-list').innerHTML = payload.feature_definitions.map((feature, index) => `<li><span>0${index + 1}</span>${feature}</li>`).join('');
  document.querySelector('#limitation-list').innerHTML = payload.limitations.map((limitation) => `<li>${limitation}</li>`).join('');
  const selector = document.querySelector('#county-selector');
  selector.innerHTML = payload.counties.map((county) => `<option value="${county.county_id}">${county.county_id.replaceAll('_', ' ')}</option>`).join('');
  selector.disabled = false;
  const selectCounty = () => renderCounty(payload.counties.find((county) => county.county_id === selector.value));
  selector.addEventListener('change', selectCounty);
  selectCounty();
}

async function loadDashboard() {
  try {
    const response = await fetch('/api/v1/evaluation');
    if (!response.ok) throw new Error('private evaluation fixture unavailable');
    renderDashboard(await response.json());
  } catch (error) {
    document.querySelector('#result-statement').textContent = 'The private evaluation fixture is unavailable in this checkout.';
  }
}

loadDashboard();
