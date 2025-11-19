"""
Main engine for Editerra RAC-CAG.

Orchestrates chunking, embedding, indexing, and querying.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from editerra_racag.config import EditerraConfig, get_config
from editerra_racag.llm.factory import get_provider
from editerra_racag.chunking.run_chunkers import run_chunking_pipeline
from editerra_racag.embedding.embed_all import embed_and_store_all
from editerra_racag.retrieval.semantic_retriever import SemanticRetriever
from editerra_racag.reranker.rerank_engine import RerankEngine
from editerra_racag.context.context_assembler import ContextAssembler

logger = logging.getLogger(__name__)


class EditerraEngine:
    """
    Main engine for Editerra RAC-CAG.
    
    Handles the complete pipeline:
    1. Chunking source files
    2. Embedding chunks
    3. Storing in vector database
    4. Querying with semantic search
    5. Reranking results
    6. Assembling context
    """
    
    def __init__(self, workspace: Path, config: Optional[EditerraConfig] = None):
        """
        Initialize the engine.
        
        Args:
            workspace: Path to the workspace/project root
            config: Optional config (will load from workspace if not provided)
        """
        self.workspace = workspace
        self.config = config or get_config(workspace)
        self.llm_provider = get_provider(self.config)
        
        # Initialize components
        self.retriever = SemanticRetriever(
            db_path=str(self.config.db_path),
            collection_name=self.config.collection_name,
            llm_provider=self.llm_provider
        )
        
        self.reranker = RerankEngine(llm_provider=self.llm_provider)
        self.context_assembler = ContextAssembler()
        
        logger.info(f"Engine initialized for workspace: {workspace}")
        logger.info(f"Provider: {self.config.llm_provider}")
        logger.info(f"Collection: {self.config.collection_name}")
    
    def index(self, force: bool = False) -> Dict[str, Any]:
        """
        Index the workspace.
        
        Performs:
        1. Chunking all source files
        2. Generating embeddings
        3. Storing in vector database
        
        Args:
            force: If True, rebuild index even if it exists
        
        Returns:
            Statistics about the indexing operation
        """
        logger.info(f"Starting index of workspace: {self.workspace}")
        
        # Step 1: Chunking
        logger.info("Step 1/2: Chunking source files...")
        chunk_stats = run_chunking_pipeline(
            workspace_root=str(self.workspace),
            output_dir=str(self.config.output_path)
        )
        
        chunks_file = self.config.output_path / "chunks.jsonl"
        if not chunks_file.exists():
            raise FileNotFoundError(f"Chunking failed: {chunks_file} not created")
        
        # Step 2: Embedding and storing
        logger.info("Step 2/2: Embedding and storing in vector database...")
        embed_stats = embed_and_store_all(
            chunks_file=str(chunks_file),
            db_path=str(self.config.db_path),
            collection_name=self.config.collection_name,
            llm_provider=self.llm_provider,
            batch_size=self.config.embedding_batch_size
        )
        
        # Combine statistics
        stats = {
            "workspace": str(self.workspace),
            "chunking": chunk_stats,
            "embedding": embed_stats,
            "collection": self.config.collection_name,
            "provider": self.config.llm_provider
        }
        
        # Save stats
        stats_file = self.config.output_path / "index_stats.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Indexing complete! Stats saved to {stats_file}")
        return stats
    
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        rerank: bool = True,
        context_window: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the codebase.
        
        Args:
            query_text: Natural language query
            top_k: Number of results to return
            rerank: Whether to rerank results (improves quality but slower)
            context_window: Number of surrounding chunks to include
        
        Returns:
            List of relevant code chunks with metadata
        """
        logger.info(f"Query: {query_text}")
        
        # Step 1: Semantic retrieval
        initial_k = top_k * 3 if rerank else top_k
        results = self.retriever.retrieve(
            query=query_text,
            top_k=initial_k
        )
        
        if not results:
            logger.warning("No results found")
            return []
        
        # Step 2: Reranking (optional)
        if rerank and len(results) > top_k:
            logger.info(f"Reranking top {len(results)} results...")
            results = self.reranker.rerank(
                query=query_text,
                chunks=results,
                top_k=top_k
            )
        
        # Step 3: Context assembly
        logger.info("Assembling context...")
        enriched_results = self.context_assembler.assemble(
            chunks=results,
            window_size=context_window
        )
        
        return enriched_results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        stats = {
            "workspace": str(self.workspace),
            "collection": self.config.collection_name,
            "provider": self.config.llm_provider,
            "db_path": str(self.config.db_path),
        }
        
        # Get collection stats
        try:
            collection = self.retriever.collection
            stats["total_chunks"] = collection.count()
            
            # Try to load index stats if available
            stats_file = self.config.output_path / "index_stats.json"
            if stats_file.exists():
                with open(stats_file) as f:
                    index_stats = json.load(f)
                stats["last_index"] = index_stats
        except Exception as e:
            logger.warning(f"Could not get collection stats: {e}")
            stats["total_chunks"] = 0
        
        return stats
    
    def delete_index(self):
        """
        Delete the index (for re-indexing).
        """
        logger.info(f"Deleting index for collection: {self.config.collection_name}")
        
        # Delete ChromaDB collection
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(self.config.db_path))
            client.delete_collection(name=self.config.collection_name)
            logger.info("Collection deleted")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")
        
        # Delete output files
        if self.config.output_path.exists():
            import shutil
            shutil.rmtree(self.config.output_path)
            self.config.output_path.mkdir(parents=True, exist_ok=True)
            logger.info("Output directory cleared")


def create_engine(workspace: Optional[Path] = None) -> EditerraEngine:
    """
    Factory function to create an engine instance.
    
    Args:
        workspace: Path to workspace (defaults to current directory)
    
    Returns:
        EditerraEngine instance
    """
    workspace = workspace or Path.cwd()
    return EditerraEngine(workspace=workspace)
