set shell := ["powershell.exe", "-Command"]

resume-generate:
    uv run .\main.py generate --options.input-file .\input\resume.yaml --options.output-file .\output\resume.html --options.profile-photo .\input\profile.jpg --options.force=true

resume-pdf:
    uv run .\main.py pdf --options.html-file .\output\resume.html --options.output-file .\output\resume.pdf --options.force=true

resume-full:
    uv run .\main.py full --options.input-file .\input\resume.yaml --options.output-file .\output\resume.html --options.profile-photo .\input\profile.jpg --options.pdf-file .\output\resume.pdf --options.force=true