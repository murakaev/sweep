from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from app.ui.base import panel_dim, fmt_success

console = Console()


def show_duplicates(
    path: Path, duplicates: dict[str, list[Path]], detail: bool = False
):
    total = sum(len(paths) for paths in duplicates.values())
    console.print(panel_dim(f"Found {total} duplicate files in '{path}'", "red"))
    if detail:
        for h, paths in duplicates.items():
            text = "\n".join(f"- {p}" for p in paths)

            try:
                size_mb = paths[0].stat().st_size / 1024 / 1024
            except OSError:
                size_mb = 0

            console.print(
                panel_dim(
                    text,
                    title=f"[bold]Hash:[/bold] {h} | [bold]Size:[/bold] {size_mb:.2f} MB",
                )
            )


def show_success(path: Path):
    console.print(fmt_success(f"No duplicates found in '{path}'", "green"))


def show_deleted(deleted: list[Path]):
    text = "\n".join(f"- {p}" for p in deleted)
    console.print(
        Panel(
            text,
            title=f"Deleted {len(deleted)} duplicate files",
            title_align="center",
            border_style="green",
        )
    )
