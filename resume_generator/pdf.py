"""HTML to PDF conversion helpers using Playwright."""
from __future__ import annotations

import asyncio
import html
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright

_FONT_READY_JS = (
    "(async () => { if (document.fonts && document.fonts.ready) { "
    "await document.fonts.ready; } })()"
)


async def html_to_pdf(
    html_content: str,
    output_path: Path,
    base_url: Optional[str] = None,
) -> None:
    """Render the given HTML into a PDF file using Playwright."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(args=["--disable-web-security"])
        context = await browser.new_context(bypass_csp=True)
        page = await context.new_page()

        if base_url:
            await page.goto(base_url, wait_until="networkidle")
        else:
            await page.set_content(html_content, wait_until="networkidle")

        try:
            await page.wait_for_load_state("networkidle")
            await page.evaluate(_FONT_READY_JS)
        except Exception:
            pass

        await page.pdf(path=str(output_path), format="A4", print_background=True)

        await context.close()
        await browser.close()


def render_pdf_from_html_file(html_file: Path, output_file: Optional[Path] = None) -> Path:
    """Convert an HTML file to PDF using the async Playwright renderer."""
    html_path = Path(html_file)
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")

    target_path = Path(output_file) if output_file else html_path.with_suffix(".pdf")
    html_content = html.unescape(html_path.read_text(encoding="utf-8"))
    base_uri = html_path.resolve().as_uri()

    asyncio.run(html_to_pdf(html_content, target_path, base_url=base_uri))
    return target_path
