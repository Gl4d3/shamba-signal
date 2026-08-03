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
