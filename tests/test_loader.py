"""Tests for loading resume data from JSON and YAML files."""
from __future__ import annotations

from pathlib import Path

import pytest

from resume_generator.loader import load_resume_data, load_resume_model
from resume_generator.models import Resume

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILES = [
    PROJECT_ROOT / "tests" / "data" / "resume.json",
    PROJECT_ROOT / "tests" / "data" / "resume.yaml",
]


@pytest.mark.parametrize("sample_path", SAMPLE_FILES)
def test_load_resume_data_handles_json_and_yaml(sample_path: Path) -> None:
    data = load_resume_data(sample_path)

    assert data["basics"]["name"] == "Sample Person"
    assert len(data["work"]) == 1
    assert data["portfolio"][0]["name"] == "Sample Project"
    expected_footer = (
        "Custom consent text from YAML."
        if sample_path.suffix == ".yaml"
        else "Custom consent text from JSON."
    )
    assert data["cvFooter"] == expected_footer


@pytest.mark.parametrize("sample_path", SAMPLE_FILES)
def test_load_resume_model_returns_resume_instance(sample_path: Path) -> None:
    resume = load_resume_model(sample_path)

    assert isinstance(resume, Resume)
    assert resume.basics.name == "Sample Person"
    assert resume.portfolio and resume.portfolio[0].name == "Sample Project"
    expected_footer = (
        "Custom consent text from YAML."
        if sample_path.suffix == ".yaml"
        else "Custom consent text from JSON."
    )
    assert resume.cvFooter == expected_footer