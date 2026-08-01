from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def main() -> None:
    client = TestClient(create_app())
    expected = {
        "/": "text/html",
        "/healthz": "application/json",
        "/api/v1/platform/status": "application/json",
        "/openapi.json": "application/json",
        "/static/app.js": "text/javascript",
        "/static/styles.css": "text/css",
    }
    for path, content_type in expected.items():
        response = client.get(path)
        if response.status_code != 200:
            raise SystemExit(f"smoke test failed: {path} returned {response.status_code}")
        if content_type not in response.headers.get("content-type", ""):
            raise SystemExit(f"smoke test failed: {path} has unexpected content type")
    print("Application/API smoke test passed")


if __name__ == "__main__":
    main()
