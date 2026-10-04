from {{package_name}} import __version__, hello


def test_hello():
    assert hello("Alice") == "Hello Alice from {{project_name}}!"
    assert "Hello World" in hello()


def test_version():
    assert __version__ == "0.1.0"