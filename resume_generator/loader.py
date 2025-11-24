"""Input helpers for loading resume data."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .models import Resume

_JSON_SUFFIXES = {".json"}
_YAML_SUFFIXES = {".yaml", ".yml"}


def _load_json(text: str) -> Any:
    return json.loads(text)


def _load_yaml(text: str) -> Any:
    return yaml.safe_load(text)


def load_resume_data(path: Path) -> Any:
    """Load resume data from JSON or YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")

    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in _JSON_SUFFIXES:
        return _load_json(text)
    if suffix in _YAML_SUFFIXES:
        return _load_yaml(text)

    # Fallback: try JSON then YAML regardless of extension.
    try:
        return _load_json(text)
    except json.JSONDecodeError:
        pass

    try:
        return _load_yaml(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Could not parse resume data from {path} as JSON or YAML") from exc


def load_resume_model(path: Path) -> Resume:
    """Load and validate resume data returning a `Resume` model."""
    data = load_resume_data(path)
    return Resume(**data)
