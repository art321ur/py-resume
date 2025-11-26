"""CLI for resume generator."""
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import cyclopts
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from resume_generator.agent import (
    AgentAction,
    AgentService,
    assess_pdf_file,
    proofread_resume_file,
    translate_resume_file,
)
from resume_generator.generator import ResumeGenerator
from resume_generator.loader import load_resume_model
from resume_generator.pdf import render_pdf_from_html_file

load_dotenv()

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


class AgentOptions(CLIBaseModel):
    action: AgentAction
    files: List[Path]
    target_language: Optional[str] = None
    source_language: Optional[str] = None
    output_dir: Path = Path("output/agent")
    model_name: Optional[str] = None


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


@app.command()
def agent(options: AgentOptions) -> None:
    """Run AI-powered helper actions on explicit files."""

    if not options.files:
        raise ValueError("Provide at least one file via --options.files.")

    service = AgentService(model_name=options.model_name)
    output_dir = Path(options.output_dir)
    resolved_files = [_ensure_exists(path, "Input file") for path in options.files]

    if options.action is AgentAction.TRANSLATE:
        if not options.target_language:
            raise ValueError("--options.target-language is required for translation.")
        for resume_path in resolved_files:
            destination = translate_resume_file(
                service,
                resume_path,
                target_language=options.target_language,
                source_language=options.source_language,
                output_dir=output_dir,
            )
            print(f"✓ Translated {resume_path.name} → {destination}")
    elif options.action is AgentAction.PROOFREAD:
        for resume_path in resolved_files:
            feedback, yaml_path = proofread_resume_file(
                service,
                resume_path,
                output_dir=output_dir,
            )
            print(f"Feedback for {resume_path.name}:\n{feedback}\nSaved to: {yaml_path}")
    elif options.action is AgentAction.PDF_ACCESSIBILITY:
        for pdf_path in resolved_files:
            report = assess_pdf_file(service, pdf_path)
            score = report.get("score")
            verdict = report.get("verdict", "")
            print(f"{pdf_path.name}: score={score} verdict={verdict}")
            issues = report.get("issues") or []
            if issues:
                print("Issues:")
                for issue in issues:
                    print(f"  - {issue}")
            suggestions = report.get("suggestions") or []
            if suggestions:
                print("Suggestions:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
            if "raw" in report:
                print("Raw response:")
                print(report["raw"])
    else:
        raise ValueError(f"Unsupported agent action: {options.action}")


@app.default
def default(options: GenerateOptions) -> None:  # type: ignore[override]
    """Run the ``generate`` command when none specified."""

    generate(options)


if __name__ == "__main__":
    app()
