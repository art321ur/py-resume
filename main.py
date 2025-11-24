"""CLI for resume generator."""
from pathlib import Path
from typing import Optional

import cyclopts

from resume_generator.generator import ResumeGenerator
from resume_generator.loader import load_resume_model
from resume_generator.pdf import render_pdf_from_html_file

app = cyclopts.App(
    name="resume-generator",
    help="Generate resumes as HTML and PDF",
)


def _generate_html(
    input_file: Path,
    output_file: Path,
    template_dir: Optional[Path],
    profile_photo: Optional[Path],
) -> Path:
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Resume file not found: {input_file}")

    resume = load_resume_model(input_path)

    generator = ResumeGenerator(
        template_dir=template_dir,
        profile_photo=profile_photo,
    )
    output_path = Path(output_file)
    generator.generate_html_file(resume, output_path)
    return output_path


@app.command()
def generate(
    input_file: Path,
    output_file: Path = Path("resume.html"),
    template_dir: Optional[Path] = None,
    profile_photo: Optional[Path] = None,
) -> None:
    """Generate an HTML resume."""

    output_path = _generate_html(input_file, output_file, template_dir, profile_photo)
    print(f"✓ Resume generated successfully: {output_path}")


@app.command()
def pdf(
    html_file: Path,
    output_file: Optional[Path] = None,
) -> None:
    """Convert an existing HTML resume to PDF."""

    html_path = Path(html_file)
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")

    target_pdf = render_pdf_from_html_file(html_path, output_file)
    print(f"✓ PDF created successfully: {target_pdf}")


@app.command()
def full(
    input_file: Path,
    output_file: Path = Path("resume.html"),
    template_dir: Optional[Path] = None,
    profile_photo: Optional[Path] = None,
    pdf_file: Optional[Path] = None,
) -> None:
    """Generate both HTML and PDF outputs with matching names by default."""

    html_path = _generate_html(input_file, output_file, template_dir, profile_photo)
    target_pdf = render_pdf_from_html_file(html_path, pdf_file)
    print(f"✓ Resume generated: {html_path}")
    print(f"✓ PDF generated: {target_pdf}")


@app.default
def default(*args, **kwargs) -> None:  # type: ignore[override]
    """Run the ``generate`` command when none specified."""

    generate(*args, **kwargs)


if __name__ == "__main__":
    app()
