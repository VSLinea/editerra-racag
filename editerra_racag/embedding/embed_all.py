import json
from typing import Any, Dict, List, Set

from chromadb import PersistentClient

from editerra_racag.chunking.normalize import normalize_chunk
from editerra_racag.embedding.embedder import embed_chunk as embed_document
from editerra_racag.paths import resolve_db_path, resolve_collection_name, resolve_output_path
EXPECTED_EMBEDDING_DIM = 1536


def load_chunks() -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as handle:
        for line in handle:
            raw = json.loads(line)
            normalized = normalize_chunk(raw)
            if normalized:
                chunks.append(normalized)
    return chunks


def build_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    tags = chunk.get("tags")
    if isinstance(tags, list):
        tags_value = ",".join(str(t) for t in tags)
    else:
        tags_value = str(tags or "")

    return {
        "description": chunk.get("description", ""),
        "file_path": chunk.get("file_path", "unknown"),
        "framework": chunk.get("framework", "unknown"),
        "function": chunk.get("function", "unknown"),
        "language": chunk.get("language", "unknown"),
        "lines": f"{chunk.get('start_line', '?')}-{chunk.get('end_line', '?')}",
        "module": chunk.get("module", "unknown"),
        "tags": tags_value,
    }


def _extract_embedding_dim(sample: Dict[str, Any]) -> int:
    embeddings = sample.get("embeddings")
    if embeddings is None or (isinstance(embeddings, (list, tuple)) and len(embeddings) == 0):
        return 0

    first = embeddings[0]
    if isinstance(first, list):
        return len(first)

    if hasattr(first, "__len__"):
        try:
            return len(first)  # type: ignore[arg-type]
        except TypeError:
            return 0

    return 0


def embed_all_chunks(
    chunks: List[Dict[str, Any]], 
    reset: bool = False,
    db_path: str = None,
    collection_name: str = None
) -> None:
    """Legacy function - use embed_and_store_all instead."""
    db_path = db_path or resolve_db_path()
    collection_name = collection_name or resolve_collection_name()
    
    client = PersistentClient(path=db_path)

    if reset:
        try:
            client.delete_collection(name=collection_name)
            print("🧹 Existing collection dropped (reset requested).")
        except Exception:
            print("ℹ️ No existing collection to drop.")

    collection = client.get_or_create_collection(name=collection_name)

    existing_ids: Set[str] = set()

    current_count = collection.count()
    if current_count:
        sample = collection.get(limit=1, include=["embeddings"])
        sample_dim = _extract_embedding_dim(sample)

        if sample_dim and sample_dim != EXPECTED_EMBEDDING_DIM:
            print(
                f"⚠️ Existing embeddings dimension {sample_dim} "
                f"!= expected {EXPECTED_EMBEDDING_DIM}. Resetting collection." 
            )
            client.delete_collection(name=COLLECTION_NAME)
            collection = client.get_or_create_collection(name=COLLECTION_NAME)
        else:
            page_size = 1000
            for offset in range(0, current_count, page_size):
                batch = collection.get(include=[], limit=page_size, offset=offset)
                batch_ids = batch.get("ids", [])
                if batch_ids:
                    existing_ids.update(batch_ids)

    def chunk_id(chunk: Dict[str, Any]) -> str:
        return chunk["chunk_id"]

    remaining = [c for c in chunks if chunk_id(c) not in existing_ids]

    print(f"🔍 Total chunks loaded: {len(chunks)}")
    print(f"🧠 Already embedded: {len(existing_ids)}")
    print(f"➡️  Remaining to embed: {len(remaining)}")

    BATCH = 32
    for i in range(0, len(remaining), BATCH):
        batch = remaining[i:i + BATCH]
        ids: List[str] = []
        docs: List[str] = []
        metas: List[Dict[str, Any]] = []
        embs: List[List[float]] = []

        for c in batch:
            ids.append(chunk_id(c))
            docs.append(c.get("chunk_text", ""))
            metas.append(build_metadata(c))

            embedded = embed_document(c)
            embs.append(embedded["embedding"])

        try:
            collection.add(
                ids=ids,
                documents=docs,
                embeddings=embs,
                metadatas=metas
            )
        except Exception as e:
            print("❌ Batch error:", e)
            print("→ IDs:", ids)

        pct = round(((i + len(batch)) / len(remaining)) * 100, 2)
        print(f"🟦 Batch {i//BATCH + 1}: {i+len(batch)}/{len(remaining)} ({pct}%)")

    final_count = collection.count()
    print("🎉 Embedding run complete.")
    print(f"📦 Collection now holds {final_count} embeddings.")


def embed_and_store_all(
    chunks_file: str,
    db_path: str,
    collection_name: str,
    llm_provider,
    batch_size: int = 100
) -> Dict[str, int]:
    """
    Main entry point for embedding pipeline (used by EditerraEngine).
    
    Args:
        chunks_file: Path to chunks.jsonl file
        db_path: Path to ChromaDB storage
        collection_name: Name of the collection
        llm_provider: LLM provider for embeddings
        batch_size: Batch size for embedding
    
    Returns:
        Statistics about the embedding operation
    """
    from pathlib import Path
    import json
    
    # Load chunks from file
    chunks = []
    with open(chunks_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    
    # Embed using the llm_provider
    client = PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name)
    
    embedded_count = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [chunk.get("content", "") for chunk in batch]
        
        # Get embeddings from provider
        embeddings = llm_provider.embed(texts)
        
        # Prepare for storage
        ids = [chunk.get("id", f"chunk_{i+j}") for j, chunk in enumerate(batch)]
        metadatas = [build_metadata(chunk) for chunk in batch]
        documents = texts
        
        # Store in ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        embedded_count += len(batch)
    
    return {
        "total_embedded": embedded_count,
        "collection": collection_name,
        "db_path": db_path
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Embed RACAG chunks into Chroma")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop existing collection before embedding to avoid stale data.",
    )
    args = parser.parse_args()

    chunks = load_chunks()
    embed_all_chunks(chunks, reset=args.reset)
