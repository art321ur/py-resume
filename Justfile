set shell := ["powershell.exe", "-Command"]

resume-generate:
    $dir = if ($env:RESUME_ARCHIVE_DIR) { $env:RESUME_ARCHIVE_DIR } else { (Resolve-Path ..\resume-archive).Path }
    uv run .\main.py generate --input-file (Join-Path $dir "input\\resume.yaml") --output-file (Join-Path $dir "output\\resume.html") --profile-photo (Join-Path $dir "input\\profile.jpg") --force

resume-pdf:
    $dir = if ($env:RESUME_ARCHIVE_DIR) { $env:RESUME_ARCHIVE_DIR } else { (Resolve-Path ..\resume-archive).Path }
    uv run .\main.py pdf --html-file (Join-Path $dir "output\\resume.html") --output-file (Join-Path $dir "output\\resume.pdf") --force

resume-full:
    $dir = if ($env:RESUME_ARCHIVE_DIR) { $env:RESUME_ARCHIVE_DIR } else { (Resolve-Path ..\resume-archive).Path }
    uv run .\main.py full --input-file (Join-Path $dir "input\\resume.yaml") --output-file (Join-Path $dir "output\\resume.html") --profile-photo (Join-Path $dir "input\\profile.jpg") --pdf-file (Join-Path $dir "output\\resume.pdf") --force