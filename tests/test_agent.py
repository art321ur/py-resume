"""Tests for AI helper utilities without calling real models."""
from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml

from resume_generator.agent import (
    AgentService,
    _normalize_agent_output,
    assess_pdf_file,
    proofread_resume_file,
    translate_resume_file,
)


class DummyService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def translate_resume(self, **kwargs):
        self.calls.append("translate")
        resume_text = kwargs["resume_text"]
        target = kwargs["target_language"]
        return f"translated-{target}\n{resume_text}"

    def proofread_resume(self, **kwargs):
        self.calls.append("proofread")
        return "- tighten summary\n- fix typos"

    def assess_pdf_accessibility(self, **kwargs):
        self.calls.append("pdf")
        return json.dumps(
            {
                "score": 82,
                "verdict": "Readable",
                "issues": ["Low contrast text"],
                "suggestions": ["Increase font size"],
            }
        )


def test_translate_resume_file_generates_unique_outputs(tmp_path: Path) -> None:
    src = tmp_path / "resume.yaml"
    src.write_text("name: Example", encoding="utf-8")
    out_dir = tmp_path / "out"
    service = cast(AgentService, DummyService())

    first = translate_resume_file(
        service,
        src,
        target_language="French",
        source_language=None,
        output_dir=out_dir,
    )
    second = translate_resume_file(
        service,
        src,
        target_language="French",
        source_language=None,
        output_dir=out_dir,
    )

    assert first.exists()
    assert second.exists()
    assert first != second
    assert "translated-french" in first.read_text(encoding="utf-8").lower()


def test_proofread_resume_file_writes_yaml(tmp_path: Path) -> None:
    src = tmp_path / "resume.json"
    src.write_text("{}", encoding="utf-8")
    out_dir = tmp_path / "out"
    service = cast(AgentService, DummyService())

    feedback, payload_path = proofread_resume_file(service, src, output_dir=out_dir)

    assert "tighten" in feedback
    assert payload_path.exists()
    data = yaml.safe_load(payload_path.read_text(encoding="utf-8"))
    assert data["source_file"].endswith("resume.json")
    assert "feedback" in data


def test_assess_pdf_file_parses_json(tmp_path: Path) -> None:
    pdf_path = tmp_path / "resume.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")
    service = cast(AgentService, DummyService())

    report = assess_pdf_file(service, pdf_path)

    assert report["score"] == 82
    assert report["issues"] == ["Low contrast text"]


def test_normalize_agent_output_handles_agent_result() -> None:
    class Result:
        def __init__(self, output: str) -> None:
            self.output = output

    text = _normalize_agent_output(Result("```yaml\nkey: value\n```"))
    assert text == "key: value"