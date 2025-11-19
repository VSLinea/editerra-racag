"""
LLM Provider Base Interface
===========================

Abstract base class for all LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        pass
    
    @abstractmethod
    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
        
        Returns:
            Embedding vector (list of floats)
        """
        pass
    
    @abstractmethod
    def rerank(self, query: str, candidates: List[str]) -> List[float]:
        """
        Score candidates for relevance to query.
        
        Args:
            query: Search query
            candidates: List of candidate texts to score
        
        Returns:
            List of relevance scores (0-1, higher is better)
        """
        pass
    
    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        """Return the dimensionality of embeddings."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass
