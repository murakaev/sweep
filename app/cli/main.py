import typer
from pathlib import Path

from app.core.duplicates import prepare_duplicate_candidates, find_duplicates
from app.ui.duplicates import show_duplicates
from app.ui.progress import progress_tracker

app = typer.Typer()


@app.command()
def duplicates(
    path: Path = typer.Argument(
        ..., exists=True, file_okay=False, dir_okay=True, help="Path to the directory"
    ),
    detail: bool = typer.Option(
        False, "--detail", help="Show detailed list of duplicates"
    ),
    delete: bool = typer.Option(
        False, "--delete", help="Delete duplicate files, keeping one copy"
    ),
):
    """
    Find duplicate files in the specified directory.
    """
    with progress_tracker() as tracker:
        scan_task = tracker.add_task("Scanning files...", total=None)
        duplicate_candidates = prepare_duplicate_candidates(
            path,
            progress_callback=lambda f: tracker.advance(
                scan_task, "Scanning file", f.name
            ),
        )
        tracker.complete(
            scan_task, f"Found {len(duplicate_candidates)} potential duplicates"
        )

        hash_task = tracker.add_task(
            "Hashing files...", total=len(duplicate_candidates)
        )
        dups = find_duplicates(
            duplicate_candidates,
            progress_callback=lambda f: tracker.advance(
                hash_task, "Hashing file", f.name
            ),
        )
        tracker.complete(hash_task, f"Found {len(dups)} duplicate groups")

    if dups:
        show_duplicates(path, dups, detail)


if __name__ == "__main__":
    app()
