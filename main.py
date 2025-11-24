"""CLI for resume generator."""
from datetime import datetime
from pathlib import Path
from typing import Optional

import cyclopts
from pydantic import BaseModel, ConfigDict

from resume_generator.generator import ResumeGenerator
from resume_generator.loader import load_resume_model
from resume_generator.pdf import render_pdf_from_html_file

app = cyclopts.App(
    name="resume-generator",
    help="Generate resumes as HTML and PDF",
)


def _timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _with_timestamp(path: Path, timestamp: Optional[str]) -> Path:
    resolved = Path(path)
    if not timestamp:
        return resolved
    return resolved.with_name(f"{resolved.stem}_{timestamp}{resolved.suffix}")


def _prepare_output_path(
    path: Path,
    *,
    timestamp: Optional[str],
    force: bool,
) -> Path:
    target = _with_timestamp(Path(path), timestamp)
    if target.exists() and not force:
        raise FileExistsError(
            f"Output already exists: {target}. Use --force to overwrite."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _ensure_exists(path: Path, description: str) -> Path:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"{description} not found: {resolved}")
    return resolved


class CLIBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerateOptions(CLIBaseModel):
    input_file: Path
    output_file: Path = Path("resume.html")
    template_dir: Optional[Path] = None
    profile_photo: Optional[Path] = None
    force: bool = False
    file_date: bool = False


class PdfOptions(CLIBaseModel):
    html_file: Path
    output_file: Optional[Path] = None
    force: bool = False
    file_date: bool = False


class FullOptions(CLIBaseModel):
    input_file: Path
    output_file: Path = Path("resume.html")
    template_dir: Optional[Path] = None
    profile_photo: Optional[Path] = None
    pdf_file: Optional[Path] = None
    force: bool = False
    file_date: bool = False


class FullManyOptions(CLIBaseModel):
    input_dir: Path
    output_dir: Path
    template_dir: Optional[Path] = None
    profile_photo: Optional[Path] = None
    force: bool = False
    file_date: bool = False


def _generate_html(
    input_file: Path,
    output_file: Path,
    template_dir: Optional[Path],
    profile_photo: Optional[Path],
    *,
    force: bool = False,
    timestamp: Optional[str] = None,
) -> Path:
    input_path = _ensure_exists(input_file, "Resume file")

    resume = load_resume_model(input_path)

    generator = ResumeGenerator(
        template_dir=template_dir,
        profile_photo=profile_photo,
    )
    output_path = _prepare_output_path(output_file, timestamp=timestamp, force=force)
    generator.generate_html_file(resume, output_path)
    return output_path


@app.command()
def generate(options: GenerateOptions) -> None:
    """Generate an HTML resume."""

    timestamp = _timestamp_suffix() if options.file_date else None
    output_path = _generate_html(
        options.input_file,
        options.output_file,
        options.template_dir,
        options.profile_photo,
        force=options.force,
        timestamp=timestamp,
    )
    print(f"✓ Resume generated successfully: {output_path}")


@app.command()
def pdf(options: PdfOptions) -> None:
    """Convert an existing HTML resume to PDF."""

    html_path = _ensure_exists(options.html_file, "HTML file")
    timestamp = _timestamp_suffix() if options.file_date else None
    pdf_candidate = options.output_file or html_path.with_suffix(".pdf")
    target_pdf = _prepare_output_path(
        pdf_candidate,
        timestamp=timestamp,
        force=options.force,
    )

    render_pdf_from_html_file(html_path, target_pdf)
    print(f"✓ PDF created successfully: {target_pdf}")


@app.command()
def full(options: FullOptions) -> None:
    """Generate both HTML and PDF outputs with matching names by default."""

    timestamp = _timestamp_suffix() if options.file_date else None
    html_path = _generate_html(
        options.input_file,
        options.output_file,
        options.template_dir,
        options.profile_photo,
        force=options.force,
        timestamp=timestamp,
    )
    pdf_candidate = options.pdf_file or html_path.with_suffix(".pdf")
    pdf_timestamp = timestamp if options.pdf_file else None
    target_pdf = _prepare_output_path(
        pdf_candidate,
        timestamp=pdf_timestamp,
        force=options.force,
    )

    render_pdf_from_html_file(html_path, target_pdf)
    print(f"✓ Resume generated: {html_path}")
    print(f"✓ PDF generated: {target_pdf}")


@app.command(name="full-many")
def full_many(options: FullManyOptions) -> None:
    """Process every JSON/YAML resume in a directory to HTML and PDF outputs."""

    input_dir = _ensure_exists(options.input_dir, "Input directory")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory is not a directory: {input_dir}")

    output_dir = Path(options.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    for pattern in ("*.json", "*.yaml", "*.yml"):
        candidates.extend(sorted(input_dir.glob(pattern)))

    resume_files: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved_candidate = candidate.resolve()
        if resolved_candidate in seen:
            continue
        seen.add(resolved_candidate)
        resume_files.append(candidate)

    if not resume_files:
        raise FileNotFoundError(
            f"No JSON or YAML resumes found in directory: {input_dir}"
        )

    generator = ResumeGenerator(
        template_dir=options.template_dir,
        profile_photo=options.profile_photo,
    )

    processed: list[tuple[Path, Path]] = []
    for resume_path in resume_files:
        resume = load_resume_model(resume_path)
        file_timestamp = _timestamp_suffix() if options.file_date else None
        html_candidate = output_dir / f"{resume_path.stem}.html"
        html_path = _prepare_output_path(
            html_candidate,
            timestamp=file_timestamp,
            force=options.force,
        )
        generator.generate_html_file(resume, html_path)

        pdf_candidate = html_path.with_suffix(".pdf")
        pdf_path = _prepare_output_path(
            pdf_candidate,
            timestamp=None,
            force=options.force,
        )
        render_pdf_from_html_file(html_path, pdf_path)
        processed.append((html_path, pdf_path))

    print(f"✓ Processed {len(processed)} resume(s) into {output_dir}:")
    for html_path, pdf_path in processed:
        print(f"  - {html_path.name} | {pdf_path.name}")


@app.default
def default(options: GenerateOptions) -> None:  # type: ignore[override]
    """Run the ``generate`` command when none specified."""

    generate(options)


if __name__ == "__main__":
    app()
