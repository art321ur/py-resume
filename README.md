# Resume Generator

Generate a beautiful, single-file HTML resume from a JSON resume file using Jinja2 templates.

## Features

- 📄 Generate single HTML file from JSON resume data
- 🎨 Beautiful, print-ready design with inlined CSS
- 🚀 No JavaScript required
- 🔤 Embedded fonts (Lato, Josefin Sans, Roboto)
- 📱 Responsive design for screen and print
- ✨ Clean, semantic HTML output

## Installation

```bash
uv install
```

## Usage

### CLI

Generate HTML resume from JSON file:

```bash
python main.py input.json --output resume.html
```

Or use the default output name:

```bash
python main.py input.json
```

### Python API

```python
from resume_generator import Resume, ResumeGenerator
import json

# Load resume data
with open('resume.json', 'r') as f:
    data = json.load(f)

# Create resume model
resume = Resume(**data)

# Generate HTML
generator = ResumeGenerator()
html = generator.generate_html(resume)

# Or save to file
generator.generate_html_file(resume, 'resume.html')
```

## Resume JSON Format

The resume follows the [JSON Resume](https://jsonresume.org/) schema. Example structure:

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
