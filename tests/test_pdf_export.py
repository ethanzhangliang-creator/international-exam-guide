from pathlib import Path
import sys

from intl_exam_guide.rendering import pdf


def test_export_pdf_falls_back_to_browser_cli(monkeypatch, tmp_path):
    html_path = tmp_path / "guide.html"
    pdf_path = tmp_path / "guide.pdf"
    html_path.write_text("<html><body>guide</body></html>", encoding="utf-8")

    def fail_playwright(_html_path: Path, _pdf_path: Path) -> Path:
        raise pdf.PdfExportError("Playwright unavailable.")

    def browser_cli(_html_path: Path, target_pdf_path: Path) -> Path:
        target_pdf_path.write_bytes(b"%PDF-1.4\n")
        return target_pdf_path

    monkeypatch.setattr(pdf, "export_pdf_with_playwright", fail_playwright)
    monkeypatch.setattr(pdf, "export_pdf_with_browser_cli", browser_cli)

    assert pdf.export_pdf(html_path, pdf_path) == pdf_path
    assert pdf_path.exists()


def test_export_pdf_reports_both_routes_when_all_fail(monkeypatch, tmp_path):
    html_path = tmp_path / "guide.html"
    pdf_path = tmp_path / "guide.pdf"
    html_path.write_text("<html><body>guide</body></html>", encoding="utf-8")

    def fail_playwright(_html_path: Path, _pdf_path: Path) -> Path:
        raise pdf.PdfExportError("Playwright unavailable.")

    def fail_browser_cli(_html_path: Path, _pdf_path: Path) -> Path:
        raise pdf.PdfExportError("No browser found.")

    monkeypatch.setattr(pdf, "export_pdf_with_playwright", fail_playwright)
    monkeypatch.setattr(pdf, "export_pdf_with_browser_cli", fail_browser_cli)

    try:
        pdf.export_pdf(html_path, pdf_path)
    except pdf.PdfExportError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected PdfExportError")

    assert "Playwright unavailable" in message
    assert "No browser found" in message


def test_find_browser_uses_cross_platform_path_names(monkeypatch):
    seen: list[str] = []

    def fake_which(name: str) -> str | None:
        seen.append(name)
        if name == "chromium":
            return sys.executable
        return None

    monkeypatch.setattr(pdf.shutil, "which", fake_which)

    assert pdf.find_browser() == sys.executable
    assert "google-chrome" in seen
    assert "chromium" in seen
