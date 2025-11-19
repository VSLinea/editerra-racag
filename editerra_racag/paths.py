"""
Path resolution utilities for Editerra RAC-CAG.

Handles converting hardcoded paths to config-aware paths.
"""

from pathlib import Path
from typing import Optional


def resolve_db_path(config_path: Optional[str] = None, workspace: Optional[Path] = None) -> str:
    """
    Resolve the ChromaDB path.
    
    Priority:
    1. Explicit config_path parameter
    2. workspace/.editerra-racag/db/chroma_store
    3. Default: .editerra-racag/db/chroma_store (relative to cwd)
    """
    if config_path:
        return config_path
    
    if workspace:
        return str(workspace / ".editerra-racag" / "db" / "chroma_store")
    
    return ".editerra-racag/db/chroma_store"


def resolve_output_path(config_path: Optional[str] = None, workspace: Optional[Path] = None) -> Path:
    """
    Resolve the output directory path.
    
    Priority:
    1. Explicit config_path parameter
    2. workspace/.editerra-racag/output
    3. Default: .editerra-racag/output (relative to cwd)
    """
    if config_path:
        return Path(config_path)
    
    if workspace:
        return workspace / ".editerra-racag" / "output"
    
    return Path(".editerra-racag/output")


def resolve_logs_path(config_path: Optional[str] = None, workspace: Optional[Path] = None) -> Path:
    """
    Resolve the logs directory path.
    
    Priority:
    1. Explicit config_path parameter
    2. workspace/.editerra-racag/logs
    3. Default: .editerra-racag/logs (relative to cwd)
    """
    if config_path:
        return Path(config_path)
    
    if workspace:
        return workspace / ".editerra-racag" / "logs"
    
    return Path(".editerra-racag/logs")


def resolve_collection_name(config_name: Optional[str] = None, workspace: Optional[Path] = None) -> str:
    """
    Resolve the ChromaDB collection name.
    
    Priority:
    1. Explicit config_name parameter
    2. Auto-generate from workspace name
    3. Default: editerra_chunks
    """
    if config_name:
        return config_name
    
    if workspace:
        # Generate collection name from workspace directory name
        name = workspace.name.lower().replace("-", "_").replace(" ", "_")
        # Remove special characters
        name = "".join(c for c in name if c.isalnum() or c == "_")
        return f"{name}_chunks"
    
    return "editerra_chunks"


def get_tree_sitter_lib_path() -> Path:
    """
    Get the path to tree-sitter language libraries.
    
    Returns path relative to editerra_racag package.
    """
    import editerra_racag
    package_root = Path(editerra_racag.__file__).parent
    return package_root / "tree_sitter_languages" / "build" / "my-languages.so"
