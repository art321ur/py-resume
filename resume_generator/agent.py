"""AI-powered helper utilities for resume automation."""
from __future__ import annotations

import base64
import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Tuple

import yaml
from pydantic_ai import Agent


class AgentAction(str, Enum):
    """Supported AI workflows."""

    TRANSLATE = "translate"
    PROOFREAD = "proofread"
    PDF_ACCESSIBILITY = "pdf-access"


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    first_newline = stripped.find("\n")
    if first_newline == -1:
        return stripped
    body = stripped[first_newline + 1 :]
    if body.endswith("```"):
        body = body[: -3]
    return body.strip()


def _normalize_agent_output(result: Any) -> str:
    candidate = result
    if hasattr(candidate, "output"):
        candidate = getattr(candidate, "output")
    elif hasattr(candidate, "data"):
        candidate = getattr(candidate, "data")
    text = str(candidate)
    return _strip_code_fence(text)


class AgentService:
    """Thin wrapper around a Pydantic AI agent."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        api_key = os.getenv("AI_API_KEY")
        if not api_key:
            raise RuntimeError("AI_API_KEY environment variable is required for agent tasks.")

        selected_model = model_name or os.getenv("AI_MODEL", "openai:gpt-4o-mini")
        if ":" not in selected_model:
            selected_model = f"openai:{selected_model}"
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = api_key
        self._agent = Agent(
            model=selected_model,
            output_type=str,
            system_prompt=(
                "You help with resume authoring tasks. Keep responses concise and structured."
            ),
        )

    def _run(self, prompt: str) -> str:
        result = self._agent.run_sync(prompt)
        return _normalize_agent_output(result)

    def translate_resume(
        self,
        *,
        resume_text: str,
        resume_format: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> str:
        language_hint = source_language or "the original language"
        prompt = (
            "Translate the following resume from "
            f"{language_hint} into {target_language}.\n"
            f"Keep it valid {resume_format.upper()} and do not add commentary.\n"
            "Return only the translated resume content.\n\n"
            f"Resume ({resume_format}):\n{resume_text}"
        )
        return self._run(prompt)

    def proofread_resume(self, *, resume_text: str, resume_format: str) -> str:
        prompt = (
            "You are a resume editor. Review the following resume content and provide concise "
            "actionable hints to improve clarity, grammar, and impact. Group feedback by sections "
            "when possible. Return a short markdown list, do not rewrite the resume.\n\n"
            f"Resume ({resume_format}):\n{resume_text}"
        )
        return self._run(prompt)

    def assess_pdf_accessibility(self, *, pdf_b64: str, file_name: str) -> str:
        prompt = (
            "You are verifying whether a resume PDF is machine-readable for AI parsing tools.\n"
            f"Evaluate the provided base64 encoded PDF named {file_name}.\n"
            "Score accessibility from 0-100 and list concrete issues impacting automated "
            "processing. Respond with JSON containing keys: score (number), verdict (string), "
            "issues (list of strings), suggestions (list of strings).\n\n"
            f"PDF name: {file_name}\n"
            f"PDF (base64): {pdf_b64}"
        )
        return self._run(prompt)


def _detect_resume_format(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".json":
        return "json"
    raise ValueError(f"Unsupported resume format for AI tasks: {file_path}")


def _unique_path(initial: Path) -> Path:
    candidate = initial
    counter = 1
    while candidate.exists():
        candidate = initial.with_name(f"{initial.stem}_{counter}{initial.suffix}")
        counter += 1
    return candidate


def translate_resume_file(
    service: AgentService,
    file_path: Path,
    *,
    target_language: str,
    source_language: Optional[str],
    output_dir: Path,
) -> Path:
    resume_format = _detect_resume_format(file_path)
    resume_text = file_path.read_text(encoding="utf-8")
    translated = service.translate_resume(
        resume_text=resume_text,
        resume_format=resume_format,
        target_language=target_language,
        source_language=source_language,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    language_suffix = target_language.lower().replace(" ", "_")
    base = output_dir / f"{file_path.stem}_translated_{language_suffix}{file_path.suffix}"
    destination = _unique_path(base)
    destination.write_text(translated, encoding="utf-8")
    return destination


def proofread_resume_file(
    service: AgentService,
    file_path: Path,
    *,
    output_dir: Path,
) -> Tuple[str, Path]:
    resume_format = _detect_resume_format(file_path)
    resume_text = file_path.read_text(encoding="utf-8")
    feedback = service.proofread_resume(resume_text=resume_text, resume_format=resume_format)

    payload = {
        "source_file": str(file_path),
        "format": resume_format,
        "feedback": feedback,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    base = output_dir / f"{file_path.stem}_proofread.yaml"
    destination = _unique_path(base)
    destination.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return feedback, destination


def assess_pdf_file(service: AgentService, file_path: Path) -> dict:
    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"PDF access check expects a .pdf file: {file_path}")

    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    raw_response = service.assess_pdf_accessibility(pdf_b64=encoded, file_name=file_path.name)
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        parsed = {
            "score": None,
            "verdict": "",
            "issues": [],
            "suggestions": [],
            "raw": raw_response,
        }
    return parsed
