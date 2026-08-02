async function loadStatus() {
  const statusNode = document.querySelector('#api-status');
  try {
    const response = await fetch('/api/v1/platform/status');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const activeCapability = payload.capabilities.find(
      (capability) => capability.status === 'blocked',
    ) || payload.capabilities.find(
      (capability) => capability.status === 'next',
    );
    if (!activeCapability) throw new Error('No active capability in platform status');
    const stateText = activeCapability.status === 'blocked' ? 'is blocked' : 'is next';
    statusNode.textContent = `${payload.release} · ${activeCapability.name} ${stateText}`;
    statusNode.dataset.state = activeCapability.status;
  } catch (error) {
    statusNode.textContent = 'Platform status is temporarily unavailable. Product boundaries remain unchanged.';
    statusNode.dataset.state = 'error';
  }
}

loadStatus();
