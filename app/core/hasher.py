import xxhash
import logging
from dataclasses import dataclass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class HasherConfig:
    """Configuration for hashing."""

    chunk_size: int = 8192
    max_workers: int = 4


def hash_file(file_path: Path, config: HasherConfig | None = None) -> str | None:
    """Hash a file using xxhash."""

    if config is None:
        config = HasherConfig()
    try:
        hasher = xxhash.xxh64()
        with file_path.open("rb") as f:
            while chunk := f.read(config.chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return None


def hash_many(
    file_paths: list[Path],
    config: HasherConfig | None = None,
    progress_callback: Callable[[Path], None] | None = None,
) -> dict[Path, str | None]:
    """Hash multiple files concurrently using xxhash."""

    if config is None:
        config = HasherConfig()
    results: dict[Path, str | None] = {}
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = {executor.submit(hash_file, p, config): p for p in file_paths}
        for future in as_completed(futures):
            path = futures[future]
            results[path] = future.result()
            if progress_callback:
                progress_callback(path)
    return results
