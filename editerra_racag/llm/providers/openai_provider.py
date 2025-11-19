"""
OpenAI LLM Provider
==================

Implementation using OpenAI's API for embeddings and reranking.
"""

from typing import List, Dict, Any
import logging

from openai import OpenAI

from editerra_racag.llm.base import LLMProvider


logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        api_key = config.get("api_key")
        if not api_key or api_key.startswith("${"):
            raise ValueError(
                "OpenAI API key not configured. Set OPENAI_API_KEY environment variable "
                "or configure it in .editerra-racag.yaml"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = config.get("embedding_model", "text-embedding-3-large")
        self.rerank_model = config.get("rerank_model", "gpt-4o-mini")
        self._embedding_dims = config.get("embedding_dimensions", 1536)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
    
    def rerank(self, query: str, candidates: List[str]) -> List[float]:
        """
        Score candidates using GPT model.
        
        Sends a prompt asking the model to score each candidate's relevance.
        """
        if not candidates:
            return []
        
        try:
            # Build reranking prompt
            prompt = self._build_rerank_prompt(query, candidates)
            
            response = self.client.chat.completions.create(
                model=self.rerank_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=len(candidates) * 5,  # Rough estimate
                temperature=0,
            )
            
            # Parse scores from response
            scores_text = response.choices[0].message.content or ""
            scores = self._parse_scores(scores_text, len(candidates))
            
            return scores
        
        except Exception as e:
            logger.warning(f"OpenAI reranking failed: {e}. Using neutral scores.")
            # Return neutral scores if reranking fails
            return [0.5] * len(candidates)
    
    def _build_rerank_prompt(self, query: str, candidates: List[str]) -> str:
        """Build prompt for reranking candidates."""
        prompt_parts = [
            f"Query: {query}",
            "",
            "Rate the relevance of each code snippet to the query on a scale of 0-1.",
            "Return ONLY the scores as a space-separated list (e.g., '0.9 0.7 0.3').",
            "",
            "Code snippets:",
        ]
        
        for i, candidate in enumerate(candidates, 1):
            # Truncate very long candidates
            truncated = candidate[:500] + "..." if len(candidate) > 500 else candidate
            prompt_parts.append(f"\n[{i}] {truncated}")
        
        prompt_parts.append("\n\nScores:")
        
        return "\n".join(prompt_parts)
    
    def _parse_scores(self, scores_text: str, expected_count: int) -> List[float]:
        """Parse scores from LLM response."""
        try:
            # Try to extract numbers from response
            import re
            numbers = re.findall(r'0?\.\d+|\d+\.?\d*', scores_text)
            scores = [float(n) for n in numbers[:expected_count]]
            
            # Normalize to 0-1 range
            scores = [max(0.0, min(1.0, s)) for s in scores]
            
            # Pad with neutral scores if needed
            while len(scores) < expected_count:
                scores.append(0.5)
            
            return scores[:expected_count]
        
        except Exception as e:
            logger.warning(f"Failed to parse rerank scores: {e}")
            return [0.5] * expected_count
    
    @property
    def embedding_dimensions(self) -> int:
        """Return embedding dimensionality."""
        return self._embedding_dims
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "openai"
