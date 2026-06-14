from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def export_pdf(html_path: Path, pdf_path: Path) -> Path:
    """Export PDF with a local Chromium-family browser if available."""
    browser = find_browser()
    if not browser:
        raise RuntimeError("No Chrome or Edge executable found for headless PDF export.")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_uri = html_path.resolve().as_uri()
    with tempfile.TemporaryDirectory() as tmp:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            f"--user-data-dir={tmp}",
            f"--print-to-pdf={str(pdf_path.resolve())}",
            html_uri,
        ]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    return pdf_path


def find_browser() -> str | None:
    candidates = [
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None
