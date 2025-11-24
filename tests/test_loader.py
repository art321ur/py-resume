"""Tests for loading resume data from JSON and YAML files."""
from __future__ import annotations

from pathlib import Path

import pytest

from resume_generator.loader import load_resume_data, load_resume_model
from resume_generator.models import Resume

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILES = [
    PROJECT_ROOT / "input" / "resume.json",
    PROJECT_ROOT / "input" / "resume.yaml",
]


@pytest.mark.parametrize("sample_path", SAMPLE_FILES)
def test_load_resume_data_handles_json_and_yaml(sample_path: Path) -> None:
    data = load_resume_data(sample_path)

    assert data["basics"]["name"] == "Artur Kuźmiński"
    assert len(data["work"]) == 2


@pytest.mark.parametrize("sample_path", SAMPLE_FILES)
def test_load_resume_model_returns_resume_instance(sample_path: Path) -> None:
    resume = load_resume_model(sample_path)

    assert isinstance(resume, Resume)
    assert resume.basics.name == "Artur Kuźmiński"