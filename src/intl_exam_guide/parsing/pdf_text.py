from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PdfTextExtractionError(ValueError):
    """Raised when a source PDF cannot be opened or read as text."""


def extract_pdf_pages(pdf_path: Path, max_pages: int | None = None) -> list[tuple[int, str]]:
    """Extract text by page so downstream content can cite page-level snippets."""
    if not pdf_path.exists():
        raise PdfTextExtractionError(f"PDF file does not exist: {pdf_path}")

    try:
        reader = PdfReader(str(pdf_path))
    except (OSError, PdfReadError, ValueError) as exc:
        raise PdfTextExtractionError(f"Could not read PDF: {pdf_path}") from exc

    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")
        except (NotImplementedError, PdfReadError, ValueError) as exc:
            raise PdfTextExtractionError(f"Encrypted PDF could not be decrypted: {pdf_path}") from exc
        if getattr(reader, "is_encrypted", False):
            raise PdfTextExtractionError(f"Encrypted PDF could not be decrypted: {pdf_path}")

    pages = reader.pages[:max_pages] if max_pages else reader.pages
    result: list[tuple[int, str]] = []
    for index, page in enumerate(pages, start=1):
        try:
            text = page.extract_text() or ""
        except (PdfReadError, ValueError, TypeError) as exc:
            raise PdfTextExtractionError(
                f"Could not extract text from page {index} of PDF: {pdf_path}"
            ) from exc
        result.append((index, text.strip()))
    return result


def extract_pdf_text(pdf_path: Path, max_pages: int | None = None) -> str:
    """Extract text from a PDF with page separators for traceability."""
    chunks: list[str] = []
    for index, text in extract_pdf_pages(pdf_path, max_pages=max_pages):
        chunks.append(f"\n\n--- Page {index} ---\n{text.strip()}")
    return "\n".join(chunks).strip()
