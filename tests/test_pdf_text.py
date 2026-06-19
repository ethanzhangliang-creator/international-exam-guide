from pypdf import PdfWriter

from intl_exam_guide.parsing.pdf_text import PdfTextExtractionError, extract_pdf_pages


def test_extract_pdf_pages_reads_blank_pdf(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with pdf_path.open("wb") as handle:
        writer.write(handle)

    assert extract_pdf_pages(pdf_path) == [(1, "")]


def test_extract_pdf_pages_reports_missing_file(tmp_path):
    try:
        extract_pdf_pages(tmp_path / "missing.pdf")
    except PdfTextExtractionError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("Expected PdfTextExtractionError")


def test_extract_pdf_pages_reports_invalid_pdf(tmp_path):
    pdf_path = tmp_path / "broken.pdf"
    pdf_path.write_text("not a pdf", encoding="utf-8")

    try:
        extract_pdf_pages(pdf_path)
    except PdfTextExtractionError as exc:
        assert "Could not read PDF" in str(exc)
    else:
        raise AssertionError("Expected PdfTextExtractionError")
