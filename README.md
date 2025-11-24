# Resume Generator
Personal project to automatically generate html/pdf resumes from json/yaml data files.
Generate a beautiful, single-file HTML resume from a JSON resume file using Jinja2 templates.



## Installation

```bash
uv install
```

## Usage

### CLI

Generate HTML resume from JSON or YAML file:

```bash
uv run main.py input/resume.yaml --output output/resume.html \
  --profile-photo input/profile.jpg
```

Or use the default output name:

```bash
uv run main.py input/resume.json
```

> `input/` is git-ignored so you can keep private resumes locally without committing them.

### Python API

```python
from pathlib import Path
from resume_generator import Resume, ResumeGenerator, load_resume_data

# Load resume data from either JSON or YAML
data = load_resume_data(Path("input/resume.yaml"))

# Create resume model
resume = Resume(**data)

# Generate HTML
generator = ResumeGenerator(profile_photo=Path("input/profile.jpg"))
html = generator.generate_html(resume)

# Or save to file
generator.generate_html_file(resume, 'resume.html')
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
  "interests": [
    {
      "name": "Software Development"
    }
  ]
}
```

## Development

### Tooling

- Lint: `uv run ruff check .`
- Type check: `uv run ty check`
- Tests: `uv run pytest`
- Install hooks: `uv run pre-commit install`

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

MIT
