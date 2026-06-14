from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(pdf_path: Path, max_pages: int | None = None) -> list[tuple[int, str]]:
    """Extract text by page so downstream content can cite page-level snippets."""
    reader = PdfReader(str(pdf_path))
    pages = reader.pages[:max_pages] if max_pages else reader.pages
    result: list[tuple[int, str]] = []
    for index, page in enumerate(pages, start=1):
        result.append((index, (page.extract_text() or "").strip()))
    return result


def extract_pdf_text(pdf_path: Path, max_pages: int | None = None) -> str:
    """Extract text from a PDF with page separators for traceability."""
    chunks: list[str] = []
    for index, text in extract_pdf_pages(pdf_path, max_pages=max_pages):
        chunks.append(f"\n\n--- Page {index} ---\n{text.strip()}")
    return "\n".join(chunks).strip()
