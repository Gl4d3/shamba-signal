import tomllib
from pathlib import Path


def test_lockfile_matches_declared_project_dependencies() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    locked_project = next(
        package for package in lock["package"] if package["name"] == project["name"]
    )

    assert lock["requires-python"] == project["requires-python"]
    assert {item["name"] for item in locked_project["dependencies"]} == {
        "fastapi",
        "pydantic",
        "uvicorn",
    }
    assert {item["name"] for item in locked_project["optional-dependencies"]["dev"]} == {
        "httpx",
        "pytest",
        "pytest-cov",
        "ruff",
    }
    assert all("specifier" in item for item in locked_project["metadata"]["requires-dist"])
    assert all(
        "specifier" in item
        for item in locked_project["metadata"]["requires-extra"]["dev"]
    )
