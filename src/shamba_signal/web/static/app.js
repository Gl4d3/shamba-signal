async function loadStatus() {
  const statusNode = document.querySelector('#api-status');
  try {
    const response = await fetch('/api/v1/platform/status');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const activeCapability = payload.capabilities.find(
      (capability) => capability.id === 'annual-snapshot',
    ) || payload.capabilities.find(
      (capability) => capability.status === 'ready',
    ) || payload.capabilities.find(
      (capability) => capability.status === 'next',
    );
    if (!activeCapability) throw new Error('No active capability in platform status');
    const stateText = activeCapability.status === 'blocked'
      ? 'is blocked'
      : activeCapability.status === 'next'
        ? 'is next'
        : 'is ready';
    statusNode.textContent = `${payload.release} · ${activeCapability.name} ${stateText}`;
    statusNode.dataset.state = activeCapability.status;
  } catch (error) {
    statusNode.textContent = 'Platform status is temporarily unavailable. Product boundaries remain unchanged.';
    statusNode.dataset.state = 'error';
  }
}

loadStatus();
