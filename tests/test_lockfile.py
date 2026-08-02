import re
import tomllib
from pathlib import Path


def load_lock() -> dict:
    return tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))


def test_lockfile_matches_declared_project_dependencies() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
    lock = load_lock()
    locked_project = next(
        package for package in lock["package"] if package["name"] == project["name"]
    )

    assert lock["requires-python"] == project["requires-python"]
    assert {item["name"] for item in locked_project["dependencies"]} == {
        "fastapi",
        "numpy",
        "pdfplumber",
        "pydantic",
        "uvicorn",
    }
    assert {item["name"] for item in locked_project["optional-dependencies"]["dev"]} == {
        "httpx",
        "pytest",
        "pytest-cov",
        "ruff",
    }
    metadata_requirements = locked_project["metadata"]["requires-dist"]
    assert all("specifier" in item for item in metadata_requirements)

    runtime_metadata = {
        f'{item["name"]}{item["specifier"]}'
        for item in metadata_requirements
        if "marker" not in item
    }
    dev_metadata = {
        f'{item["name"]}{item["specifier"]}'
        for item in metadata_requirements
        if item.get("marker") == "extra == 'dev'"
    }
    assert runtime_metadata == set(project["dependencies"])
    assert dev_metadata == set(project["optional-dependencies"]["dev"])


def test_registry_packages_have_verified_universal_source_fallbacks() -> None:
    registry_packages = [
        package
        for package in load_lock()["package"]
        if package.get("source", {}).get("registry")
    ]

    assert registry_packages
    for package in registry_packages:
        source = package["source"]
        sdist = package.get("sdist")
        assert source == {"registry": "https://pypi.org/simple"}
        assert sdist is not None, f'{package["name"]} has no source distribution'
        assert sdist["url"].startswith("https://files.pythonhosted.org/packages/")
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", sdist["hash"])
        assert isinstance(sdist["size"], int) and sdist["size"] > 0


def test_compiled_dependencies_are_not_locked_to_one_os_or_architecture() -> None:
    packages = {package["name"]: package for package in load_lock()["package"]}

    for package_name in {"coverage", "pydantic-core", "ruff"}:
        package = packages[package_name]
        assert "sdist" in package, f"{package_name} needs a portable build fallback"
        assert package["sdist"]["url"].endswith(".tar.gz")


def test_lock_contains_no_local_registry_artifact_paths() -> None:
    for package in load_lock()["package"]:
        if package["name"] == "shamba-signal":
            assert package["source"] == {"editable": "."}
            continue
        assert "path" not in package.get("source", {})
        for artifact_key in ("sdist", "wheels"):
            artifact = package.get(artifact_key)
            if isinstance(artifact, dict):
                assert artifact["url"].startswith("https://")
            elif isinstance(artifact, list):
                assert all(item["url"].startswith("https://") for item in artifact)


def test_lock_dependency_references_are_closed() -> None:
    packages = {package["name"]: package for package in load_lock()["package"]}
    for package in packages.values():
        for dependency in package.get("dependencies", []):
            assert dependency["name"] in packages
