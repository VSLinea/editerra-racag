"""
Editerra RAC-CAG: AI-Powered Code Intelligence for Complex Projects

A universal code intelligence engine that brings semantic understanding
to any codebase, working with any LLM provider.
"""

__version__ = "0.2.0"
__author__ = "VSLinea"
__license__ = "BSL-1.1"

from importlib import import_module
from typing import Any, Dict, Tuple

__all__ = [
    "__version__",
    "EditerraEngine",
    "EditerraConfig",
    "get_config",
    "create_engine",
]


_LAZY_IMPORTS: Dict[str, Tuple[str, str]] = {
    "EditerraEngine": ("editerra_racag.engine", "EditerraEngine"),
    "create_engine": ("editerra_racag.engine", "create_engine"),
    "EditerraConfig": ("editerra_racag.config", "EditerraConfig"),
    "get_config": ("editerra_racag.config", "get_config"),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module 'editerra_racag' has no attribute {name!r}")

    module_name, attr_name = _LAZY_IMPORTS[name]
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
