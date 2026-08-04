const globalCountySearch = document.querySelector('#global-search');
const selectedCountyName = document.querySelector('#county-name');

function clearGlobalCountySearch() {
  if (document.activeElement !== globalCountySearch) {
    globalCountySearch.value = '';
  }
}

if (globalCountySearch && selectedCountyName) {
  clearGlobalCountySearch();

  const selectedCountyObserver = new MutationObserver(clearGlobalCountySearch);
  selectedCountyObserver.observe(selectedCountyName, {
    childList: true,
    characterData: true,
    subtree: true,
  });

  globalCountySearch.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      window.setTimeout(() => {
        globalCountySearch.value = '';
      }, 0);
    }
  });
}

function renumberSidebarNavigation() {
  const methodNumber = document.querySelector('.sidebar-nav a[href="#method"] span');
  const qualityNumber = document.querySelector('.sidebar-nav a[href="#quality"] span');
  if (methodNumber) methodNumber.textContent = '05';
  if (qualityNumber) qualityNumber.textContent = '06';
}

import('/static/tabfm-study.js?v=1')
  .then(renumberSidebarNavigation)
  .catch((error) => {
    console.warn('Optional TabFM study module could not be loaded.', error);
  });
