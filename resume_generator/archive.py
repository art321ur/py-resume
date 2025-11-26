"""Shared helpers for resolving archive directories."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_DEFAULT_ARCHIVE_NAME = "resume-archive"
_ENV_KEYS = ("RESUME_ARCHIVE_DIR", "RESUME_DATA_DIR", "DATA_DIR")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_archive_dir(explicit: Optional[Path] = None) -> Path:
    """Return the directory that stores private resume data."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    for key in _ENV_KEYS:
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()
    fallback = _project_root().parent / _DEFAULT_ARCHIVE_NAME
    return fallback.resolve()


def resolve_input_dir(archive_dir: Optional[Path] = None) -> Path:
    return resolve_archive_dir(archive_dir) / "input"


def resolve_output_dir(archive_dir: Optional[Path] = None) -> Path:
    return resolve_archive_dir(archive_dir) / "output"
