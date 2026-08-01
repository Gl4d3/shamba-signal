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

    runtime_metadata = {
        f'{item["name"]}{item["specifier"]}'
        for item in locked_project["metadata"]["requires-dist"]
    }
    dev_metadata = {
        f'{item["name"]}{item["specifier"]}'
        for item in locked_project["metadata"]["requires-extra"]["dev"]
    }
    assert runtime_metadata == set(project["dependencies"])
    assert dev_metadata == set(project["optional-dependencies"]["dev"])


def test_lock_does_not_filter_registry_packages_to_one_platform() -> None:
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    registry_packages = [
        package for package in lock["package"] if package.get("source", {}).get("registry")
    ]
    assert registry_packages
    assert all("wheels" not in package for package in registry_packages)
