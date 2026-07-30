import json
from pathlib import Path


def test_dataset_catalog_records_slice_one_selection_and_candidate_sources() -> None:
    catalog = json.loads(Path('data/catalog/datasets.yaml').read_text())

    selection = catalog['pilot_selection']
    weights = selection['weights']
    assert sum(weights.values()) == 100
    assert weights['yield_label_quality'] == 35
    assert selection['selected_crop'] == 'maize'
    assert selection['selected_county'] == 'busia'
    assert selection['fallback_county'] == 'trans_nzoia'

    source_ids = {source['id'] for source in catalog['sources']}
    assert {
        'kilimostat-county-crops',
        'nipfn-maize-2012-2020',
        'fsd-maize-yield',
        'africultures-crop-calendar',
        'plantvillage-kenya',
        'sentinel-2-l2a',
        'chirps-v3',
        'soilgrids',
        'icpac-admin1',
    }.issubset(source_ids)

    for source in catalog['sources']:
        assert source['license_status'] in {'verified', 'review-required'}
        assert source['access_url'].startswith('https://')
