set shell := ["powershell.exe", "-Command"]

resume-generate:
    uv run .\main.py generate --input-file .\input\resume.yaml --output_file .\output\resume222.html --profile_photo .\input\profile.jpg

resume-pdf:
    uv run .\main.py pdf --html-file .\output\resume222.html --output_file .\output\resume222.pdf

resume-full:
    uv run .\main.py full --input-file .\input\resume.yaml --output_file .\output\resume222.html --profile_photo .\input\profile.jpg --pdf-file .\output\resume222.pdf
