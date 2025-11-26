"""Tests for CLI helpers and commands."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import main


def test_prepare_output_path_requires_force(tmp_path: Path) -> None:
    target = tmp_path / "resume.html"
    target.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        main._prepare_output_path(target, timestamp=None, force=False)

    resolved = main._prepare_output_path(target, timestamp=None, force=True)
    assert resolved == target


def test_pdf_command_adds_timestamp_when_requested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    html_file = tmp_path / "resume.html"
    html_file.write_text("<html></html>", encoding="utf-8")

    outputs: list[Path] = []

    def fake_render(html_path: Path, output_path: Path | None) -> Path:
        assert output_path is not None
        target = Path(output_path)
        target.write_text("pdf", encoding="utf-8")
        outputs.append(target)
        return target

    monkeypatch.setattr(main, "render_pdf_from_html_file", fake_render)
    monkeypatch.setattr(main, "_timestamp_suffix", lambda: "20250101_010101")

    options = main.PdfOptions(
        html_file=html_file,
        output_file=None,
        force=False,
        file_date=True,
    )

    main.pdf(options)

    assert outputs[0].name == "resume_20250101_010101.pdf"
    assert outputs[0].exists()


def test_pdf_command_requires_force_when_output_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    html_file = tmp_path / "resume.html"
    html_file.write_text("<html></html>", encoding="utf-8")
    existing_pdf = tmp_path / "resume.pdf"
    existing_pdf.write_text("old", encoding="utf-8")

    monkeypatch.setattr(main, "render_pdf_from_html_file", lambda *args, **kwargs: None)

    options = main.PdfOptions(
        html_file=html_file,
        output_file=None,
        force=False,
        file_date=False,
    )

    with pytest.raises(FileExistsError):
        main.pdf(options)


def test_full_many_processes_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    data_dir = Path("tests/data")
    shutil.copy(data_dir / "resume.json", input_dir / "sample.json")
    shutil.copy(data_dir / "resume.yaml", input_dir / "sample.yaml")

    def fake_generate_html(self, resume, output_path):
        Path(output_path).write_text("<html></html>", encoding="utf-8")

    monkeypatch.setattr(main.ResumeGenerator, "generate_html_file", fake_generate_html)

    def fake_render(html_path: Path, output_path: Path | None) -> Path:
        assert output_path is not None
        Path(output_path).write_text("pdf", encoding="utf-8")
        return Path(output_path)

    monkeypatch.setattr(main, "render_pdf_from_html_file", fake_render)

    timestamps = iter(["202501010303", "202501010404"])
    monkeypatch.setattr(main, "_dated_folder_name", lambda: next(timestamps))

    options = main.FullManyOptions(
        input_dir=input_dir,
        output_dir=output_dir,
        template_dir=None,
        profile_photo=None,
        force=False,
        file_date=False,
    )

    main.full_many(options)

    html_outputs = sorted(
        p.relative_to(output_dir).as_posix() for p in output_dir.glob("**/*.html")
    )
    pdf_outputs = sorted(
        p.relative_to(output_dir).as_posix() for p in output_dir.glob("**/*.pdf")
    )

    assert html_outputs == [
        "sample/202501010303/Sample_Person_CV.html",
        "sample/202501010404/Sample_Person_CV.html",
    ]
    assert pdf_outputs == [
        "sample/202501010303/Sample_Person_CV.pdf",
        "sample/202501010404/Sample_Person_CV.pdf",
    ]