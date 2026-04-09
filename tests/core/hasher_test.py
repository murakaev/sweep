import sys
import pytest
from app.core.hasher import hash_file, hash_many


def test_same_content_same_hash(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_bytes(b"hello world")
    f2.write_bytes(b"hello world")

    assert hash_file(f1) == hash_file(f2)


def test_different_content_different_hash(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_bytes(b"hello")
    f2.write_bytes(b"world")

    assert hash_file(f1) != hash_file(f2)


def test_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")

    assert hash_file(f) is not None


def test_hash_many_returns_all(tmp_path):
    files = []
    for i in range(5):
        f = tmp_path / f"file_{i}.txt"
        f.write_bytes(f"content {i}".encode())
        files.append(f)

    result = hash_many(files)

    assert len(result) == 5
    assert all(p in result for p in files)


def test_hash_many_parallel_matches_single(tmp_path):
    files = []
    for i in range(3):
        f = tmp_path / f"file_{i}.txt"
        f.write_bytes(f"data {i}".encode())
        files.append(f)

    parallel = hash_many(files)
    single = {f: hash_file(f) for f in files}

    assert parallel == single


def test_nonexistent_file_returns_none(tmp_path):
    ghost = tmp_path / "does_not_exist_xyz.txt"

    assert hash_file(ghost) is None


@pytest.mark.skipif(
    sys.platform == "win32", reason="chmod doesn't work reliably on Windows"
)
def test_no_permission_returns_none(tmp_path):
    f = tmp_path / "locked.txt"
    f.write_bytes(b"secret")
    f.chmod(0o000)

    try:
        assert hash_file(f) is None
    finally:
        f.chmod(0o644)


def test_hash_many_with_missing_file(tmp_path):
    good = tmp_path / "good.txt"
    good.write_bytes(b"data")
    ghost = tmp_path / "ghost_file_xyz.txt"

    result = hash_many([good, ghost])

    assert len(result) == 2
    assert result[good] is not None
    assert result[ghost] is None


def test_hash_many_all_missing(tmp_path):
    ghosts = [tmp_path / f"ghost_{i}.txt" for i in range(3)]

    result = hash_many(ghosts)

    assert len(result) == 3
    assert all(v is None for v in result.values())


def test_progress_callback_called_for_error_files(tmp_path):
    ghost = tmp_path / "ghost_callback_xyz.txt"
    called_with = []

    hash_many([ghost], progress_callback=lambda p: called_with.append(p))

    assert ghost in called_with
