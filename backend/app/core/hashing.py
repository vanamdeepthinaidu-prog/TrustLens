import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Tuple, List, Optional

def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    """
    Compute cryptographic digest of raw byte sequence.
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()

def hash_file(filepath: str | Path, algorithm: str = "sha256", chunk_size: int = 65536) -> str:
    """
    Compute cryptographic digest of a file using buffered streaming.
    Memory efficient for large model weights and datasets.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hashing: {filepath}")
    
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def canonicalize_json(data: Any) -> str:
    """
    Produce canonical JSON string with sorted keys, compact separators, and UTF-8 encoding.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str
    )

def hash_json(data: Any, algorithm: str = "sha256") -> str:
    """
    Compute deterministic cryptographic hash of arbitrary JSON-serializable data.
    Ensures canonical formatting (sorted keys, compact separators, UTF-8).
    """
    canonical_json = canonicalize_json(data)
    return hash_bytes(canonical_json.encode("utf-8"), algorithm=algorithm)

def hash_directory(
    dirpath: str | Path,
    algorithm: str = "sha256",
    ignore_patterns: Optional[List[str]] = None
) -> Tuple[str, Dict[str, str]]:
    """
    Deterministically hash an entire directory tree.
    Algorithm:
      1. Discover all files recursively (excluding common temporary/meta files).
      2. Normalize relative paths using forward slashes.
      3. Sort relative paths lexicographically.
      4. Compute hash_file for each file.
      5. Construct canonical manifest: '<rel_path>:<file_hash>\\n'.
      6. Hash the manifest to produce the overall directory hash.
    
    Returns:
      (root_directory_hash, manifest_dictionary)
    """
    root = Path(dirpath)
    if not root.is_dir():
        raise NotADirectoryError(f"Directory not found for hashing: {dirpath}")
    
    default_ignores = [
        "__pycache__", ".git", ".DS_Store", "Thumbs.db", ".pytest_cache"
    ]
    ignores = set(default_ignores + (ignore_patterns or []))
    
    manifest: Dict[str, str] = {}
    
    all_files: List[Tuple[str, Path]] = []
    for dirpath_str, dirnames, filenames in os.walk(root):
        # Filter directories in-place to prevent traversing ignored dirs
        dirnames[:] = [d for d in dirnames if d not in ignores]
        
        current_dir = Path(dirpath_str)
        for fname in filenames:
            if any(ign in fname for ign in ignores):
                continue
            full_path = current_dir / fname
            rel_path = full_path.relative_to(root).as_posix()
            all_files.append((rel_path, full_path))
    
    # Strictly sort relative paths alphabetically
    all_files.sort(key=lambda item: item[0])
    
    manifest_lines = []
    for rel_path, full_path in all_files:
        f_hash = hash_file(full_path, algorithm=algorithm)
        manifest[rel_path] = f_hash
        manifest_lines.append(f"{rel_path}:{f_hash}")
    
    canonical_manifest_text = "\n".join(manifest_lines) + ("\n" if manifest_lines else "")
    dir_hash = hash_bytes(canonical_manifest_text.encode("utf-8"), algorithm=algorithm)
    
    return dir_hash, manifest
