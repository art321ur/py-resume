"""Tests for the PDF conversion helpers."""
from __future__ import annotations

import asyncio
import html
from pathlib import Path
from typing import Any, Dict

from resume_generator import pdf as pdf_module


class FakePage:
    def __init__(self, recorder: Dict[str, Any]) -> None:
        self.recorder = recorder

    async def goto(self, url: str, wait_until: str) -> None:  # pragma: no cover - simple recorder
        self.recorder["goto"] = (url, wait_until)

    async def set_content(self, content: str, wait_until: str) -> None:
        self.recorder["set_content"] = (content, wait_until)

    async def wait_for_load_state(self, state: str) -> None:
        self.recorder["load_state"] = state

    async def evaluate(self, script: str) -> None:
        self.recorder["evaluate_script"] = script

    async def pdf(self, path: str, format: str, print_background: bool) -> None:
        self.recorder["pdf_call"] = {
            "path": Path(path),
            "format": format,
            "print_background": print_background,
        }
        Path(path).write_text("stub-pdf", encoding="utf-8")


class FakeContext:
    def __init__(self, recorder: Dict[str, Any]) -> None:
        self.recorder = recorder

    async def new_page(self) -> FakePage:
        return FakePage(self.recorder)

    async def close(self) -> None:
        self.recorder["context_closed"] = True


class FakeBrowser:
    def __init__(self, recorder: Dict[str, Any]) -> None:
        self.recorder = recorder

    async def new_context(self, bypass_csp: bool) -> FakeContext:
        self.recorder["bypass_csp"] = bypass_csp
        return FakeContext(self.recorder)

    async def close(self) -> None:
        self.recorder["browser_closed"] = True


class FakeChromium:
    def __init__(self, recorder: Dict[str, Any]) -> None:
        self.recorder = recorder

    async def launch(self, args):
        self.recorder["launch_args"] = args
        return FakeBrowser(self.recorder)


class FakePlaywright:
    def __init__(self, recorder: Dict[str, Any]) -> None:
        self.recorder = recorder
        self.chromium = FakeChromium(recorder)

    async def __aenter__(self) -> "FakePlaywright":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.recorder["playwright_closed"] = True


def test_html_to_pdf_uses_base_url_when_provided(monkeypatch, tmp_path):
    recorder: Dict[str, Any] = {}

    def fake_async_playwright():
        return FakePlaywright(recorder)

    monkeypatch.setattr(pdf_module, "async_playwright", fake_async_playwright)

    output_pdf = tmp_path / "resume.pdf"
    asyncio.run(pdf_module.html_to_pdf("<p>hello</p>", output_pdf, base_url="file:///resume.html"))

    assert recorder["goto"] == ("file:///resume.html", "networkidle")
    assert "set_content" not in recorder
    assert output_pdf.exists()


def test_html_to_pdf_sets_content_without_base_url(monkeypatch, tmp_path):
    recorder: Dict[str, Any] = {}

    def fake_async_playwright():
        return FakePlaywright(recorder)

    monkeypatch.setattr(pdf_module, "async_playwright", fake_async_playwright)

    output_pdf = tmp_path / "resume.pdf"
    asyncio.run(pdf_module.html_to_pdf("<p>hello</p>", output_pdf))

    assert recorder["set_content"][0] == "<p>hello</p>"
    assert output_pdf.exists()


def test_render_pdf_from_html_file_runs_async_conversion(monkeypatch, tmp_path):
    html_path = tmp_path / "resume.html"
    html_text = "<h1>Hi &amp; Bye</h1>"
    html_path.write_text(html_text, encoding="utf-8")

    recorded: Dict[str, Any] = {}

    async def fake_html_to_pdf(html_content, output_path, base_url=None):
        recorded["html_content"] = html_content
        recorded["output_path"] = Path(output_path)
        recorded["base_url"] = base_url
        Path(output_path).write_text("stub-pdf", encoding="utf-8")

    monkeypatch.setattr(pdf_module, "html_to_pdf", fake_html_to_pdf)

    pdf_path = pdf_module.render_pdf_from_html_file(html_path)

    assert pdf_path == html_path.with_suffix(".pdf")
    assert pdf_path.exists()
    assert recorded["html_content"] == html.unescape(html_text)
    assert recorded["base_url"] == html_path.resolve().as_uri()