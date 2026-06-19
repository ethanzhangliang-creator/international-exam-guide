from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class PdfExportError(RuntimeError):
    """Raised when neither Playwright nor a local browser can export the PDF."""


def export_pdf(html_path: Path, pdf_path: Path) -> Path:
    """Export PDF with Playwright when available, then fall back to a local browser."""
    errors: list[str] = []
    try:
        return export_pdf_with_playwright(html_path, pdf_path)
    except PdfExportError as exc:
        errors.append(str(exc))

    try:
        return export_pdf_with_browser_cli(html_path, pdf_path)
    except PdfExportError as exc:
        errors.append(str(exc))

    raise PdfExportError("PDF export failed. " + " ".join(errors))


def export_pdf_with_playwright(html_path: Path, pdf_path: Path) -> Path:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise PdfExportError("Playwright is not installed.") from exc

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_uri = html_path.resolve().as_uri()
    launch_errors: list[str] = []
    with sync_playwright() as playwright:
        for channel in ("chrome", "msedge", None):
            browser = None
            try:
                launch_kwargs = {"headless": True}
                if channel:
                    launch_kwargs["channel"] = channel
                browser = playwright.chromium.launch(**launch_kwargs)
                page = browser.new_page()
                page.goto(html_uri, wait_until="load")
                page.pdf(
                    path=str(pdf_path.resolve()),
                    print_background=True,
                    prefer_css_page_size=True,
                )
                return pdf_path
            except PlaywrightError as exc:
                label = channel or "bundled chromium"
                launch_errors.append(f"{label}: {exc}")
            finally:
                if browser:
                    browser.close()
    raise PdfExportError(
        "Playwright could not launch a Chromium browser. "
        + " ".join(error.splitlines()[0] for error in launch_errors)
    )


def export_pdf_with_browser_cli(html_path: Path, pdf_path: Path) -> Path:
    """Export PDF with a local Chromium-family browser if available."""
    browser = find_browser()
    if not browser:
        raise PdfExportError("No Chrome or Edge executable found for headless PDF export.")

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
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired as exc:
            raise PdfExportError("Browser PDF export timed out after 300 seconds.") from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "").strip().splitlines()
            suffix = f" {detail[0]}" if detail else ""
            raise PdfExportError(f"Browser PDF export failed.{suffix}") from exc
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
