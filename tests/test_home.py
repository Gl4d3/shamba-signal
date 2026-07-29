from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_home_page_describes_the_real_mvp_boundary() -> None:
    client = TestClient(create_app())

    response = client.get('/')

    assert response.status_code == 200
    assert 'Shamba Signal' in response.text
    assert 'County-season yield forecasting' in response.text
    assert 'Relative yield potential' in response.text
    assert 'farm-level yield prediction' in response.text
