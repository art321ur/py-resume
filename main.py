"""CLI for resume generator."""
import json
from pathlib import Path
from typing import Optional

import cyclopts

from resume_generator.generator import ResumeGenerator
from resume_generator.models import Resume

app = cyclopts.App(
    name="resume-generator",
    help="Generate HTML resume from JSON resume data"
)


@app.default
def generate(
    input_file: str,
    output_file: str = "resume.html",
    template_dir: Optional[str] = None
) -> None:
    """Generate HTML resume from JSON file.
    
    Args:
        input_file: Path to JSON resume file
        output_file: Path to output HTML file (default: resume.html)
        template_dir: Path to templates directory (optional)
    """
    # Load resume data from JSON
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Resume file not found: {input_file}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Parse with Pydantic
    resume = Resume(**data)
    
    # Generate HTML
    generator = ResumeGenerator(template_dir=template_dir)
    generator.generate_html_file(resume, output_file)
    
    print(f"✓ Resume generated successfully: {output_file}")


if __name__ == "__main__":
    app()
