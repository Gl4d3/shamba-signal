import sys

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
            print(
                f"smoke test failed: {path} returned {response.status_code}",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if content_type not in response.headers.get("content-type", ""):
            print(
                f"smoke test failed: {path} has unexpected content type",
                file=sys.stderr,
            )
            raise SystemExit(1)
    print("Application/API smoke test passed")


if __name__ == "__main__":
    main()
