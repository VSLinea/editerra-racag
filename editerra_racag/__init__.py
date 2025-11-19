"""
Editerra RAC-CAG: AI-Powered Code Intelligence for Complex Projects

A universal code intelligence engine that brings semantic understanding
to any codebase, working with any LLM provider.
"""

__version__ = "0.1.0"
__author__ = "VSLinea"
__license__ = "BSL-1.1"

__all__ = [
    "__version__",
    "EditerraEngine",
    "EditerraConfig",
    "get_config",
    "create_engine",
]

from editerra_racag.engine import EditerraEngine, create_engine
from editerra_racag.config import EditerraConfig, get_config
