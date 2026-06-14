from intl_exam_guide.models import Qualification, SourceRecord, Topic
from intl_exam_guide.planning.guide_plan import build_guide_plan
from intl_exam_guide.providers.oxfordaqa import (
    Link,
    OxfordAQAProvider,
    PageParser,
    extract_assessments,
    extract_topics,
    find_source_snippets,
    find_specification_url,
)
from intl_exam_guide.validation.checks import validate_plan


def parse(html: str) -> PageParser:
    parser = PageParser("https://www.oxfordaqa.com/example/")
    parser.feed(html)
    return parser


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
        <p>OxfordAQA International AS/A-level Computer Science covers the following topics:</p>
        <ul><li>Procedural programming</li><li>Databases</li></ul>
        <h2>Teaching resources available</h2>
        """
    )
    topics = extract_topics(parser.nodes)
    assert [topic.title for topic in topics] == ["Procedural programming", "Databases"]


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
        <span>OxfordAQA International AS/A-level Business covers the following topics:</span>
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
    assert alevel.group_label == "red International AS/A-level subject listing"


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
            group_label="red International AS/A-level subject listing",
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
                    text="OxfordAQA International AS/A-level Business",
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
                audience_note="International AS/A-level modular qualification for international students.",
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
        ],
        ["Atomic structure", "isotopes"],
    )
    assert snippets[0].page == 2
    assert snippets[0].matched_term == "Atomic structure"
    assert "electron configuration" in snippets[0].text


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
