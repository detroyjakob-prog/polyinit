"""{{project_name}}: A Python library."""

__version__ = "0.1.0"

def hello(name: str = "World") -> str:
    return f"Hello {name} from {{project_name}}!"

__all__ = ["hello", "__version__"]