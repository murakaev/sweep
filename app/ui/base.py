from rich.panel import Panel

STYLE_ACTIVE = "cyan"
STYLE_SUCCESS = "green"
STYLE_ERROR = "red"
STYLE_DIM = "dim"

ICON_SUCCESS = "✓"
ICON_ERROR = "✗"
ICON_ACTIVE = "›"
ICON_WARNING = "⚠"


def fmt_success(text: str) -> str:
    return f"[{STYLE_SUCCESS}]{ICON_SUCCESS} {text}[/{STYLE_SUCCESS}]"


def fmt_error(text: str) -> str:
    return f"[{STYLE_ERROR}]{ICON_ERROR} {text}[/{STYLE_ERROR}]"


def fmt_dim(text: str) -> str:
    return f"[{STYLE_DIM}]{text}[/{STYLE_DIM}]"


def fmt_active(label: str, detail: str) -> str:
    return f"[{STYLE_ACTIVE}]{ICON_ACTIVE} {label}: [/{STYLE_ACTIVE}][{STYLE_DIM}]{detail}[/{STYLE_DIM}]"


def panel_success(text: str, title: str = "Success") -> str:
    return Panel(text, title=title, title_align="left", border_style=STYLE_SUCCESS)


def panel_error(text: str, title: str = "Error") -> str:
    return Panel(text, title=title, title_align="left", border_style=STYLE_ERROR)


def panel_dim(text: str, title: str = "Info") -> str:
    return Panel(text, title=title, title_align="left", border_style=STYLE_DIM)
