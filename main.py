"""CLI for resume generator."""
from pathlib import Path
from typing import Optional

import cyclopts

from resume_generator.generator import ResumeGenerator
from resume_generator.loader import load_resume_model

app = cyclopts.App(
    name="resume-generator",
    help="Generate HTML resume from JSON or YAML resume data"
)



@app.default
def generate(
    input_file: Path,
    output_file: Path = Path("resume.html"),
    template_dir: Optional[Path] = None,
    profile_photo: Optional[Path] = None,
) -> None:
    """Generate HTML resume from JSON/YAML file.

    Args:
        input_file: Path to resume file (JSON or YAML)
        output_file: Path to output HTML file (default: resume.html)
        template_dir: Path to templates directory (optional)
        profile_photo: Optional override path for profile photo
    """

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Resume file not found: {input_file}")

    resume = load_resume_model(input_path)

    generator = ResumeGenerator(
        template_dir=template_dir,
        profile_photo=profile_photo,
    )
    generator.generate_html_file(resume, Path(output_file))

    print(f"✓ Resume generated successfully: {output_file}")


if __name__ == "__main__":
    app()
