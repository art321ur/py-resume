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
    input_file: str,
    output_file: str = "resume.html",
    template_dir: Optional[str] = None
) -> None:
    """Generate HTML resume from JSON/YAML file.
    
    Args:
        input_file: Path to resume file (JSON or YAML)
        output_file: Path to output HTML file (default: resume.html)
        template_dir: Path to templates directory (optional)
    """
    # Load resume data from JSON
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Resume file not found: {input_file}")
    
    resume = load_resume_model(input_path)
    
    # Generate HTML
    generator = ResumeGenerator(template_dir=template_dir)
    generator.generate_html_file(resume, output_file)
    
    print(f"✓ Resume generated successfully: {output_file}")


if __name__ == "__main__":
    app()
