async function loadStatus() {
  const statusNode = document.querySelector('#api-status');
  try {
    const response = await fetch('/api/v1/platform/status');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    statusNode.textContent = `${payload.release} · ${payload.capabilities[0].name} is next`;
    statusNode.dataset.state = 'ready';
  } catch (error) {
    statusNode.textContent = 'Platform contract unavailable';
    statusNode.dataset.state = 'error';
  }
}

loadStatus();
