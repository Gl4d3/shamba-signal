async function loadStatus() {
  const statusNode = document.querySelector('#api-status');
  try {
    const response = await fetch('/api/v1/platform/status');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const nextCapability = payload.capabilities.find(
      (capability) => capability.status === 'next',
    );
    if (!nextCapability) throw new Error('No next capability in platform status');
    statusNode.textContent = `${payload.release} · ${nextCapability.name} is next`;
    statusNode.dataset.state = 'ready';
  } catch (error) {
    statusNode.textContent = 'Platform status is temporarily unavailable. Product boundaries remain unchanged.';
    statusNode.dataset.state = 'error';
  }
}

loadStatus();
