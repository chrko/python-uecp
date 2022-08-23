def test_version():
    from pathlib import Path

    import tomli

    from uecp import __version__

    pyproject_toml = Path(__file__).parent.parent.joinpath("pyproject.toml")

    with open(pyproject_toml, "rb") as f:
        toml_dict = tomli.load(f)

    pyproject_version = toml_dict["tool"]["poetry"]["version"]

    assert __version__ == pyproject_version
