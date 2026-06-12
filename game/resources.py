"""Shared helpers for loading packaged resources."""

from pathlib import Path
import sys


def resource_path(*relative_parts: str) -> Path:
    """Return a path that works in both source and PyInstaller environments."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base.joinpath(*relative_parts)
