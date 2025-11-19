"""
LLM Provider Factory
===================

Creates the appropriate LLM provider based on configuration.
"""

from typing import Dict, Any

from editerra_racag.config import EditerraConfig
from editerra_racag.llm.base import LLMProvider
from editerra_racag.llm.providers import OpenAIProvider, OllamaProvider


def get_provider(config: EditerraConfig) -> LLMProvider:
    """
    Get LLM provider instance based on configuration.
    
    Args:
        config: Editerra configuration object
    
    Returns:
        LLMProvider instance
    
    Raises:
        ValueError: If provider is unknown or not configured
    """
    provider_name = config.llm_provider.lower()
    provider_config = config.get_provider_config()
    
    if provider_name == "openai":
        return OpenAIProvider(provider_config)
    
    elif provider_name == "ollama":
        return OllamaProvider(provider_config)
    
    # Future providers
    elif provider_name == "anthropic":
        raise NotImplementedError("Anthropic provider coming soon!")
    
    elif provider_name == "azure":
        raise NotImplementedError("Azure OpenAI provider coming soon!")
    
    elif provider_name == "vertex":
        raise NotImplementedError("Google Vertex AI provider coming soon!")
    
    elif provider_name == "cohere":
        raise NotImplementedError("Cohere provider coming soon!")
    
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. "
            f"Supported providers: openai, ollama"
        )


# Global provider instance (lazy-loaded)
_global_provider: LLMProvider | None = None


def get_global_provider(config: EditerraConfig | None = None) -> LLMProvider:
    """
    Get or create global provider instance.
    
    Args:
        config: Editerra configuration. If None, uses default config.
    
    Returns:
        LLMProvider instance
    """
    global _global_provider
    
    if _global_provider is None or config is not None:
        from editerra_racag.config import get_config
        if config is None:
            config = get_config()
        _global_provider = get_provider(config)
    
    return _global_provider
