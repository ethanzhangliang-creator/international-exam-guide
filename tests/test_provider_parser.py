from intl_exam_guide.models import Qualification, SourceRecord, SourceSnippet, Topic
from intl_exam_guide.planning.guide_plan import build_guide_plan
from intl_exam_guide.providers.oxfordaqa import (
    Link,
    OxfordAQAProvider,
    PageParser,
    attach_source_snippets,
    extract_assessments,
    extract_detailed_topics_from_pdf,
    extract_topics,
    find_source_snippets,
    find_specification_url,
    clean_text,
)
from intl_exam_guide.validation.checks import validate_plan


def parse(html: str) -> PageParser:
    parser = PageParser("https://www.oxfordaqa.com/example/")
    parser.feed(html)
    return parser


def test_clean_text_repairs_set_notation_pdf_symbol_duplication():
    text = clean_text("n(A), A\u2032, A \u222a B, A \u222a B, \u03be")
    assert text == "n(A), A\u2032, A \u222a B, A \u2229 B, \u03be"


def test_clean_text_does_not_rewrite_plain_repeated_union():
    text = clean_text("Compare A \u222a B, A \u222a B in two worked examples")
    assert text == "Compare A \u222a B, A \u222a B in two worked examples"


def test_extract_topics_with_group_headings():
    parser = parse(
        """
        <h2>Syllabus summary</h2>
        <p>OxfordAQA International GCSE Chemistry covers the following topics:</p>
        <h6>Atomic structure</h6>
        <ul><li>Atoms</li><li>The periodic table</li></ul>
        <h6>Organic chemistry</h6>
        <ul><li>Hydrocarbons</li></ul>
        <h2>Teaching resources available</h2>
        """
    )
    topics = extract_topics(parser.nodes)
    assert [topic.title for topic in topics] == ["Atomic structure", "Organic chemistry"]
    assert topics[0].points == ["Atoms", "The periodic table"]


def test_extract_topics_without_group_headings():
    parser = parse(
        """
        <h2>Syllabus summary</h2>
        <p>OxfordAQA International AS-A-level Computer Science covers the following topics:</p>
        <ul><li>Procedural programming</li><li>Databases</li></ul>
        <h2>Teaching resources available</h2>
        """
    )
    topics = extract_topics(parser.nodes)
    assert [topic.title for topic in topics] == ["Procedural programming", "Databases"]


def test_extract_detailed_topics_from_pdf_reference_codes():
    pages = [
        (
            10,
            """
            3 Subject content
            The content has been organised into broad topic areas and given a reference as follows:
            3.1 Number
            3.1.1 Structure and calculation
            N1
            Core content Extension content
            order positive and negative integers, decimals and fractions
            use the symbols =, !=, <, >
            N2
            Core content Extension content
            apply the four operations to integers and fractions
            N3
            Core content Extension content
            recognise and use inverse operations
            3.2 Algebra
            3.2.1 Notation and manipulation
            A1
            Core content Extension content
            use letters to express generalised numbers
            A2
            Core content Extension content
            substitute numbers for letters in formulae
            A3
            Core content Extension content
            understand expressions, equations, and formulae
            4 Scheme of Assessment
            """,
        )
    ]
    topics = extract_detailed_topics_from_pdf(pages)
    assert [topic.title for topic in topics] == [
        "N1 - Structure and calculation",
        "N2 - Structure and calculation",
        "N3 - Structure and calculation",
        "A1 - Notation and manipulation",
        "A2 - Notation and manipulation",
        "A3 - Notation and manipulation",
    ]
    assert topics[0].points[:2] == [
        "order positive and negative integers, decimals and fractions",
        "use the symbols =, !=, <, >",
    ]


def test_extract_detailed_topics_from_pdf_numeric_sections():
    pages = [
        (
            10,
            """
            3 Subject content
            3.1.1 Economic foundations
            Students study the central economic problem.
            3.1.1.1 Economic activity
            Content Additional information
            Needs and wants
            The central purpose of economic activity
            Students should be able to understand:
            the difference between a need and a want
            the key economic decisions are what to produce, how to produce, and who benefits
            3.1.1.2 The factors of production
            Content Additional information
            The factors of production
            land, labour, capital and enterprise
            3.1.2.1 Markets and allocation of resources
            Content Additional information
            Markets
            Allocation of resources
            Factor and product markets
            3.1.3.1 Demand for goods and services
            Content Additional information
            Demand
            The demand curve
            3.1.3.2 Supply for goods and services
            Content Additional information
            Supply
            The supply curve
            3.2.2.1 Economic objectives of a government
            Content Additional information
            Full employment
            Price stability
            Economic growth
            4 Scheme of assessment
            """,
        )
    ]
    topics = extract_detailed_topics_from_pdf(pages)
    assert [topic.title for topic in topics] == [
        "3.1.1.1 - Economic activity",
        "3.1.1.2 - The factors of production",
        "3.1.2.1 - Markets and allocation of resources",
        "3.1.3.1 - Demand for goods and services",
        "3.1.3.2 - Supply for goods and services",
        "3.2.2.1 - Economic objectives of a government",
    ]
    assert "the difference between a need and a want" in topics[0].points


def test_extract_detailed_topics_from_pdf_expands_body_tables_without_leaf_codes():
    pages = [
        (
            2,
            """
            Contents
            3 Subject content 10
            3.1 Sources and recording of data 10
            3.2 Verification of accounting records 12
            3.3 Development of the accounting model 13
            4 Scheme of assessment 19
            """,
        ),
        (
            10,
            """
            3 Subject content
            Students must demonstrate a good understanding of accounting principles.
            3.1 Sources and recording of data
            Content Additional information
            The double entry system including understanding of the use
            and the preparation of source documents.
            Source documents are:
            • purchase invoices
            • sales invoices
            Books of prime entry are:
            • purchases journal
            • sales journal
            Ledger accounts may be subdivided into:
            • receivables ledgers
            • payables ledgers
            The accounting equation.
            Prepare and understand accounting records based on source documents.
            3.2 Verification of accounting records
            Content Additional information
            Verification of the double entry records.
            Verification techniques are:
            • trial balance
            • bank reconciliation statements
            Prepare and understand the use of a trial balance.
            Explain the use and limitations of a trial balance.
            3.3 Development of the accounting model
            Content Additional information
            General accounting concepts used in the preparation of accounting records.
            Concepts are:
            • business entity
            • prudence
            Explain and apply the straight line and reducing balance methods of calculating depreciation.
            4 Scheme of assessment
            """,
        ),
    ]
    topics = extract_detailed_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]
    assert len(topics) >= 8
    assert any("Source documents" in title for title in titles), titles
    assert any("Books of prime entry" in title for title in titles), titles
    assert any("trial balance" in " ".join(topic.points).lower() for topic in topics)
    assert all(topic.points for topic in topics)
    assert {snippet.page for topic in topics for snippet in topic.source_snippets} == {10}


def test_extract_topics_with_strong_headings_and_paragraph_points():
    parser = parse(
        """
        <h2>Syllabus summary</h2>
        <p>OxfordAQA International GCSE Economics covers the following topics:</p>
        <strong>How markets work</strong>
        <p>Economic foundations</p>
        <p>Resource allocation</p>
        <strong>How the economy works</strong>
        <p>Government objectives</p>
        <p>International trade and the global economy</p>
        <h2>Teaching resources available</h2>
        """
    )
    topics = extract_topics(parser.nodes)
    assert [topic.title for topic in topics] == ["How markets work", "How the economy works"]
    assert topics[0].points == ["Economic foundations", "Resource allocation"]
    assert topics[1].points == ["Government objectives", "International trade and the global economy"]


def test_extract_topics_with_capitalized_span_syllabus_and_span_points():
    parser = parse(
        """
        <h3>International AS and A-level Business (9725)</h3>
        <span>Syllabus Summary</span>
        <span>OxfordAQA International AS-A-level Business covers the following topics:</span>
        <span>AS:</span>
        <span>What is business?</span>
        <span>Marketing</span>
        <span>A-level only:</span>
        <span>Strategic options</span>
        <span>Implementing a strategy</span>
        <span>Teaching resources</span>
        """
    )
    topics = extract_topics(parser.nodes)
    assert [topic.title for topic in topics] == ["AS", "A-level only"]
    assert topics[0].points == ["What is business?", "Marketing"]
    assert topics[1].points == ["Strategic options", "Implementing a strategy"]


def test_extract_topics_from_assessment_when_no_syllabus_summary():
    parser = parse(
        """
        <span>Assessment</span>
        <strong>Paper 1</strong>
        <p>• Families</p>
        <p>• Research methods</p>
        <p>• Written exam</p>
        <p>• 1 hour 30 minutes</p>
        <p>• 60 marks</p>
        <strong>Paper 2</strong>
        <p>• Differences and inequalities</p>
        <p>• Socialization and social control</p>
        <p>• 50% of GCSE</p>
        <span>Thinking about switching to OxfordAQA?</span>
        """
    )
    topics = extract_topics(parser.nodes)
    assert [topic.title for topic in topics] == ["Paper 1", "Paper 2"]
    assert topics[0].points == ["Families", "Research methods"]
    assert topics[1].points == ["Differences and inequalities", "Socialization and social control"]


def test_extract_project_assessments_without_paper_or_unit_labels():
    parser = parse(
        """
        <span>Assessment</span>
        <strong>Individual project</strong>
        <p>• Students choose a topic that develops their own study area.</p>
        <p>• 60%</p>
        <strong>Group sustainability action project</strong>
        <p>• Students work in groups on a sustainability themed action project.</p>
        <p>• 40%</p>
        <span>Thinking about switching to OxfordAQA?</span>
        """
    )
    papers = extract_assessments(parser.nodes)
    assert [paper.title for paper in papers] == ["Individual project", "Group sustainability action project"]
    assert "Students choose a topic" in papers[0].details[0]


def test_parser_captures_subject_listing_level_metadata():
    parser = parse(
        """
        <h3>Chemistry</h3>
        <a href="/qualifications/international-gcse-chemistry/" class="btn btn--type-8">
          <span>International GCSE Chemistry (9202)</span>
        </a>
        <a href="/qualifications/international-as-a-level-chemistry/" class="btn btn--type-7">
          <span>International AS and A-level Chemistry (9620)</span>
        </a>
        """
    )
    gcse, alevel = parser.links
    assert gcse.subject_heading == "Chemistry"
    assert gcse.qualification_type == "international_gcse"
    assert gcse.group_label == "blue International GCSE subject listing"
    assert gcse.style_class == "btn btn--type-8"
    assert alevel.qualification_type == "international_as_a_level"
    assert alevel.group_label == "red International AS-A-level subject listing"


def test_listing_metadata_promotes_unknown_epq_type():
    provider = OxfordAQAProvider()
    qualification = Qualification(
        title="International Extended Project Qualification (EPQ) (9695)",
        code="9695",
        qualification_type="unknown",
        subject_area="Project-based learning",
        page_url="https://www.oxfordaqa.com/qualifications/international-epq/",
        summary=[],
        topics=[],
        assessments=[],
        source=SourceRecord(
            provider="oxfordaqa",
            page_url="https://www.oxfordaqa.com/qualifications/international-epq/",
            specification_url="https://example.test/spec.pdf",
        ),
        audience_note="unknown",
    )
    provider.apply_listing_metadata(
        qualification,
        Link(
            text="International Extended Project Qualification (EPQ) (9695)",
            href=qualification.page_url,
            qualification_type="international_as_a_level",
            group_label="red International AS-A-level subject listing",
        ),
    )
    assert qualification.qualification_type == "international_as_a_level"
    assert "international students" in qualification.audience_note.lower()


def test_code_query_checks_detail_page_before_level_fallback():
    class FakeProvider(OxfordAQAProvider):
        def discover_subject_pages(self):
            return [Link(text="Business", href="https://example.test/subjects/business/")]

        def list_qualifications(self, subject_url: str):
            return [
                Link(
                    text="International AS and A-level Accounting (9615)",
                    href="https://example.test/accounting/",
                    qualification_type="international_as_a_level",
                ),
                Link(
                    text="OxfordAQA International AS-A-level Business",
                    href="https://example.test/business-revised/",
                    qualification_type="international_as_a_level",
                ),
            ]

        def parse_qualification(self, page_url: str):
            code = "9725" if "business" in page_url else "9615"
            title = (
                "International AS and A-level Business (9725) - revised"
                if code == "9725"
                else "International AS and A-level Accounting (9615)"
            )
            return Qualification(
                title=title,
                code=code,
                qualification_type="international_as_a_level",
                subject_area=None,
                page_url=page_url,
                summary=[],
                topics=[],
                assessments=[],
                source=SourceRecord(provider="test", page_url=page_url),
                audience_note="International AS-A-level modular qualification for international students.",
            )

    link = FakeProvider().find_qualification("9725", level="a-level")
    assert link.href == "https://example.test/business-revised/"
    assert "9725" in link.text


def test_find_specification_url_prefers_specification_pdf():
    parser = parse(
        """
        <a href="/foo.pdf">switching guide</a>
        <a href="/specification.pdf">Download the specification</a>
        """
    )
    assert find_specification_url(parser.links) == "https://www.oxfordaqa.com/specification.pdf"


def test_find_source_snippets_returns_page_references():
    snippets = find_source_snippets(
        [
            (1, "Intro text"),
            (2, "Atomic structure includes atoms, isotopes, and electron configuration."),
            (8, "Atomic structure includes atoms, isotopes, and electron configuration."),
        ],
        ["Atomic structure", "isotopes"],
    )
    assert snippets[0].page == 8
    assert snippets[0].matched_term == "Atomic structure"
    assert "electron configuration" in snippets[0].text


def test_attach_source_snippets_preserves_body_snippets_and_skips_contents_page():
    qualification = Qualification(
        title="International GCSE Accounting (9215)",
        code="9215",
        qualification_type="international_gcse",
        subject_area="Accounting",
        page_url="https://example.test/accounting/",
        summary=[],
        topics=[
            Topic(
                title="3.3.3 - The use of accounting concepts",
                points=["The use of accounting concepts in a variety of situations."],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Content Additional information The use of accounting concepts in a variety of situations.",
                        matched_term="3.3",
                    )
                ],
            )
        ],
        assessments=[],
        source=SourceRecord(provider="test", page_url="https://example.test/accounting/"),
        audience_note="International GCSE linear qualification for international students.",
    )
    attach_source_snippets(
        qualification,
        [
            (2, "Contents The use of accounting concepts in a variety of situations 12"),
            (12, "Content Additional information The use of accounting concepts in a variety of situations."),
        ],
    )
    assert [snippet.page for snippet in qualification.topics[0].source_snippets] == [12]


def test_validate_plan_checks_generated_guide_blocks():
    qualification = Qualification(
        title="International GCSE Example (9999)",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Example",
        page_url="https://example.test",
        summary=[],
        topics=[Topic(title="Atomic structure", points=["Atoms"])],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test",
            specification_url="https://example.test/spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students.",
    )
    plan = build_guide_plan(qualification)
    issues = validate_plan(plan)
    messages = [issue.message for issue in issues]
    assert "Topic guide coverage does not match topic count." not in messages
    assert any("No assessment papers" in message for message in messages)
