# Resume Generator
Personal project to automatically generate html/pdf resumes from json/yaml data files.
Generate a beautiful, single-file HTML resume from a JSON resume file using Jinja2 templates.

> **Data storage tip:** keep your personal resume sources outside of this repository (for example in a private folder living next to `py-resume`). The commands below assume an environment variable named `DATA_DIR` (or PowerShell `$env:DATA_DIR`) that points to that private directory containing `input/` and `output/` subfolders.



## Installation

```bash
uv install
```

## Usage

Clone `py-resume` alongside wherever you keep your private resume data, and export `DATA_DIR` (or `$env:DATA_DIR`) to reference that location while running commands.

### CLI

Generate HTML resume from JSON or YAML file:

```bash
uv run main.py generate "$DATA_DIR/input/resume.yaml" \
  --output "$DATA_DIR/output/resume.html" \
  --profile-photo "$DATA_DIR/input/profile.jpg" \
  --force
```

Or use the default output name:

```bash
uv run main.py generate "$DATA_DIR/input/resume.json"
```

> Commands now refuse to overwrite existing files unless you pass `--force`. Add `--file-date` to append a timestamp.

Convert an already-rendered HTML file to PDF (defaults to the same name with `.pdf`):

```bash
uv run main.py pdf "$DATA_DIR/output/resume.html" \
  --output "$DATA_DIR/output/resume.pdf" \
  --force
```

Generate both HTML and PDF with matching names in one go:

```bash
uv run main.py full "$DATA_DIR/input/resume.yaml" \
  --output "$DATA_DIR/output/resume.html" \
  --force
```

Process every JSON/YAML resume in a directory (outputs stored in another directory):

```bash
uv run main.py full-many "$DATA_DIR/input" "$DATA_DIR/output" --file-date --force
```

> Keep your resume sources and outputs outside of version control to avoid leaking personal information.

### Python API

```python
from pathlib import Path
from resume_generator import Resume, ResumeGenerator, load_resume_data

data_dir = Path("../private-resume-data")  # update this path to wherever you store inputs
data = load_resume_data(data_dir / "input" / "resume.yaml")
resume = Resume(**data)

generator = ResumeGenerator(profile_photo=data_dir / "input" / "profile.jpg")
html = generator.generate_html(resume)

generator.generate_html_file(resume, data_dir / "output" / "resume.html")
```

## Resume JSON Format

The resume follows the [JSON Resume](https://jsonresume.org/) schema, adjusted as needed to my needs. Example structure:

```json
{
  "basics": {
    "name": "Your Name",
    "label": "Your Title",
    "email": "your.email@example.com",
    "phone": "+1 234 567 8900",
    "summary": "Your professional summary",
    "location": {
      "address": "123 Main St",
      "city": "City",
      "postalCode": "12345",
      "countryCode": "US",
      "region": "State"
    },
    "profiles": [
      {
        "network": "LinkedIn",
        "username": "yourname",
        "url": "https://linkedin.com/in/yourname"
      }
    ]
  },
  "work": [
    {
      "name": "Company Name",
      "position": "Job Title",
      "startDate": "2020-01",
      "endDate": "2023-12",
      "summary": "Job description",
      "highlights": ["Achievement 1", "Achievement 2"],
      "additional": [
        {
          "title": "Technologies",
          "tech": ["Python", "React"]
        }
      ]
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "studyType": "Bachelor",
      "area": "Computer Science",
      "startDate": "2016",
      "endDate": "2020"
    }
  ],
  "skills": [
    {
      "category": "Programming",
      "name": "Python",
      "rating": 5
    }
  ],
  "languages": [
    {
      "language": "English",
      "rating": 5
    }
  ],
  "portfolio": [
    {
      "name": "Python Resume Generator",
      "description": "Render **Markdown** blurbs with links.",
      "url": "https://github.com/art321ur/py-resume"
    }
  ],
  "interests": [
    {
      "name": "Software Development"
    }
  ],
  "cvFooter": "Optional consent statement shown at the bottom of the resume."
}
```

Add an optional `cvFooter` string if you want to override the default GDPR consent text rendered at the bottom of the generated resume. When omitted, the classic consent block remains unchanged.

## Development

### Tooling

- Lint: `uv run ruff check .`
- Type check: `uv run ty check`
- Tests: `uv run pytest`
- Install hooks: `uv run pre-commit install`
- Install Playwright browsers (once): `uv run playwright install`

### Local helpers

- Run HTML generation or checks via `local_tasks.ps1`:
  - `pwsh ./local_tasks.ps1 -Task html`
  - `pwsh ./local_tasks.ps1 -Task checks`

### Project Structure

```
resume_generator/
├── __init__.py
├── models.py           # Pydantic models
├── generator.py        # HTML generation
├── assets.py          # Font and icon assets
├── static/
│   └── styles.css     # Inlined CSS styles
└── templates/
    ├── resume.html    # Main template
    └── components/    # Component templates
        ├── about.html
        ├── skills.html
        ├── languages.html
        ├── experience.html
        ├── education.html
        ├── hobbies.html
        └── summary.html
```

## License

GPL 3
