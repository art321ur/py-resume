"""HTML generation from resume data."""
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja_markdown import MarkdownExtension

from .assets import get_image_as_data_uri, get_placeholder_avatar_data_uri, get_svg_icons
from .models import Resume


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """Best-effort parser for ISO-like date strings."""
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def calculate_years(start_value: Optional[str], end_value: Optional[str]) -> Optional[str]:
    """Replicate React's rounded duration helper."""
    start_date = _parse_date(start_value)
    if not start_date:
        return None
    end_date = _parse_date(end_value) or datetime.now()
    diff_days = (end_date - start_date).days
    years = diff_days / 365
    rounded = round(years * 2) / 2
    return f"{rounded:.1f}"


class ResumeGenerator:
    """Generate HTML resumes from JSON or YAML data."""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        profile_photo: Optional[Path] = None,
    ) -> None:
        """Initialize the generator.

        Args:
            template_dir: Path to templates directory. Defaults to package templates.
            profile_photo: Optional override path for the profile image.
        """

        self.template_dir = (
            Path(__file__).parent / "templates"
            if template_dir is None
            else Path(template_dir)
        )
        self.profile_photo = Path(profile_photo) if profile_photo else None

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            extensions=[MarkdownExtension]
        )
        self.env.globals["calc_years"] = calculate_years

    def generate_html(self, resume: Resume) -> str:
        """Generate HTML from resume data.
        
        Args:
            resume: Resume data model
            
        Returns:
            Complete HTML string with inlined CSS and fonts
        """
        # Read CSS file and inline it
        static_dir = Path(__file__).parent / "static"
        styles_path = static_dir / "styles.css"
        paper_css_path = static_dir / "paper.css"

        with open(paper_css_path, 'r', encoding='utf-8') as paper_file:
            paper_css = paper_file.read()

        with open(styles_path, 'r', encoding='utf-8') as styles_file:
            styles_css = styles_file.read()

        css_content = f"{paper_css}\n\n{styles_css}"

        # Get SVG icons
        icons = get_svg_icons()
        
        # Process picture - try matching React's public/profile.jpg
        package_dir = Path(__file__).resolve().parent
        repo_root = package_dir.parent.parent
        candidate_paths = []
        if self.profile_photo:
            candidate_paths.append(self.profile_photo)
        candidate_paths.extend([
            repo_root / "public" / "profile.jpg",
            Path.cwd() / "public" / "profile.jpg",
        ])

        picture_url = None
        for candidate in candidate_paths:
            data_uri = get_image_as_data_uri(candidate)
            if data_uri:
                picture_url = data_uri
                break

        if not picture_url and resume.basics.picture:
            picture_url = get_image_as_data_uri(resume.basics.picture) or resume.basics.picture

        if not picture_url:
            picture_url = get_placeholder_avatar_data_uri()

        # Load template
        template = self.env.get_template("resume.html")

        # Render template
        html = template.render(
            resume=resume,
            css_content=css_content,
            icons=icons,
            picture_url=picture_url
        )

        return html

    def generate_html_file(self, resume: Resume, output_path: Path) -> None:
        """Generate HTML file from resume data.
        
        Args:
            resume: Resume data model
            output_path: Path where to write the HTML file
        """
        html = self.generate_html(resume)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
