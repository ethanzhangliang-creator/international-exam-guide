import json

from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
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
    image_provider_display,
    link_or_missing,
    render_language_policy,
    render_source_note,
    render_source_snippets,
    render_student_overview,
    style_display,
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
    assert build_visual_asset_lookup(entries)

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
