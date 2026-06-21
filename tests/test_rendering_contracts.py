import json

from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.planning.guide_plan import build_guide_plan
from intl_exam_guide.rendering.cover import (
    cover_version_label,
    exam_board_identity,
    qualification_type_display,
    render_cover,
    stripped_subject_title,
)
from intl_exam_guide.rendering.handbook_package import (
    slugify,
    write_handbook_package,
    write_visual_assets,
)
from intl_exam_guide.rendering.html import (
    display_topic_title,
    format_source_reference,
    image_provider_display,
    link_or_missing,
    localized_topic_title,
    render_assessments,
    render_html,
    render_language_policy,
    render_listing_note,
    render_practice,
    render_reference_appendix,
    render_revision_stages,
    render_source_note,
    render_source_snippets,
    render_story_modes,
    render_student_overview,
    render_summary,
    render_topic_diagram,
    render_topic_guide,
    render_topic_map,
    render_topic_nav,
    render_topics,
    render_visual_example,
    style_display,
    topic_anchor,
)
from intl_exam_guide.rendering.styles import stylesheet
from intl_exam_guide.rendering.visual_assets import (
    build_visual_asset_lookup,
    has_renderable_infographic,
    has_renderable_svg_fallback,
    is_raster_asset,
    is_svg_asset,
    load_visual_manifest,
    scientific_vector_route,
    visual_asset_key_from_brief,
    visual_asset_key_from_entry,
)


def sample_rendering_qualification() -> Qualification:
    return Qualification(
        title="International GCSE Accounting Example (9215)",
        code="9215",
        qualification_type="international_gcse",
        subject_area="Accounting",
        page_url="https://example.test/accounting/",
        summary=[
            "Students learn source documents, books of prime entry, ledgers, and statements."
        ],
        topics=[
            Topic(
                title="3.1 - Source documents",
                points=[
                    "Explain source documents and books of prime entry.",
                    "Prepare ledger entries from business evidence.",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Students should explain source documents and books of prime entry.",
                        matched_term="Source documents",
                    )
                ],
            )
        ],
        assessments=[
            AssessmentPaper(
                title="Paper 1",
                details=["1 hour 30 minutes", "80 marks", "50% of qualification"],
            )
        ],
        source=SourceRecord(
            provider="oxfordaqa",
            page_url="https://example.test/accounting/",
            specification_url="https://example.test/accounting-specification.pdf",
            specification_sha256="abc123",
        ),
        audience_note="International GCSE qualification for students outside the UK.",
        provider="OxfordAQA",
        qualification_family="International GCSE",
    )


def sample_topic_guide(topic_title: str = "3.1 - Source documents") -> TopicGuide:
    return TopicGuide(
        topic_title=topic_title,
        essence="Business evidence must flow into the right book before it reaches the ledger.",
        analogy="Treat each invoice like a boarding pass: it tells the transaction where to go.",
        mini_worked_example="A sales invoice is first recorded in the sales day book.",
        worked_solution_steps=[
            "Identify the source document.",
            "Choose the correct book of prime entry.",
            "Post the total to the relevant ledger account.",
        ],
        pitfall="Do not post every invoice straight into the final accounts.",
        checklist=[
            "Match invoices, credit notes, and receipts to the right record.",
            "Explain why books of prime entry reduce repeated ledger writing.",
            "Use ledger totals when preparing statements.",
        ],
        diagram_brief="Show source documents feeding books of prime entry and then ledgers.",
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Students should explain source documents and books of prime entry.",
                matched_term="Source documents",
            )
        ],
    )


def sample_practice_item(topic_title: str = "3.1 - Source documents") -> PracticeItem:
    return PracticeItem(
        topic_title=topic_title,
        command_word="Explain",
        difficulty="medium",
        focus_point="source document to book of prime entry",
        question="Explain where a sales invoice should be recorded first.",
        answer_frame=[
            "Name the source document.",
            "Name the first accounting book.",
            "Explain why this keeps records organised.",
        ],
        public_solution_steps=[
            "A sales invoice is evidence of a credit sale.",
            "It is recorded in the sales day book first.",
            "The total is later posted to the ledger.",
        ],
        answer_checkpoints=[
            "Sales invoice identified.",
            "Sales day book named.",
            "Ledger posting explained.",
        ],
        source_points=["Explain source documents and books of prime entry."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Students should explain source documents and books of prime entry.",
                matched_term="Source documents",
            )
        ],
    )


def sample_visual_brief(
    topic_title: str = "3.1 - Source documents",
    complexity: str = "svg-basic",
    image_provider: str = "deterministic-svg",
) -> VisualBrief:
    return VisualBrief(
        topic_title=topic_title,
        focus_point="source documents to ledger flow",
        trigger="multi-step accounting process",
        visual_type="ledger flow diagram",
        complexity=complexity,
        image_provider=image_provider,
        prompt="Create a clear source-document to ledger flow visual.",
        source_points=["Explain source documents and books of prime entry."],
    )


def test_stylesheet_keeps_handbook_cover_responsive_and_print_contracts():
    css = stylesheet()

    for selector in [
        ".cover {",
        ".cover-mast",
        ".cover-identity-grid",
        ".student-overview",
        ".topic-nav",
        ".practice-block",
        ".generated-infographic-grid",
        ".story-modes",
        "@media (max-width: 760px)",
        "@media print",
    ]:
        assert selector in css

    assert ".cover { min-height: 270mm" in css
    assert "print-color-adjust: exact" in css
    assert "letter-spacing: 0" in css


def test_cover_helpers_identify_three_boards_and_neutral_unknown_sources():
    qualification = sample_rendering_qualification()

    assert exam_board_identity(qualification)["short"] == "AQA"
    assert qualification_type_display(qualification) == "International GCSE"
    assert stripped_subject_title(qualification) == "Accounting Example"

    qualification.provider = None
    qualification.source.provider = "Pearson Edexcel"
    qualification.source.specification_url = "https://qualifications.pearson.com/spec.pdf"
    assert exam_board_identity(qualification) == {
        "short": "Edexcel",
        "full": "Pearson Edexcel International Qualifications",
        "class_name": "board-edexcel",
    }

    qualification.source.provider = "Cambridge International"
    qualification.source.specification_url = "https://www.cambridgeinternational.org/syllabus.pdf"
    assert exam_board_identity(qualification)["short"] == "CAIE"

    qualification.source.provider = "synthetic-demo"
    qualification.source.specification_url = "https://example.test/spec.pdf"
    assert exam_board_identity(qualification)["class_name"] == "board-neutral"


def test_cover_version_label_uses_issue_range_exam_year_then_pdf_fallback():
    qualification = sample_rendering_qualification()
    options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        exam_year="2028",
    )

    qualification.source.issue_version = "Issue 4"
    qualification.source.syllabus_year_range = "2027-2029"
    assert cover_version_label(qualification, options, "en") == "Issue 4"

    qualification.source.issue_version = None
    assert cover_version_label(qualification, options, "en") == "2027-2029 syllabus"

    qualification.source.syllabus_year_range = None
    assert cover_version_label(qualification, options, "en") == "2028 exams"

    options.exam_year = None
    qualification.selected_exam_year = None
    qualification.source.selected_exam_year = None
    assert cover_version_label(qualification, options, "en") == "See official specification/syllabus PDF"


def test_render_cover_keeps_first_page_to_course_identity():
    qualification = sample_rendering_qualification()
    options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        exam_year="2028",
    )

    html = render_cover(qualification, options)

    assert "Official exam board" in html
    assert "AQA" in html
    assert "Accounting Example" in html
    assert "Course code" in html
    assert "9215" in html
    assert "Target exam year" in html
    assert "2028" in html
    assert "Study Order" not in html
    assert "Knowledge units" not in html
    assert "Assessment Structure" not in html


def test_render_html_writes_full_handbook_from_manifest_assets(tmp_path):
    qualification = sample_rendering_qualification()
    guide = sample_topic_guide()
    practice = sample_practice_item()
    visual = sample_visual_brief()
    plan = GuidePlan(
        qualification=qualification,
        run_options=GuideRunOptions(
            requested_subject="Accounting",
            image_provider="deterministic-svg",
            explanation_style="friendly",
            output_language="en",
            exam_year="2028",
        ),
        topic_guides=[guide],
        practice_items=[practice],
        visual_briefs=[visual],
        diagram_briefs=[],
        revision_stages=["Read the source", "Work examples"],
    )
    manifest_path = tmp_path / "images" / "visual_manifest.json"
    manifest_path.parent.mkdir()
    manifest_path.write_text(
        json.dumps(
            [
                {
                    "key": visual_asset_key_from_brief(visual),
                    "file": "source-flow.svg",
                    "asset_status": "svg-draft",
                    "image_provider": "deterministic-svg",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    output_path = render_html(plan, tmp_path / "guide.html", manifest_path)
    html = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert '<html lang="en">' in html
    assert "International GCSE Accounting Example (9215) Revision Guide" in html
    assert "How to Study" in html
    assert "Study Roadmap" in html
    assert "Quick Navigation" in html
    assert "source documents to ledger flow" in html
    assert "Source Appendix" in html


def test_html_helpers_keep_source_policy_and_setup_copy_readable():
    qualification = sample_rendering_qualification()
    qualification.source.listing_subject = "Business and Accounting"
    qualification.source.listing_group_label = "blue International GCSE subject listing"
    qualification.source.listing_style_class = "btn btn--type-8"
    options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="custom",
        image_model="SenseNova U1 Fast",
        image_endpoint_url="https://images.example.test/v1/images/generations",
        image_api_key_env="IMAGE_KEY",
        explanation_style="detective",
        output_language="en",
    )

    overview = render_student_overview(qualification, ["Read the source", "Practise twice"], options)
    source_note = render_source_note(qualification, "en")
    policy = render_language_policy()

    assert "custom illustration model: SenseNova U1 Fast" in overview
    assert "Writing style: Detective" in overview
    assert "Audience and Sources" in source_note
    assert "Business and Accounting" in source_note
    assert "blue International GCSE subject listing" in source_note
    assert "PDF SHA-256" in source_note
    assert "one selected output language" in policy
    assert style_display("life", "en") == "Life Scene"
    assert image_provider_display(options, "en") == "custom illustration model: SenseNova U1 Fast"
    assert "warning" in link_or_missing(None, "en")
    assert render_listing_note(qualification, "en") == (
        '<p class="listing-note">Subject group: Business and Accounting · '
        "Website group: blue International GCSE subject listing · "
        "Detected class: btn btn--type-8</p>"
    )
    assert topic_anchor(12) == "topic-12"


def test_chinese_html_helpers_have_direct_contracts():
    qualification = sample_rendering_qualification()
    qualification.source.listing_subject = "Accounting"
    qualification.source.listing_group_label = "AQA International GCSE"
    qualification.source.listing_style_class = "subject-card"
    custom_options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="custom",
        image_model="SenseNova U1 Fast",
        explanation_style="friendly",
        output_language="zh-CN",
    )
    prompt_options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="zh-CN",
    )
    svg_options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="deterministic-svg",
        explanation_style="friendly",
        output_language="zh-CN",
    )

    assert style_display("friendly", "zh-CN") != "Friendly"
    assert style_display("unknown-style", "zh-CN") == "unknown-style"
    assert "SenseNova U1 Fast" in image_provider_display(custom_options, "zh-CN")
    assert "custom illustration model" not in image_provider_display(custom_options, "zh-CN")
    assert "infographic prompts prepared" not in image_provider_display(prompt_options, "zh-CN")
    assert "simple diagrams are included" not in image_provider_display(svg_options, "zh-CN")

    listing_note = render_listing_note(qualification, "zh-CN")
    source_note = render_source_note(qualification, "zh-CN")
    revision_stages = render_revision_stages(["第一轮通读", "第二轮做题"], "zh-CN")

    assert "Subject group" not in listing_note
    assert "Accounting" in listing_note
    assert "AQA International GCSE" in listing_note
    assert "Audience and Sources" not in source_note
    assert "Qualification page" not in source_note
    assert "https://example.test/accounting/" in source_note
    assert "PDF SHA-256" in source_note
    assert "Three-Stage Revision" not in revision_stages
    assert "第一轮通读" in revision_stages
    assert "第二轮做题" in revision_stages
    assert "missing" not in link_or_missing(None, "zh-CN")
    assert "warning" in link_or_missing(None, "zh-CN")


def test_render_html_writes_chinese_handbook_directly(tmp_path):
    qualification = sample_rendering_qualification()
    guide = sample_topic_guide()
    practice = sample_practice_item()
    visual = sample_visual_brief()
    plan = GuidePlan(
        qualification=qualification,
        run_options=GuideRunOptions(
            requested_subject="Accounting",
            image_provider="deterministic-svg",
            explanation_style="friendly",
            output_language="zh-CN",
            exam_year="2028",
        ),
        topic_guides=[guide],
        practice_items=[practice],
        visual_briefs=[visual],
        diagram_briefs=[],
        revision_stages=["第一轮通读", "第二轮做题"],
    )

    output_path = render_html(plan, tmp_path / "guide-zh.html")
    html = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert '<html lang="zh-CN">' in html
    assert "How to Study" not in html
    assert "Study Roadmap" not in html
    assert "Quick Navigation" not in html
    assert "Source Appendix" not in html
    assert "guide.html" not in html
    assert "deterministic-svg" not in html


def test_topic_renderers_cover_guides_practice_story_and_visual_blocks():
    qualification = sample_rendering_qualification()
    topic = qualification.topics[0]
    guide = sample_topic_guide()
    practice = sample_practice_item()
    visual = sample_visual_brief()

    rendered_topics = render_topics(
        [topic],
        [guide],
        [practice],
        [visual],
        {},
        "en",
    )

    assert 'id="topic-1"' in rendered_topics
    assert "Key Ideas" in rendered_topics
    assert "Exam Logic" in rendered_topics
    assert "One-Sentence Essence" in rendered_topics
    assert "Concept Map" in rendered_topics
    assert "Visual Worked Example" in rendered_topics
    assert "Life Scene" in rendered_topics
    assert "Worked Example" in rendered_topics
    assert "Explain where a sales invoice should be recorded first." in rendered_topics
    assert rendered_topics.count("<article class=\"practice\">") == 1

    assert "Everyday Analogy" in render_topic_guide(guide, "en")
    assert "Concept map for 3.1 - Source documents" in render_topic_diagram(topic, guide, 1, "en")
    assert "Local SVG draft" in render_visual_example(topic, guide, visual, 1, {}, "en")
    assert "Image model slot: custom-provider" in render_visual_example(
        topic,
        guide,
        sample_visual_brief(image_provider="custom-provider"),
        1,
        {},
        "en",
    )
    assert "Narrative explanation styles" in render_story_modes(topic, guide, "en", 1)
    assert "Source documents - Worked Example" in render_practice(practice, "en")


def test_topic_renderers_cover_missing_guides_and_empty_topic_fallbacks():
    empty_topic = Topic(title="Unmapped topic", points=[])

    html = render_topics([empty_topic], [], [], [], None, "en")

    assert "Use the official specification text to expand this topic" in html
    assert "One-Sentence Essence" not in html
    assert "Visual Worked Example" not in html
    assert "No page-level source snippet was matched" in html
    assert '<div class="practice-block"></div>' in html


def test_infographic_visual_branch_uses_manifest_asset_when_available():
    qualification = sample_rendering_qualification()
    topic = qualification.topics[0]
    guide = sample_topic_guide()
    visual = sample_visual_brief(
        complexity="infographic",
        image_provider="external-generation-required",
    )
    asset = {
        "file": "accounting-flow.png",
        "asset_status": "reviewed-generated",
        "image_provider": "external-reviewed-workflow",
    }

    html = render_visual_example(
        topic,
        guide,
        visual,
        1,
        {visual_asset_key_from_brief(visual): asset},
        "en",
    )

    assert "Generated Infographic" in html
    assert "accounting-flow.png" in html
    assert "external-reviewed-workflow - reviewed visual asset" in html


def test_secondary_html_sections_and_chinese_rendering_paths():
    qualification = sample_rendering_qualification()
    qualification.assessments = []
    qualification.source.specification_sha256 = None
    guide = sample_topic_guide()
    topic = Topic(
        title="Demand and supply",
        points=["Market demand shifts"],
        source_snippets=[
            SourceSnippet(
                page=33,
                text="Learners should understand changes in demand and supply.",
                matched_term="Demand and supply",
            )
        ],
    )
    chinese_topic = Topic(title="中文主题名称很长但应该保持可读", points=[])

    assert "Course Position" in render_summary(qualification, "en")
    assert "warning" in render_assessments(qualification, "en")
    assert "Study Roadmap" in render_topic_map([topic], "en", [guide])
    assert "Use the specification text" in render_topic_map([Topic(title="No points", points=[])], "en")
    assert "Quick Navigation" in render_topic_nav([topic], "en")
    assert "Three-Stage Revision" in render_revision_stages(["Plan", "Practise"], "en")
    assert "Generated practice examples" in render_reference_appendix(qualification, 3, "en")
    assert "Source: review required" == format_source_reference(None, "en", include_prefix=True)
    assert "Source: p.33 - Demand and supply" == format_source_reference(
        topic.source_snippets[0],
        "en",
        include_prefix=True,
    )
    assert "href=\"https://example.test/spec.pdf\"" in link_or_missing(
        "https://example.test/spec.pdf",
        "en",
    )

    chinese_map = render_topic_map([topic], "zh-CN", [guide])
    chinese_nav = render_topic_nav([topic], "zh-CN")
    chinese_story = render_story_modes(topic, guide, "zh-CN", 1)
    chinese_source = render_source_snippets(topic.source_snippets, language="zh-CN")
    chinese_title = display_topic_title(chinese_topic, 4, "zh-CN")

    assert "topic-1" in chinese_map
    assert "topic-1" in chinese_nav
    assert "story-modes" in chinese_story
    assert "source-snippets" in chinese_source
    assert localized_topic_title("probability and statistics", 1) == "统计与概率"
    assert localized_topic_title(chinese_topic.title, 4) == chinese_topic.title[:32]
    assert chinese_title == chinese_topic.title[:32]
    assert display_topic_title(Topic(title="A2 Topic title", points=[]), 2, "zh-CN") == "第 A2 节"
    assert format_source_reference(topic.source_snippets[0], "zh-CN") == (
        "第 33 页（官方原文见结构化来源文件）"
    )


def test_chinese_html_rendering_paths_have_direct_contracts():
    qualification = sample_rendering_qualification()
    topic = qualification.topics[0]
    guide = sample_topic_guide()
    practice = sample_practice_item()
    visual = sample_visual_brief(
        topic_title=topic.title,
        complexity="svg-basic",
        image_provider="deterministic-svg",
    )
    options = GuideRunOptions(
        requested_subject="Accounting",
        image_provider="deterministic-svg",
        explanation_style="friendly",
        output_language="zh-CN",
        exam_year="2028",
    )

    overview = render_student_overview(qualification, ["第一轮通读", "第二轮做题"], options)
    summary = render_summary(qualification, "zh-CN")
    assessments = render_assessments(qualification, "zh-CN")
    topics = render_topics([topic], [guide], [practice], [visual], {}, "zh-CN")
    topic_guide = render_topic_guide(guide, "zh-CN")
    topic_diagram = render_topic_diagram(topic, guide, 1, "zh-CN")
    visual_example = render_visual_example(topic, guide, visual, 1, {}, "zh-CN")
    practice_html = render_practice(practice, "zh-CN", "会计记录")
    appendix = render_reference_appendix(qualification, 1, "zh-CN")

    assert "怎么用这本手册" in overview
    assert "科目：会计学" in overview
    assert "课程定位" in summary
    assert "考试结构" in assessments
    assert "T1." in topics
    assert "本节要掌握" in topics
    assert "做题逻辑" in topics
    assert "一句话本质" in topic_guide
    assert "图文解释" in topic_diagram
    assert "本地矢量图草图" in visual_example
    assert "图形例题" in visual_example
    assert "会计记录 - 例题" in practice_html
    assert "附录：来源与考试信息" in appendix
    assert "生成例题数量" in appendix


def test_source_snippets_and_topic_titles_have_direct_rendering_guards():
    long_text = "Matched syllabus statement. " * 20
    snippets = [SourceSnippet(page=7, text=long_text, matched_term="Ledger accounts")]

    compact = render_source_snippets(snippets, compact=True, language="en")
    missing = render_source_snippets([], language="en")

    assert "p.7" in compact
    assert "Ledger accounts" in compact
    assert "..." in compact
    assert "Review manually" in missing
    assert display_topic_title(Topic(title="Demand and supply", points=[]), 2, "en") == "Demand and supply"
    assert slugify("Long Topic: source documents / ledger entries!") == (
        "long-topic-source-documents-ledger-entries"
    )
    assert slugify("!!!") == "topic"


def test_visual_manifest_loading_and_asset_classification_edges(tmp_path):
    manifest_path = tmp_path / "visual_manifest.json"

    assert load_visual_manifest(tmp_path) == []
    manifest_path.write_text("{not-json", encoding="utf-8")
    assert load_visual_manifest(tmp_path) == []
    manifest_path.write_text('{"not": "a list"}', encoding="utf-8")
    assert load_visual_manifest(manifest_path) == []
    manifest_path.write_text(
        json.dumps(
            [
                {
                    "topic_title": " Bonding ",
                    "focus_point": " Ionic ",
                    "visual_type": " Chart ",
                    "complexity": " svg-basic ",
                },
                "ignore me",
            ]
        ),
        encoding="utf-8",
    )

    entries = load_visual_manifest(tmp_path)
    assert len(entries) == 1
    assert visual_asset_key_from_entry(entries[0]) == "bonding||ionic||chart||svg-basic"
    assert build_visual_asset_lookup(entries) == {
        "bonding||ionic||chart||svg-basic": entries[0]
    }

    assert is_raster_asset("diagram.PNG")
    assert not is_raster_asset("diagram.svg")
    assert not is_raster_asset(None)
    assert is_svg_asset("diagram.SVG")
    assert not is_svg_asset("diagram.webp")
    assert scientific_vector_route("axis graph and data table") == "scripted-scientific-vector"
    assert scientific_vector_route("labelled accounting records flow") == "hand-authored-svg"


def test_renderable_asset_checks_require_matching_status_extension_and_file(tmp_path):
    png_entry = {"file": "visual.png", "asset_status": "REVIEWED-GENERATED"}
    svg_entry = {"file": "visual.svg", "asset_status": "svg-fallback-needs-review"}

    assert has_renderable_infographic(png_entry)
    assert not has_renderable_infographic({"file": "visual.svg", "asset_status": "generated"})
    assert not has_renderable_infographic(png_entry, tmp_path)
    (tmp_path / "visual.png").write_bytes(b"png")
    assert has_renderable_infographic(png_entry, tmp_path)

    assert has_renderable_svg_fallback(svg_entry)
    assert not has_renderable_svg_fallback({"file": "visual.png", "asset_status": "svg-fallback-needs-review"})
    assert not has_renderable_svg_fallback(svg_entry, tmp_path)
    (tmp_path / "visual.svg").write_text("<svg></svg>", encoding="utf-8")
    assert has_renderable_svg_fallback(svg_entry, tmp_path)


def test_write_visual_assets_preserves_generated_raster_and_rebuilds_svg_manifest(tmp_path):
    svg_brief = VisualBrief(
        topic_title="Statistics chart",
        focus_point="draw a bar chart",
        trigger="simple chart",
        visual_type="statistics chart",
        complexity="svg-basic",
        image_provider="deterministic-svg",
        prompt="Draw a simple chart.",
        source_points=["draw a bar chart"],
    )
    raster_brief = VisualBrief(
        topic_title="Ledger flow",
        focus_point="source document to ledger",
        trigger="complex process",
        visual_type="ledger flow infographic",
        complexity="infographic",
        image_provider="external-generation-required",
        prompt="Create a ledger flow infographic.",
        source_points=["source documents"],
    )
    fallback_brief = VisualBrief(
        topic_title="Market flow",
        focus_point="demand and supply",
        trigger="complex market",
        visual_type="demand-supply infographic",
        complexity="infographic",
        image_provider="external-generation-required",
        prompt="Create a demand and supply infographic.",
        source_points=["demand and supply"],
    )
    plan = GuidePlan(
        qualification=sample_rendering_qualification(),
        run_options=GuideRunOptions(
            requested_subject="Accounting",
            image_provider="deterministic-svg",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[],
        practice_items=[],
        visual_briefs=[svg_brief, raster_brief, fallback_brief],
        diagram_briefs=[],
        revision_stages=[],
    )
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "old.svg").write_text("<svg>old</svg>", encoding="utf-8")
    (images_dir / "ledger.png").write_bytes(b"png")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "key": visual_asset_key_from_brief(raster_brief),
                    "file": "ledger.png",
                    "asset_status": "reviewed-generated",
                    "image_provider": "external-reviewed-workflow",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    written = write_visual_assets(plan, images_dir)
    manifest = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))

    assert not (images_dir / "old.svg").exists()
    assert len(written) == 3
    assert [entry["asset_status"] for entry in manifest] == [
        "svg-draft",
        "reviewed-generated",
        "svg-fallback-needs-review",
    ]
    assert manifest[0]["fallback_route"] == "scripted-scientific-vector"
    assert manifest[1]["file"] == "ledger.png"
    assert manifest[2]["file"].endswith("-svg-fallback.svg")
    assert (images_dir / manifest[0]["file"]).exists()
    assert (images_dir / manifest[2]["file"]).exists()


def test_write_handbook_package_writes_modular_sections_manifest_and_images(tmp_path):
    qualification = sample_rendering_qualification()
    plan = build_guide_plan(
        qualification,
        image_provider="deterministic-svg",
        explanation_style="friendly",
        output_language="en",
        requested_subject="Accounting",
    )

    manifest = write_handbook_package(plan, tmp_path)

    assert manifest["section_files"] == [
        "00_css.txt",
        "01_cover.txt",
        "02_study_overview.txt",
        "03_topic_map.txt",
        "03_topic_navigation.txt",
        "04_topic_guides_and_examples.txt",
        "05_source_appendix.txt",
    ]
    assert len(manifest["image_files"]) == len(plan.visual_briefs)
    assert (tmp_path / "handbook-package.json").exists()
    assert (tmp_path / "sections" / "01_cover.txt").read_text(encoding="utf-8").count("AQA")
    assert "How to Study" in (tmp_path / "sections" / "02_study_overview.txt").read_text(
        encoding="utf-8"
    )
    assert "Worked Example" in (
        tmp_path / "sections" / "04_topic_guides_and_examples.txt"
    ).read_text(encoding="utf-8")
    assert "</body></html>" in (tmp_path / "sections" / "05_source_appendix.txt").read_text(
        encoding="utf-8"
    )
    assert (tmp_path / "images" / "visual_manifest.json").exists()
