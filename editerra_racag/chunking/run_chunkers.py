import json
import time
from pathlib import Path

from editerra_racag.chunking.code_chunker import extract_code_chunks
from editerra_racag.chunking.markdown_chunker import chunk_markdown
from editerra_racag.chunking.json_chunker import chunk_json
from editerra_racag.chunking.normalize import normalize_chunk

# ============================================================
# OPTION B — SMART PROJECT‑LEVEL FILTER
# ============================================================

ALLOWED_EXTS = {
    ".py", ".swift", ".md", ".json", ".ts", ".js", ".yaml", ".yml", ".sh", ".txt"
}

EXCLUDED_DIRS = {
    # Frameworks & virtual envs
    "racag_env", "venv", ".git", "__pycache__", "node_modules",
    "Pods", ".build", ".swiftpm",

    # Build products
    "DerivedData", "build", "dist", "out", "target",

    # Agent artefacts / dead folders
    "dev_agents.DISABLED", "LOGS", "container", "mock-server",
    "Tools", "plugins", ".cache", ".mypy_cache", ".pytest_cache",

    # Very large vendor deps
    "tree_sitter_languages"
}

EXCLUDED_FILE_PATTERNS = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tgz", ".tar",
    ".dylib", ".so", ".o", ".bin", ".db", ".sqlite", ".lock", ".log",
    ".xcworkspace", ".xcuserstate", ".xcuserdata"
}

# ============================================================

def safe_print(msg: str):
    try:
        print(msg, flush=True)
    except Exception:
        pass


def should_process(path: Path) -> bool:
    """True if file should be chunked."""
    if not path.is_file():
        return False

    # Directory-level exclusion
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False

    # Extension-level exclusion
    if path.suffix.lower() in EXCLUDED_FILE_PATTERNS:
        return False

    # Allow only whitelisted extensions
    return path.suffix.lower() in ALLOWED_EXTS


# ============================================================

def validate_chunk(chunk: dict) -> dict | None:
    """Guarantees minimal required structure."""
    if not isinstance(chunk, dict):
        return None

    required = {
        "chunk_id": "",
        "chunk_text": "",
        "language": "unknown",
        "framework": "unknown",
        "module": "unknown",
        "function": "unknown",
        "file_path": "unknown",
        "start_line": 0,
        "end_line": 0,
        "tags": []
    }

    fixed = {k: chunk.get(k, v) for k, v in required.items()}
    return fixed


# ============================================================

def run_chunkers(repo_root: Path):
    safe_print("🚀 RACAG chunking pipeline running")
    safe_print(f"📂 Repository: {repo_root}")

    all_chunks = []
    error_log = []

    scanned = 0
    start = time.time()

    for path in repo_root.rglob("*"):
        if not should_process(path):
            continue

        scanned += 1
        if scanned % 200 == 0:
            safe_print(f"   → Scanned {scanned:,} files...")

        try:
            if path.suffix == ".swift":
                chunks = extract_code_chunks(str(path))
            elif path.suffix == ".md":
                chunks = chunk_markdown(str(path))
            elif path.suffix == ".json":
                chunks = chunk_json(str(path))
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
                chunks = [{
                    "chunk_id": f"{path.name}::all",
                    "chunk_text": text,
                    "start_line": 0,
                    "end_line": len(text.splitlines()),
                    "file_path": str(path)
                }]
        except Exception as e:
            msg = f"{path}: {e}"
            safe_print(f"⚠️ Error chunking {msg}")
            error_log.append(msg)
            continue

        for c in chunks:
            norm = normalize_chunk(c)
            validated = validate_chunk(norm)
            if validated:
                all_chunks.append(validated)

    elapsed = time.time() - start
    safe_print(f"⏱ Total scan time: {elapsed:.2f}s")
    safe_print(f"🔢 Total chunk count: {len(all_chunks):,}")
    safe_print(f"❗ Errors encountered: {len(error_log)}")

    return all_chunks, error_log


# ============================================================

def save_outputs(chunks, errors, out_dir: Path = None):
    chunks = [c for c in chunks if c is not None]

    if out_dir is None:
        out_dir = Path(".editerra-racag/output")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save chunks.jsonl
    chunks_path = out_dir / "chunks.jsonl"
    with open(chunks_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Summary
    meta = {
        "total_chunks": len(chunks),
        "languages": {},
        "frameworks": {}
    }

    for c in chunks:
        lang = c.get("language", "unknown")
        fw = c.get("framework", "unknown")
        meta["languages"][lang] = meta["languages"].get(lang, 0) + 1
        meta["frameworks"][fw] = meta["frameworks"].get(fw, 0) + 1

    meta_path = out_dir / "meta_summary.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Error log
    err_path = out_dir / "errors.jsonl"
    with open(err_path, "w", encoding="utf-8") as f:
        for e in errors:
            f.write(e + "\n")

    safe_print(f"📦 Saved chunks: {chunks_path}")
    safe_print(f"📊 Summary:      {meta_path}")
    safe_print(f"⚠️ Error log:     {err_path}")


# ============================================================

def run_chunking_pipeline(workspace_root: str, output_dir: str) -> dict:
    """
    Main entry point for chunking pipeline (used by EditerraEngine).
    
    Args:
        workspace_root: Path to workspace root
        output_dir: Path to output directory
    
    Returns:
        Statistics about chunking operation
    """
    repo = Path(workspace_root)
    out_dir = Path(output_dir)
    
    chunks, errors = run_chunkers(repo)
    save_outputs(chunks, errors, out_dir)
    
    # Return stats
    return {
        "total_chunks": len(chunks),
        "errors": len(errors),
        "output_dir": str(out_dir)
    }


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[2]
    chunks, errors = run_chunkers(repo)
    save_outputs(chunks, errors)
    safe_print("🎉 Chunking complete.")
