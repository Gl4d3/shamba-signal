from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_platform_status_exposes_approved_product_contract() -> None:
    client = TestClient(create_app())

    response = client.get('/api/v1/platform/status')
    assert response.status_code == 200
    body = response.json()
    assert body['product'] == 'Shamba Signal'
    assert body['release'] == 'slice-1-feasibility-v0'
    assert body['primary_output'] == 'county-season yield forecast'
    assert body['forecast_timing'] == 'mid-season'
    assert body['architecture'] == 'modular decision-intelligence platform'
    assert body['geography'] == 'Kenya-wide with Busia as the selected county deep dive'
    assert body['crop_scope'] == (
        'maize selected by data feasibility; Trans Nzoia is the county fallback'
    )
    assert body['refresh_modes'] == ['scheduled', 'analyst-triggered']
    assert [capability['id'] for capability in body['capabilities']] == [
        'data-feasibility',
        'yield-forecasting',
        'stress-attribution',
        'guardrailed-advisory',
    ]


def test_slice_one_marks_feasibility_ready_and_target_dataset_next() -> None:
    client = TestClient(create_app())

    body = client.get('/api/v1/platform/status').json()
    statuses = {item['id']: item['status'] for item in body['capabilities']}

    assert statuses == {
        'data-feasibility': 'ready',
        'yield-forecasting': 'next',
        'stress-attribution': 'planned',
        'guardrailed-advisory': 'planned',
    }
