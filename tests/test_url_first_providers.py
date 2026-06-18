import pytest

from intl_exam_guide.providers import get_provider
from intl_exam_guide.providers.base import Link
from intl_exam_guide.providers import cambridge as cambridge_module
from intl_exam_guide.providers import pearson as pearson_module
from intl_exam_guide.providers.cambridge import CambridgeInternationalProvider
from intl_exam_guide.providers.cambridge import select_syllabus_link
from intl_exam_guide.providers.common import parse_generic_topics_from_pdf
from intl_exam_guide.providers.pearson import PearsonEdexcelProvider, pearson_candidate_urls


class FakeParser:
    def __init__(self, title="", links=None, nodes=None):
        self.title = title
        self.links = links or []
        self.nodes = nodes or []


def test_url_first_providers_are_registered():
    assert get_provider("pearson").name == "pearson"
    assert get_provider("edexcel").name == "pearson"
    assert get_provider("cambridge").name == "cambridge"
    assert get_provider("caie").name == "cambridge"


def test_generic_pdf_parser_handles_pearson_split_topic_codes():
    pages = [
        (
            17,
            """
            1.1
            Integers
            A understand and use integers
            B understand place value
            1.2
            Fractions
            A understand equivalent fractions
            B use mixed numbers
            1.3
            Decimals
            A use decimal notation
            B understand place value
            1.4
            Powers and roots
            A identify square numbers
            B use index notation
            1.5
            Set language and notation
            A understand set notation
            B use Venn diagrams
            1.6
            Percentages
            A convert between percentages
            B calculate percentage change
            3 Assessment information
            """,
        )
    ]

    topics = parse_generic_topics_from_pdf(pages)

    assert [topic.title for topic in topics[:6]] == [
        "1.1 - Integers",
        "1.2 - Fractions",
        "1.3 - Decimals",
        "1.4 - Powers and roots",
        "1.5 - Set language and notation",
        "1.6 - Percentages",
    ]
    assert all(topic.points for topic in topics)


def test_cambridge_subject_page_requires_exam_year_when_ranges_are_ambiguous():
    links = [
        Link(
            text="2023 - 2025 Syllabus (PDF, 693KB)",
            href="https://www.cambridgeinternational.org/Images/123-2023-2025-syllabus.pdf",
        ),
        Link(
            text="2026 - 2028 Syllabus (PDF, 1MB)",
            href="https://www.cambridgeinternational.org/Images/456-2026-2028-syllabus.pdf",
        ),
    ]

    with pytest.raises(ValueError, match="Please provide --exam-year"):
        select_syllabus_link(links, None)

    chosen = select_syllabus_link(links, "2027")
    assert chosen.href.endswith("456-2026-2028-syllabus.pdf")
    assert chosen.syllabus_year_range == "2026-2028"
    assert chosen.selected_exam_year == "2027"


def test_cambridge_subject_page_rejects_unmatched_exam_year():
    links = [
        Link(
            text="2026 - 2028 Syllabus (PDF, 1MB)",
            href="https://www.cambridgeinternational.org/Images/456-2026-2028-syllabus.pdf",
        ),
        Link(
            text="2029 - 2031 Syllabus (PDF, 1MB)",
            href="https://www.cambridgeinternational.org/Images/789-2029-2031-syllabus.pdf",
        ),
    ]

    with pytest.raises(ValueError, match="does not match any syllabus range"):
        select_syllabus_link(links, "2032")


def test_pearson_subject_query_resolves_unique_official_candidate(monkeypatch):
    def fake_parse_page(url):
        if url.endswith("/international-gcse-accounting-2017.html"):
            return FakeParser(title="Edexcel International GCSE Accounting (2017)")
        raise OSError("not found")

    monkeypatch.setattr(pearson_module, "parse_page", fake_parse_page)

    link = PearsonEdexcelProvider().find_qualification("Edexcel Accounting", "igcse")

    assert link.href.endswith("/international-gcse-accounting-2017.html")
    assert link.qualification_type == "international_gcse"


def test_pearson_igcse_subject_slug_preserves_mathematics_a_suffix():
    urls = pearson_candidate_urls("Edexcel Mathematics A", "igcse")

    assert any(url.endswith("/international-gcse-mathematics-a-2016.html") for url in urls)


def test_pearson_subject_query_lists_multiple_candidates(monkeypatch):
    def fake_parse_page(url):
        if "biology" in url:
            return FakeParser(title=f"Edexcel {url.rsplit('/', 1)[-1]}")
        raise OSError("not found")

    monkeypatch.setattr(pearson_module, "parse_page", fake_parse_page)

    with pytest.raises(ValueError) as exc:
        PearsonEdexcelProvider().find_qualification("Biology", None)

    message = str(exc.value)
    assert "multiple official candidates" in message
    assert "international-gcse-biology-2017.html" in message
    assert "biology-2018.html" in message


def test_cambridge_subject_query_lists_ambiguous_level_and_codes(monkeypatch):
    links = [
        Link(
            text="Accounting - 0452",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-0452/",
        ),
        Link(
            text="Accounting (9-1) - 0985",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-9-1-0985/",
        ),
        Link(
            text="Accounting - 9706",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-accounting-9706/",
        ),
    ]

    monkeypatch.setattr(cambridge_module, "parse_page", lambda _url: FakeParser(links=links))

    with pytest.raises(ValueError) as exc:
        CambridgeInternationalProvider().find_qualification("CAIE Accounting", None)

    message = str(exc.value)
    assert "0452" in message
    assert "0985" in message
    assert "9706" in message


def test_cambridge_subject_query_uses_code_to_resolve_unique_candidate(monkeypatch):
    links = [
        Link(
            text="Accounting - 0452",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-0452/",
        ),
        Link(
            text="Accounting (9-1) - 0985",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-9-1-0985/",
        ),
    ]

    monkeypatch.setattr(cambridge_module, "parse_page", lambda _url: FakeParser(links=links))

    link = CambridgeInternationalProvider().find_qualification("Accounting 0452", "igcse")

    assert link.href.endswith("cambridge-igcse-accounting-0452/")
    assert link.qualification_type == "international_gcse"
