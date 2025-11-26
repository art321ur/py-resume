set shell := ["powershell.exe", "-Command"]

resume-generate:
    uv run .\main.py generate --input-file .\input\resume.yaml --output-file .\output\resume.html --profile-photo .\input\profile.jpg --force

resume-pdf:
    uv run .\main.py pdf --html-file .\output\resume.html --output-file .\output\resume.pdf --force

resume-full:
    uv run .\main.py full --input-file .\input\resume.yaml --output-file .\output\resume.html --profile-photo .\input\profile.jpg --pdf-file .\output\resume.pdf --force