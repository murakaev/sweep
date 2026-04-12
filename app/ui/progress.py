from contextlib import contextmanager
from typing import Generator
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TaskID,
)
from app.ui.base import fmt_active, fmt_success, fmt_error


class ProgressTracker:
    def __init__(self, progress: Progress):
        self._progress = progress

    def add_task(self, description: str, total: int | None = None) -> TaskID:
        return self._progress.add_task(fmt_active(description, ""), total=total)

    def advance(self, task_id: TaskID, label: str, detail: str = "") -> None:
        self._progress.update(task_id, advance=1, description=fmt_active(label, detail))

    def complete(self, task_id: TaskID, message: str) -> None:
        self._progress.update(
            task_id, description=fmt_success(message), total=1, completed=1
        )

    def fail(self, task_id: TaskID, message: str) -> None:
        self._progress.update(
            task_id, description=fmt_error(message), total=1, completed=1
        )


@contextmanager
def progress_tracker(transient: bool = False) -> Generator[ProgressTracker, None, None]:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        transient=transient,
    ) as progress:
        yield ProgressTracker(progress)
