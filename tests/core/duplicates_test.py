from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.duplicates import prepare_duplicate_candidates, find_duplicates


def make_file(tmp_path: Path, name: str, content: bytes) -> Path:
    """Create a real file with given content and return its Path."""
    p = tmp_path / name
    p.write_bytes(content)
    return p


class TestPrepareDuplicateCandidates:
    def test_returns_empty_list_when_directory_is_empty(self, tmp_path):
        result = prepare_duplicate_candidates(tmp_path)
        assert result == []

    def test_returns_empty_list_for_single_file(self, tmp_path):
        make_file(tmp_path, "only.txt", b"hello")
        result = prepare_duplicate_candidates(tmp_path)
        assert result == []

    def test_returns_files_with_same_size(self, tmp_path):
        a = make_file(tmp_path, "a.txt", b"abc")
        b = make_file(tmp_path, "b.txt", b"xyz")
        result = prepare_duplicate_candidates(tmp_path)
        assert set(result) == {a, b}

    def test_excludes_unique_size_files(self, tmp_path):
        make_file(tmp_path, "small.txt", b"hi")
        make_file(tmp_path, "large.txt", b"hello world!")
        result = prepare_duplicate_candidates(tmp_path)
        assert result == []

    def test_mixed_files_only_same_size_returned(self, tmp_path):
        a = make_file(tmp_path, "a.txt", b"abc")
        b = make_file(tmp_path, "b.txt", b"xyz")
        make_file(tmp_path, "unique.txt", b"unique content here")
        result = prepare_duplicate_candidates(tmp_path)
        assert set(result) == {a, b}

    def test_works_recursively_in_subdirectories(self, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        a = make_file(tmp_path, "a.txt", b"abc")
        b = make_file(sub, "b.txt", b"xyz")
        result = prepare_duplicate_candidates(tmp_path)
        assert set(result) == {a, b}

    def test_directories_are_not_included(self, tmp_path):
        (tmp_path / "subdir").mkdir()
        make_file(tmp_path, "only.txt", b"alone")
        result = prepare_duplicate_candidates(tmp_path)
        assert result == []

    def test_progress_callback_called_for_each_file(self, tmp_path):
        a = make_file(tmp_path, "a.txt", b"abc")
        b = make_file(tmp_path, "b.txt", b"xyz")
        callback = MagicMock()
        prepare_duplicate_candidates(tmp_path, progress_callback=callback)
        assert callback.call_count == 2
        called_paths = {c.args[0] for c in callback.call_args_list}
        assert called_paths == {a, b}

    def test_progress_callback_not_required(self, tmp_path):
        make_file(tmp_path, "a.txt", b"abc")
        make_file(tmp_path, "b.txt", b"xyz")
        result = prepare_duplicate_candidates(tmp_path)
        assert len(result) == 2

    def test_three_files_same_size_all_returned(self, tmp_path):
        a = make_file(tmp_path, "a.txt", b"111")
        b = make_file(tmp_path, "b.txt", b"222")
        c = make_file(tmp_path, "c.txt", b"333")
        result = prepare_duplicate_candidates(tmp_path)
        assert set(result) == {a, b, c}


class TestFindDuplicates:
    def _make_paths(self, *names: str) -> list[Path]:
        return [Path(name) for name in names]

    @patch("app.core.duplicates.hash_many")
    def test_returns_empty_dict_when_no_duplicates(self, mock_hash_many):
        paths = self._make_paths("a.txt", "b.txt")
        mock_hash_many.return_value = {
            Path("a.txt"): "hash_a",
            Path("b.txt"): "hash_b",
        }
        result = find_duplicates(paths)
        assert result == {}

    @patch("app.core.duplicates.hash_many")
    def test_groups_files_with_same_hash(self, mock_hash_many):
        paths = self._make_paths("a.txt", "b.txt")
        mock_hash_many.return_value = {
            Path("a.txt"): "same_hash",
            Path("b.txt"): "same_hash",
        }
        result = find_duplicates(paths)
        assert "same_hash" in result
        assert set(result["same_hash"]) == {Path("a.txt"), Path("b.txt")}

    @patch("app.core.duplicates.hash_many")
    def test_multiple_duplicate_groups(self, mock_hash_many):
        paths = self._make_paths("a.txt", "b.txt", "c.txt", "d.txt")
        mock_hash_many.return_value = {
            Path("a.txt"): "hash_1",
            Path("b.txt"): "hash_1",
            Path("c.txt"): "hash_2",
            Path("d.txt"): "hash_2",
        }
        result = find_duplicates(paths)
        assert set(result.keys()) == {"hash_1", "hash_2"}
        assert set(result["hash_1"]) == {Path("a.txt"), Path("b.txt")}
        assert set(result["hash_2"]) == {Path("c.txt"), Path("d.txt")}

    @patch("app.core.duplicates.hash_many")
    def test_excludes_unique_hashes(self, mock_hash_many):
        paths = self._make_paths("a.txt", "b.txt", "c.txt")
        mock_hash_many.return_value = {
            Path("a.txt"): "shared",
            Path("b.txt"): "shared",
            Path("c.txt"): "unique",
        }
        result = find_duplicates(paths)
        assert "unique" not in result
        assert "shared" in result

    @patch("app.core.duplicates.hash_many")
    def test_returns_empty_dict_for_empty_input(self, mock_hash_many):
        mock_hash_many.return_value = {}
        result = find_duplicates([])
        assert result == {}

    @patch("app.core.duplicates.hash_many")
    def test_passes_progress_callback_to_hash_many(self, mock_hash_many):
        mock_hash_many.return_value = {}
        callback = MagicMock()
        find_duplicates([], progress_callback=callback)
        mock_hash_many.assert_called_once_with([], progress_callback=callback)

    @patch("app.core.duplicates.hash_many")
    def test_passes_paths_to_hash_many(self, mock_hash_many):
        mock_hash_many.return_value = {}
        paths = self._make_paths("x.txt", "y.txt")
        find_duplicates(paths)
        mock_hash_many.assert_called_once_with(paths, progress_callback=None)

    @patch("app.core.duplicates.hash_many")
    def test_three_files_same_hash_all_grouped(self, mock_hash_many):
        paths = self._make_paths("a.txt", "b.txt", "c.txt")
        mock_hash_many.return_value = {
            Path("a.txt"): "triple",
            Path("b.txt"): "triple",
            Path("c.txt"): "triple",
        }
        result = find_duplicates(paths)
        assert set(result["triple"]) == {Path("a.txt"), Path("b.txt"), Path("c.txt")}
