"""
Editerra RAC-CAG Configuration System
=====================================

Handles workspace-specific and global configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


DEFAULT_CONFIG = {
    "version": 1,
    "project_name": None,  # Auto-detected from workspace
    "collection_name": None,  # Auto-generated
    
    # Paths (relative to workspace root)
    "db_path": ".editerra-racag/db",
    "output_path": ".editerra-racag/output",
    "cache_path": ".editerra-racag/cache",
    
    # Indexing settings
    "watch_enabled": True,
    "watch_paths": ["src", "lib", "app"],
    "exclude_dirs": [
        "node_modules", ".git", "build", "dist", "__pycache__",
        "venv", "env", ".venv", "racag_env",
        "target", ".next", ".nuxt",
        "DerivedData", "Pods", ".build", ".swiftpm",
    ],
    "include_extensions": [
        ".py", ".ts", ".js", ".tsx", ".jsx",
        ".swift", ".java", ".go", ".rs",
        ".c", ".cpp", ".h", ".hpp",
        ".md", ".json", ".yaml", ".yml",
    ],
    
    # LLM Provider
    "llm_provider": "openai",  # openai, anthropic, azure, ollama, vertex, cohere
    
    # OpenAI settings
    "openai": {
        "api_key": "${OPENAI_API_KEY}",
        "embedding_model": "text-embedding-3-large",
        "rerank_model": "gpt-4o-mini",
        "embedding_dimensions": 1536,
    },
    
    # Anthropic settings
    "anthropic": {
        "api_key": "${ANTHROPIC_API_KEY}",
        "embedding_model": "voyage-3",
        "rerank_model": "claude-3-haiku-20240307",
    },
    
    # Azure OpenAI settings
    "azure": {
        "api_key": "${AZURE_OPENAI_API_KEY}",
        "endpoint": "${AZURE_OPENAI_ENDPOINT}",
        "deployment_name": "gpt-4",
        "api_version": "2024-02-15-preview",
    },
    
    # Ollama settings (local, free)
    "ollama": {
        "base_url": "http://localhost:11434",
        "embedding_model": "nomic-embed-text",
        "rerank_model": "llama3.1:8b",
    },
    
    # Google Vertex AI settings
    "vertex": {
        "project_id": "${GCP_PROJECT_ID}",
        "location": "us-central1",
        "embedding_model": "text-embedding-004",
        "rerank_model": "gemini-1.5-flash",
    },
    
    # Cohere settings
    "cohere": {
        "api_key": "${COHERE_API_KEY}",
        "embedding_model": "embed-english-v3.0",
        "rerank_model": "command-r",
    },
    
    # Embedding settings
    "embedding_batch_size": 32,
    "embedding_cache": True,
    
    # Query settings
    "retrieve_k": 40,
    "final_k": 5,
    
    # API settings (optional)
    "api_enabled": False,
    "api_port": 8009,
    "api_host": "127.0.0.1",
}


class EditerraConfig:
    """Configuration manager for Editerra RAC-CAG."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            workspace_root: Root directory of the workspace. Defaults to current directory.
        """
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.config_file = self.workspace_root / ".editerra-racag.yaml"
        self.config = self._load_config()
        self._resolve_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            # Merge with defaults
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
        
        # Return default config
        config = DEFAULT_CONFIG.copy()
        
        # Auto-detect project name
        if not config.get("project_name"):
            config["project_name"] = self.workspace_root.name
        
        # Auto-generate collection name
        if not config.get("collection_name"):
            config["collection_name"] = f"{self.workspace_root.name.lower()}_chunks"
        
        return config
    
    def _resolve_env_vars(self):
        """Resolve environment variables in config values."""
        def resolve_value(value: Any) -> Any:
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            return value
        
        self.config = resolve_value(self.config)
    
    def save(self):
        """Save current configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    @property
    def db_path(self) -> Path:
        """Get absolute path to database directory."""
        return self.workspace_root / self.config["db_path"]
    
    @property
    def output_path(self) -> Path:
        """Get absolute path to output directory."""
        return self.workspace_root / self.config["output_path"]
    
    @property
    def cache_path(self) -> Path:
        """Get absolute path to cache directory."""
        return self.workspace_root / self.config["cache_path"]
    
    @property
    def collection_name(self) -> str:
        """Get ChromaDB collection name."""
        return self.config.get("collection_name", f"{self.workspace_root.name}_chunks")
    
    @property
    def project_name(self) -> str:
        """Get project name."""
        return self.config.get("project_name", self.workspace_root.name)
    
    @property
    def llm_provider(self) -> str:
        """Get LLM provider name."""
        return self.config.get("llm_provider", "openai")
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Get configuration for current LLM provider."""
        provider = self.llm_provider
        return self.config.get(provider, {})
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to config."""
        return self.config[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value with default."""
        return self.config.get(key, default)


# Global config instance (lazy-loaded)
_global_config: Optional[EditerraConfig] = None


def get_config(workspace_root: Optional[Path] = None) -> EditerraConfig:
    """
    Get or create global configuration instance.
    
    Args:
        workspace_root: Workspace root directory. If None, uses current directory.
    
    Returns:
        EditerraConfig instance
    """
    global _global_config
    if _global_config is None or workspace_root is not None:
        _global_config = EditerraConfig(workspace_root)
    return _global_config


def init_config(workspace_root: Optional[Path] = None) -> EditerraConfig:
    """
    Initialize configuration file in workspace.
    
    Args:
        workspace_root: Workspace root directory.
    
    Returns:
        EditerraConfig instance
    """
    config = EditerraConfig(workspace_root)
    if not config.config_file.exists():
        config.save()
        print(f"✅ Created configuration file: {config.config_file}")
    else:
        print(f"⚠️  Configuration file already exists: {config.config_file}")
    return config
