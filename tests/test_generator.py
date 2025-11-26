"""Tests for HTML generator helpers."""
from __future__ import annotations

from resume_generator.generator import DEFAULT_CV_FOOTER, ResumeGenerator
from resume_generator.models import Basics, Resume


def test_generate_html_uses_default_footer_text() -> None:
    resume = Resume(basics=Basics(name="Sample Person"))

    html = ResumeGenerator().generate_html(resume)

    assert DEFAULT_CV_FOOTER.splitlines()[0] in html


def test_generate_html_renders_custom_footer_text() -> None:
    custom_footer = "Custom footer from test suite."
    resume = Resume(basics=Basics(name="Sample Person"), cvFooter=custom_footer)

    html = ResumeGenerator().generate_html(resume)

    assert custom_footer in html
