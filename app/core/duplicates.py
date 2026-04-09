import logging
from collections import defaultdict
from pathlib import Path
from app.core.hasher import hash_many

logger = logging.getLogger(__name__)


def prepare_duplicate_candidates(root: Path, progress_callback=None) -> list[Path]:
    by_size = defaultdict(list)
    for file in root.rglob("*"):
        if file.is_file():
            by_size[file.stat().st_size].append(file)
            if progress_callback:
                progress_callback(file)
    return [file for files in by_size.values() if len(files) > 1 for file in files]


def find_duplicates(
    duplicates: list[Path], progress_callback=None
) -> dict[str, list[Path]]:
    hashes = hash_many(duplicates, progress_callback=progress_callback)

    by_hash = defaultdict(list)
    for path, h in hashes.items():
        by_hash[h].append(path)

    return {h: paths for h, paths in by_hash.items() if len(paths) > 1}
