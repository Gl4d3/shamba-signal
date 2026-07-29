from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_platform_status_exposes_approved_product_contract() -> None:
    client = TestClient(create_app())

    response = client.get('/api/v1/platform/status')

    assert response.status_code == 200
    body = response.json()
    assert body['product'] == 'Shamba Signal'
    assert body['primary_output'] == 'county-season yield forecast'
    assert body['forecast_timing'] == 'mid-season'
    assert body['architecture'] == 'modular decision-intelligence platform'
    assert body['refresh_modes'] == ['scheduled', 'analyst-triggered']
    assert [capability['id'] for capability in body['capabilities']] == [
        'data-feasibility',
        'yield-forecasting',
        'stress-attribution',
        'guardrailed-advisory',
    ]


def test_foundation_only_marks_runnable_shell_ready() -> None:
    client = TestClient(create_app())

    body = client.get('/api/v1/platform/status').json()
    statuses = {item['id']: item['status'] for item in body['capabilities']}

    assert statuses == {
        'data-feasibility': 'next',
        'yield-forecasting': 'planned',
        'stress-attribution': 'planned',
        'guardrailed-advisory': 'planned',
    }
