"""
Ollama LLM Provider
==================

Implementation using Ollama for local, free LLM inference.
"""

from typing import List, Dict, Any
import logging
import requests

from editerra_racag.llm.base import LLMProvider


logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama implementation of LLM provider (local, free)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.embedding_model = config.get("embedding_model", "nomic-embed-text")
        self.rerank_model = config.get("rerank_model", "llama3.1:8b")
        
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                logger.warning("Ollama server not responding. Is it running?")
        except Exception as e:
            logger.warning(f"Cannot connect to Ollama at {self.base_url}: {e}")
            logger.info("Install Ollama from https://ollama.ai or change llm_provider in config")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama."""
        if not texts:
            return []
        
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embeddings.append(data.get("embedding", []))
                else:
                    logger.error(f"Ollama embedding failed: {response.text}")
                    embeddings.append([])
            
            except Exception as e:
                logger.error(f"Ollama embedding request failed: {e}")
                embeddings.append([])
        
        return embeddings
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
    
    def rerank(self, query: str, candidates: List[str]) -> List[float]:
        """
        Score candidates using local LLM.
        """
        if not candidates:
            return []
        
        try:
            prompt = self._build_rerank_prompt(query, candidates)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.rerank_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "num_predict": len(candidates) * 10
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                scores = self._parse_scores(response_text, len(candidates))
                return scores
            else:
                logger.warning(f"Ollama reranking failed: {response.text}")
                return [0.5] * len(candidates)
        
        except Exception as e:
            logger.warning(f"Ollama reranking failed: {e}. Using neutral scores.")
            return [0.5] * len(candidates)
    
    def _build_rerank_prompt(self, query: str, candidates: List[str]) -> str:
        """Build prompt for reranking."""
        prompt_parts = [
            f"Query: {query}",
            "",
            "Rate each code snippet's relevance to the query (0-1 scale).",
            "Return ONLY the scores as space-separated numbers.",
            "",
            "Snippets:",
        ]
        
        for i, candidate in enumerate(candidates, 1):
            truncated = candidate[:400] + "..." if len(candidate) > 400 else candidate
            prompt_parts.append(f"\n[{i}] {truncated}")
        
        prompt_parts.append("\n\nScores:")
        
        return "\n".join(prompt_parts)
    
    def _parse_scores(self, scores_text: str, expected_count: int) -> List[float]:
        """Parse scores from response."""
        try:
            import re
            numbers = re.findall(r'0?\.\d+|\d+\.?\d*', scores_text)
            scores = [float(n) for n in numbers[:expected_count]]
            scores = [max(0.0, min(1.0, s)) for s in scores]
            
            while len(scores) < expected_count:
                scores.append(0.5)
            
            return scores[:expected_count]
        
        except Exception as e:
            logger.warning(f"Failed to parse Ollama scores: {e}")
            return [0.5] * expected_count
    
    @property
    def embedding_dimensions(self) -> int:
        """Return embedding dimensionality (nomic-embed-text uses 768)."""
        return 768
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "ollama"
