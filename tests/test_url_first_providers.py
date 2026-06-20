import pytest

from intl_exam_guide.providers import get_provider
from intl_exam_guide.providers.base import Link
from intl_exam_guide.providers import cambridge as cambridge_module
from intl_exam_guide.providers import pearson as pearson_module
from intl_exam_guide.providers.cambridge import CambridgeInternationalProvider
from intl_exam_guide.providers.cambridge import parse_exam_year
from intl_exam_guide.providers.cambridge import select_syllabus_link
from intl_exam_guide.providers.common import (
    TextNode,
    find_pdf_link,
    parse_assessment_objectives_from_pdf,
    parse_assessments_from_pdf,
    parse_command_words_from_pdf,
    parse_generic_topics_from_pdf,
    parse_pearson_subsection_line,
    parse_pearson_topic_tables,
)
from intl_exam_guide.providers.pearson import (
    PearsonEdexcelProvider,
    pearson_candidate_urls,
    pearson_is_specification_pdf,
    pearson_route_tags,
    pearson_subject_area,
)


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


def test_generic_pdf_parser_handles_pearson_learning_tables():
    pages = [
        (
            19,
            """
            Topic 1: The accounting environment
            What students need to learn:
            1 Types of
            business
            organisation
            a) Explain the characteristics of public sector organisations.
            b) Explain the connection between stakeholders and a business.
            2 Accounting
            concepts
            a) Understand the significance of consistency and prudence.
            b) Apply accounting concepts to simple scenarios.
            """,
        ),
        (
            21,
            """
            Topic 2: Introduction to bookkeeping
            What students need to learn:
            1 Business
            documentation
            a) Explain the purpose of business documents.
            b) Prepare purchase invoices and sales invoices.
            2 Books of original
            entry
            a) Explain the purpose of books of original entry.
            b) Prepare purchases and sales day books.
            3 Ledger
            accounting
            a) Explain the purpose of the nominal ledger.
            b) Record transactions using double entry principles.
            """,
        ),
        (
            23,
            """
            Topic 3: Introduction to control processes
            What students need to learn:
            1 Trial balance  a) Explain the purpose of a trial balance.
            b) Prepare a trial balance.
            2 Control accounts a) Explain the purpose of control accounts.
            b) Prepare trade receivables control accounts.
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)

    assert [topic.title for topic in topics[:7]] == [
        "1.1 - Types of business organisation",
        "1.2 - Accounting concepts",
        "2.1 - Business documentation",
        "2.2 - Books of original entry",
        "2.3 - Ledger accounting",
        "3.1 - Trial balance",
        "3.2 - Control accounts",
    ]
    assert "a) Explain the purpose of books of original entry." in topics[3].points


def test_pearson_learning_tables_ignore_trailing_front_matter():
    pages = [
        (
            17,
            """
            Paper 1: Introduction to Bookkeeping and Accounting
            Topic 1: The accounting environment
            What students need to learn:
            1 Types of business organisation a) Explain the characteristics of public sector organisations.
            b) Explain the connection between stakeholders and a business.
            2 Accounting concepts a) Understand consistency and prudence.
            b) Apply accounting concepts to simple scenarios.
            Topic 2: Introduction to bookkeeping
            What students need to learn:
            1 Business documentation a) Explain the purpose of business documents.
            2 Books of original entry a) Prepare purchases and sales day books.
            3 Ledger accounting a) Record transactions using double entry principles.
            Topic 3: Introduction to control processes
            What students need to learn:
            1 Trial balance a) Explain the purpose of a trial balance.
            2 Control accounts a) Prepare trade receivables control accounts.
            """,
        ),
        (
            42,
            """
            Specification - Issue 1 - October 2016 © Pearson Education Limited 2016
            We have guided Pearson through what we judge to be a rigorous world-class qualification
            development process that has included benchmarking assessments against UK and overseas providers.
            Professor Sing Kong Lee
            Chief Education Advisor, Pearson plc
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]
    joined = " ".join(titles + [point for topic in topics for point in topic.points])

    assert len(topics) >= 6
    assert any("Books of original entry" in title for title in titles)
    assert "Content unit" not in joined
    assert "Specification - Issue" not in joined
    assert "Pearson Education Limited" not in joined


def test_pearson_subsection_parser_rejects_noise_and_long_lines():
    assert parse_pearson_subsection_line("a) Explain the purpose of accounting.") is None
    assert parse_pearson_subsection_line("12") is None
    assert parse_pearson_subsection_line("1 " + "very long " * 20) is None

    assert parse_pearson_subsection_line(
        "2 Books of original entry a) Explain the purpose of books of original entry."
    ) == (
        "2",
        "Books of original entry",
        "a) Explain the purpose of books of original entry.",
    )


def test_pearson_topic_tables_stop_at_appendix_and_administration():
    pages = [
        (
            20,
            """
            Topic 1: The accounting environment
            What students need to learn:
            1 Types of business organisation a) Explain public sector organisations.
            b) Explain stakeholder connections.
            2 Accounting concepts a) Understand prudence.
            b) Apply consistency.
            Topic 2: Bookkeeping
            What students need to learn:
            1 Business documentation a) Explain invoices.
            b) Prepare credit notes.
            2 Ledger accounting a) Record transactions.
            b) Balance ledger accounts.
            Appendix 1 Formulae
            1 Assessment objectives a) This is not subject content.
            Administration arrangements
            Topic 9: Noise
            What students need to learn:
            1 Do not parse this a) It belongs to admin pages.
            """,
        )
    ]

    topics = parse_pearson_topic_tables(pages)
    titles = [topic.title for topic in topics]
    joined = " ".join(titles + [point for topic in topics for point in topic.points])

    assert "1.1 - Types of business organisation" in titles
    assert "2.2 - Ledger accounting" in titles
    assert "9.1 - Do not parse this" not in titles
    assert "Administration arrangements" not in joined


def test_generic_pdf_parser_does_not_treat_assessment_objectives_as_topics():
    pages = [
        (
            12,
            """
            Subject content
            1.1 The purpose of accounting
            Candidates should understand the role of accounting information.
            1.2 The accounting equation
            Candidates should understand assets, liabilities and capital.
            2.1 The double entry system of book-keeping
            Candidates should prepare ledger accounts.
            2.2 Business documents
            Candidates should understand invoices and credit notes.
            3.1 The trial balance
            Candidates should prepare and interpret a trial balance.
            3.2 Corrections of errors
            Candidates should correct errors and understand suspense accounts.
            """,
        ),
        (
            23,
            """
            Assessment objectives
            AO1 Knowledge and understanding
            AO2 Analysis
            AO3 Evaluation
            Paper 1 Paper 2
            AO1 Knowledge and understanding 80 60
            AO2 Analysis 20 25
            AO3 Evaluation 0 15
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]

    assert len(topics) >= 6
    assert any("The accounting equation" in title for title in titles)
    assert not any(title.startswith("AO") for title in titles)


def test_cambridge_content_overview_is_not_mixed_with_detailed_subject_content():
    pages = [
        (
            8,
            """
            Syllabus overview
            Content overview
            1 The fundamentals of accounting
            1.1 The purpose of accounting
            1.2 The accounting equation
            2 Sources and recording of data
            2.1 The double entry system of book-keeping
            2.2 Business documents
            2.3 Books of prime entry
            7 Accounting concepts and modern practice
            7.3 Technology and sustainability
            """,
        ),
        (
            11,
            """
            3 Subject content
            1.1 The purpose of accounting
            Candidates should have an understanding of:
            the difference between book-keeping and accounting
            the role of accounting in providing information
            1.2 The accounting equation
            Candidates should have an understanding of:
            assets, liabilities and owner’s equity
            how to apply the accounting equation
            2.1 The double entry system of book-keeping
            Candidates should have an understanding of:
            the dual effect of transactions
            how to prepare ledger accounts
            2.2 Business documents
            Candidates should have an understanding of:
            invoices, credit notes and statements of account
            how documents are used as sources of information
            2.3 Books of prime entry
            Candidates should have an understanding of:
            how to process accounting data in the books of prime entry
            how to post the ledger entries from the books of prime entry
            3.1 The trial balance
            Candidates should have an understanding of:
            how to prepare and use a trial balance
            how to identify errors not revealed by a trial balance
            4 Details of the assessment
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]

    assert titles[:6] == [
        "1.1 - The purpose of accounting",
        "1.2 - The accounting equation",
        "2.1 - The double entry system of book-keeping",
        "2.2 - Business documents",
        "2.3 - Books of prime entry",
        "3.1 - The trial balance",
    ]
    assert "7.3 - Technology and sustainability" not in titles


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


def test_pearson_subject_query_does_not_swallow_code_errors(monkeypatch):
    def fake_parse_page(_url):
        raise RuntimeError("parser bug")

    monkeypatch.setattr(pearson_module, "parse_page", fake_parse_page)

    with pytest.raises(RuntimeError, match="parser bug"):
        PearsonEdexcelProvider().find_qualification("Edexcel Accounting", "igcse")


def test_pearson_parse_qualification_extracts_spec_pdf_and_metadata(monkeypatch):
    parser = FakeParser(
        title="Pearson Edexcel International GCSE Accounting (2017)",
        links=[
            Link(
                text="Download specification",
                href="https://qualifications.pearson.com/content/dam/pdf/accounting-specification.pdf",
            ),
            Link(text="Past paper", href="https://example.test/past-paper.pdf"),
        ],
        nodes=[
            TextNode(tag="h1", text="Pearson Edexcel International GCSE Accounting (2017)"),
            TextNode(tag="p", text="First teaching: September 2017"),
            TextNode(tag="p", text="First external assessment: June 2019"),
        ],
    )

    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    qualification = PearsonEdexcelProvider().parse_qualification(
        "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-accounting-2017.html",
        "igcse",
    )

    assert qualification.provider == "pearson"
    assert qualification.qualification_type == "international_gcse"
    assert qualification.subject_area == "Accounting"
    assert qualification.source.specification_url.endswith("accounting-specification.pdf")
    assert qualification.source.first_teaching == "September 2017"
    assert qualification.source.first_assessment == "June 2019"
    assert "Pearson Edexcel" in qualification.route_tags


def test_pearson_parse_qualification_rejects_page_without_spec_pdf(monkeypatch):
    parser = FakeParser(
        title="Pearson Edexcel International GCSE Accounting (2017)",
        links=[Link(text="Welcome guide", href="https://example.test/welcome-guide.pdf")],
    )
    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    with pytest.raises(ValueError, match="No Pearson specification PDF link"):
        PearsonEdexcelProvider().parse_qualification("https://example.test/accounting.html", "igcse")


def test_pearson_rejects_non_specification_pdf_links_even_if_downloadable(monkeypatch):
    parser = FakeParser(
        title="Pearson Edexcel International GCSE Accounting (2017)",
        links=[
            Link(
                text="Download welcome guide",
                href="https://qualifications.pearson.com/content/dam/pdf/accounting-welcome-guide.pdf",
            ),
            Link(
                text="Download mark scheme",
                href="https://qualifications.pearson.com/content/dam/pdf/accounting-mark-scheme.pdf",
            ),
        ],
    )
    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    with pytest.raises(ValueError, match="No Pearson specification PDF link"):
        PearsonEdexcelProvider().parse_qualification("https://example.test/accounting.html", "igcse")


def test_pearson_helper_functions_cover_subject_area_and_route_tags():
    assert pearson_subject_area(
        "Pearson Edexcel International GCSE Accounting (2017)",
        "https://example.test/international-gcse-accounting-2017.html",
    ) == "Accounting"
    assert pearson_route_tags(
        "international_as_a_level",
        "https://example.test/biology-2018.html",
    ) == ["Pearson Edexcel", "modular"]
    assert pearson_route_tags(
        "international_gcse",
        "https://example.test/mathematics-2024-modular.html",
    ) == ["Pearson Edexcel", "modular"]
    assert pearson_is_specification_pdf("https://example.test/accounting-specification.pdf")
    assert not pearson_is_specification_pdf("https://example.test/accounting-past-paper.pdf")


def test_find_pdf_link_scores_include_terms_and_excludes_noise():
    parser = FakeParser(
        links=[
            Link(text="Past paper PDF", href="https://example.test/past-paper.pdf"),
            Link(text="Download specification", href="https://example.test/specification.pdf"),
            Link(text="Welcome guide", href="https://example.test/welcome-guide.pdf"),
        ]
    )

    assert find_pdf_link(
        parser,
        include_terms=("specification", "download"),
        exclude_terms=("past paper", "past-paper", "welcome"),
    ) == "https://example.test/specification.pdf"


def test_common_pdf_parser_extracts_assessments_command_words_and_objectives():
    pages = [
        (
            31,
            """
            Details of assessment
            Paper 1: Introduction to Bookkeeping and Accounting
            1 hour 30 minutes
            80 marks
            50%
            Written examination with structured questions.
            Paper 2: Financial Statements
            1 hour 45 minutes
            90 marks
            50%
            Written examination with questions based on accounting statements.
            """,
        ),
        (
            42,
            """
            Command words
            Calculate - Work out from given facts, figures or information.
            Explain - Set out purposes or reasons.
            Analyse - Examine in detail to show meaning.
            3 Appendix
            """,
        ),
        (
            44,
            """
            Assessment objectives
            AO1 Knowledge and understanding of accounting terms
            AO2 Application and analysis of accounting information
            AO3 Evaluation and judgement
            """,
        ),
    ]

    assessments = parse_assessments_from_pdf(pages)
    command_words = parse_command_words_from_pdf(pages)
    objectives = parse_assessment_objectives_from_pdf(pages)

    assert [paper.title for paper in assessments[:2]] == [
        "Paper 1: Introduction to Bookkeeping and Accounting",
        "Paper 2: Financial Statements",
    ]
    assert assessments[0].duration == "1 hour 30 minutes"
    assert assessments[0].marks == "80 marks"
    assert assessments[0].weighting == "50%"
    assert command_words[:3] == ["Calculate", "Explain", "Analyse"]
    assert objectives == [
        "AO1 Knowledge and understanding of accounting terms",
        "AO2 Application and analysis of accounting information",
        "AO3 Evaluation and judgement",
    ]


def test_cambridge_parse_qualification_uses_exam_year_to_choose_syllabus(monkeypatch):
    parser = FakeParser(
        title="Cambridge IGCSE Accounting (0452)",
        links=[
            Link(
                text="2023 - 2025 Syllabus",
                href="https://www.cambridgeinternational.org/Images/123-2023-2025-syllabus.pdf",
            ),
            Link(
                text="2026 - 2028 Syllabus",
                href="https://www.cambridgeinternational.org/Images/456-2026-2028-syllabus.pdf",
            ),
            Link(
                text="2026 - 2028 Syllabus update",
                href="https://www.cambridgeinternational.org/Images/999-2026-2028-syllabus-update.pdf",
            ),
        ],
    )
    monkeypatch.setattr(cambridge_module, "parse_page", lambda _url: parser)

    qualification = CambridgeInternationalProvider().parse_qualification(
        "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-0452/",
        "igcse",
        exam_year="2027",
    )

    assert qualification.provider == "cambridge"
    assert qualification.code == "0452"
    assert qualification.source.syllabus_year_range == "2026-2028"
    assert qualification.source.selected_exam_year == "2027"
    assert qualification.source.specification_url.endswith("456-2026-2028-syllabus.pdf")
    assert qualification.selected_exam_year == "2027"


def test_cambridge_parse_direct_pdf_validates_exam_year():
    qualification = CambridgeInternationalProvider().parse_qualification(
        "https://www.cambridgeinternational.org/Images/123-2026-2028-syllabus.pdf",
        "igcse",
        exam_year="2027",
    )

    assert qualification.source.syllabus_year_range == "2026-2028"
    assert qualification.source.selected_exam_year == "2027"
    assert qualification.source.specification_url.endswith("123-2026-2028-syllabus.pdf")


def test_cambridge_parse_direct_pdf_rejects_exam_year_outside_range():
    with pytest.raises(ValueError, match="does not match syllabus PDF range"):
        CambridgeInternationalProvider().parse_qualification(
            "https://www.cambridgeinternational.org/Images/123-2026-2028-syllabus.pdf",
            "igcse",
            exam_year="2029",
        )


def test_cambridge_parse_exam_year_requires_four_digit_year():
    with pytest.raises(ValueError, match="Invalid Cambridge exam year"):
        parse_exam_year("27")


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


def test_cambridge_subject_query_does_not_swallow_code_errors(monkeypatch):
    def fake_parse_page(_url):
        raise RuntimeError("parser bug")

    monkeypatch.setattr(cambridge_module, "parse_page", fake_parse_page)

    with pytest.raises(RuntimeError, match="parser bug"):
        CambridgeInternationalProvider().find_qualification("CAIE Accounting", "igcse")


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
