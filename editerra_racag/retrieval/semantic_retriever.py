import math
from typing import List, Dict
from chromadb import PersistentClient

class SemanticRetriever:
    """Semantic search using ChromaDB."""
    
    def __init__(self, db_path: str, collection_name: str, llm_provider=None):
        self.db_path = db_path
        self.collection_name = collection_name
        self.llm_provider = llm_provider
        self.client = PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        # Embed the query
        query_embedding = self.llm_provider.embed_single(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        chunks = []
        if results and results['ids']:
            for i in range(len(results['ids'][0])):
                chunk = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'score': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                }
                # Extract common fields from metadata
                metadata = chunk['metadata']
                chunk['file_path'] = metadata.get('file_path', 'unknown')
                chunk['start_line'] = int(metadata.get('lines', '0-0').split('-')[0])
                chunk['end_line'] = int(metadata.get('lines', '0-0').split('-')[1])
                chunks.append(chunk)
        
        return chunks

# Legacy global instances for backward compatibility
_default_client = None
_default_collection = None

def _get_default_collection():
    global _default_client, _default_collection
    if _default_client is None:
        from editerra_racag.paths import resolve_db_path, resolve_collection_name
        _default_client = PersistentClient(path=resolve_db_path())
        _default_collection = _default_client.get_or_create_collection(name=resolve_collection_name())
    return _default_collection

collection = property(lambda self: _get_default_collection())

# ---------- BASIC COSINE SIMILARITY ----------
def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

# ---------- MAIN SEARCH USING CHROMA ----------
def semantic_search(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """
    Runs vector similarity search over ChromaDB using the RACAG unified metadata format.
    """

    # Query Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "documents", "distances"]
    )

    out = []
    ids = results.get("ids", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for chunk_id, meta, dist in zip(ids, metas, dists):
        out.append({
            "chunk_id": chunk_id,
            "score": 1 / (1 + dist),  # convert distance → similarity
            "metadata": meta
        })

    return out