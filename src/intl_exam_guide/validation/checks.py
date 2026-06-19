from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re

from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.visual_assets import (
    PENDING_ASSET_STATUSES,
    has_renderable_infographic,
    has_renderable_svg_fallback,
    is_raster_asset,
    load_visual_manifest,
)


@dataclass
class ValidationIssue:
    severity: str
    message: str


BILINGUAL_LABEL_PATTERNS = [
    "Chinese / English",
    "中文 / English",
    "图文学习页 / Visual Guide",
    "复习路线 / Study Roadmap",
    "例题 / Worked Example",
]
BILINGUAL_SLASH_PATTERN = re.compile(
    r"(?:[\u4e00-\u9fff][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[A-Za-z]"
    r"|[A-Za-z][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[\u4e00-\u9fff])"
)
ZH_FORBIDDEN_TEMPLATE_PHRASES = [
    "How to Study",
    "Study Roadmap",
    "One-Sentence Essence",
    "Everyday Analogy",
    "Worked Example",
    "Try First",
    "Solution",
    "Check",
    "Exam Pitfall",
    "Source anchor",
    "Concept Map",
    "Visual Worked Example",
    "Generated Infographic",
    "Infographic Queue",
    "Local SVG draft",
    "Why not SVG",
    "Prompt queue",
    "Output language: English",
    "官方大纲要求",
]


def validate_plan(
    plan: GuidePlan,
    html_path: Path | None = None,
    pdf_path: Path | None = None,
    output_dir: Path | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(validate_preflight_and_source(plan))
    issues.extend(validate_topic_coverage(plan))
    issues.extend(validate_guides(plan))
    issues.extend(validate_practice(plan))
    issues.extend(validate_visual_briefs(plan))
    issues.extend(validate_qualification_notes(plan))
    if html_path:
        issues.extend(validate_html_output(plan, html_path))
    if pdf_path and not pdf_path.exists():
        issues.append(ValidationIssue("warning", f"PDF output is missing: {pdf_path}"))
    if output_dir:
        issues.extend(validate_output_package(plan, output_dir))
    return issues


def validate_preflight_and_source(plan: GuidePlan) -> list[ValidationIssue]:
    qualification = plan.qualification
    options = plan.run_options
    issues: list[ValidationIssue] = []

    if not options.requested_subject.strip():
        issues.append(ValidationIssue("error", "Missing preflight subject selection."))
    if options.explanation_style not in {"formal", "friendly", "life", "story", "detective", "adventure"}:
        issues.append(ValidationIssue("error", "Missing or unsupported explanation style selection."))
    if options.output_language not in {"en", "zh-CN"}:
        issues.append(ValidationIssue("error", "Missing or unsupported output language selection."))
    if options.image_provider not in {"prompt-queue", "deterministic-svg", "custom"}:
        issues.append(ValidationIssue("error", "Missing or unsupported image-provider selection."))
    if options.image_provider == "custom":
        issues.extend(validate_custom_image_provider(options))

    if not qualification.source.page_url:
        issues.append(ValidationIssue("error", "Missing source qualification page URL."))
    if not qualification.source.provider:
        issues.append(ValidationIssue("error", "Missing source provider name."))
    if not qualification.source.specification_url:
        issues.append(ValidationIssue("error", "Missing specification PDF URL."))
    if not qualification.source.specification_sha256:
        issues.append(ValidationIssue("warning", "Specification PDF hash was not recorded."))
    if not qualification.topics:
        issues.append(ValidationIssue("error", "No syllabus topics were extracted."))
    if qualification.source.specification_path and len(qualification.topics) < 6:
        issues.append(
            ValidationIssue(
                "error",
                f"Only {len(qualification.topics)} syllabus topics were extracted from a downloaded specification PDF.",
            )
        )
    if qualification.source.specification_path and any(
        topic.title.lower().startswith("content unit ") for topic in qualification.topics
    ):
        issues.append(
            ValidationIssue(
                "error",
                "Downloaded specification fell back to generic Content unit topics; "
                "the syllabus parser needs a more precise provider-specific match.",
            )
        )
    if (
        (qualification.source.provider == "cambridge" or qualification.provider == "cambridge")
        and qualification.source.syllabus_year_range
        and not qualification.source.selected_exam_year
    ):
        issues.append(
            ValidationIssue(
                "error",
                "Cambridge syllabus range is present but selected exam year was not recorded.",
            )
        )
    if not qualification.assessments:
        severity = "error" if qualification.source.specification_path else "warning"
        issues.append(ValidationIssue(severity, "No assessment papers were extracted."))
    if len(plan.practice_items) < len(qualification.topics):
        issues.append(ValidationIssue("warning", "Practice coverage is below one item per topic."))
    if len(plan.topic_guides) != len(qualification.topics):
        issues.append(ValidationIssue("error", "Topic guide coverage does not match topic count."))
    if not plan.visual_briefs:
        issues.append(ValidationIssue("warning", "No topics were selected for visual explanation."))
    return issues


def validate_custom_image_provider(options: object) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not getattr(options, "image_model", None):
        issues.append(ValidationIssue("error", "Custom image provider is missing a model name."))
    if not getattr(options, "image_endpoint_url", None):
        issues.append(ValidationIssue("error", "Custom image provider is missing an endpoint URL."))
    api_key_env = getattr(options, "image_api_key_env", None)
    if not api_key_env:
        issues.append(
            ValidationIssue(
                "error",
                "Custom image provider is missing an API-key environment variable name.",
            )
        )
    elif not os.environ.get(api_key_env):
        issues.append(
            ValidationIssue(
                "error",
                f"Custom image provider environment variable is not set: {api_key_env}",
            )
        )
    return issues


def validate_topic_coverage(plan: GuidePlan) -> list[ValidationIssue]:
    guide_topics = {guide.topic_title for guide in plan.topic_guides}
    practice_topics = {item.topic_title for item in plan.practice_items}
    issues: list[ValidationIssue] = []
    for topic in plan.qualification.topics:
        if topic.title not in guide_topics:
            issues.append(ValidationIssue("error", f"Missing authored guide block for topic: {topic.title}"))
        if topic.title not in practice_topics:
            issues.append(ValidationIssue("error", f"Missing practice item for topic: {topic.title}"))
        if not topic.points:
            issues.append(ValidationIssue("error", f"Syllabus topic has no extracted body points: {topic.title}"))
        if not topic.source_snippets:
            issues.append(ValidationIssue("warning", f"No PDF source snippet matched for topic: {topic.title}"))
        elif all(is_contents_or_index_snippet(snippet) for snippet in topic.source_snippets):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Topic source snippets look like contents/index pages, not syllabus body: {topic.title}",
                )
            )
    return issues


def validate_guides(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for guide in plan.topic_guides:
        required = [
            guide.essence,
            guide.analogy,
            guide.mini_worked_example,
            guide.pitfall,
            guide.diagram_brief,
        ]
        if any(not value.strip() for value in required):
            issues.append(ValidationIssue("error", f"Incomplete topic guide block: {guide.topic_title}"))
        if len(guide.worked_solution_steps) < 4:
            issues.append(
                ValidationIssue(
                    "warning",
                    f"Worked example has fewer than 4 public steps: {guide.topic_title}",
                )
            )
        if len(guide.checklist) < 3:
            issues.append(ValidationIssue("warning", f"Checklist is too short: {guide.topic_title}"))
        if plan.run_options.output_language == "zh-CN" and has_zh_placeholder_text(
            [
                guide.essence,
                guide.analogy,
                guide.mini_worked_example,
                guide.pitfall,
                guide.diagram_brief,
                *guide.worked_solution_steps,
                *guide.checklist,
            ]
        ):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Chinese topic guide contains generic syllabus placeholder text: {guide.topic_title}",
                )
            )
    return issues


def validate_practice(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for item in plan.practice_items:
        issues.extend(validate_practice_item(plan, item))
    for topic_title in duplicate_practice_question_topics(plan.practice_items):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice items repeat the same question for topic: {topic_title}",
            )
        )
    return issues


def validate_practice_item(plan: GuidePlan, item: object) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    topic_title = getattr(item, "topic_title", "")
    if not item.command_word.strip():
        issues.append(ValidationIssue("error", f"Practice item is missing a command word: {topic_title}"))
    if not item.difficulty.strip():
        issues.append(ValidationIssue("error", f"Practice item is missing a difficulty: {topic_title}"))
    if not item.focus_point.strip():
        issues.append(ValidationIssue("error", f"Practice item is missing a focus point: {topic_title}"))
    if len(item.public_solution_steps) < 4:
        issues.append(ValidationIssue("error", f"Practice item has too few solution steps: {topic_title}"))
    if len(item.answer_checkpoints) < 3:
        issues.append(ValidationIssue("error", f"Practice item has too few answer checkpoints: {topic_title}"))
    if not item.source_points:
        issues.append(ValidationIssue("error", f"Practice item has no source points: {topic_title}"))
    if is_placeholder_practice_question(item.question):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice item is an authoring frame, not a concrete worked example: {topic_title}",
            )
        )
    if is_cross_subject_borrowed_practice(item.question, plan.qualification.subject_area):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice item appears to borrow a different subject template: {topic_title}",
            )
        )
    if plan.run_options.output_language == "zh-CN" and has_zh_placeholder_text(
        [
            item.question,
            item.command_word,
            item.focus_point,
            *item.public_solution_steps,
            *item.answer_checkpoints,
            *item.source_points,
        ]
    ):
        issues.append(
            ValidationIssue(
                "error",
                f"Chinese practice item contains generic syllabus placeholder text: {topic_title}",
            )
        )
    return issues


def validate_visual_briefs(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for brief in plan.visual_briefs:
        if not brief.focus_point.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing a focus point: {brief.topic_title}"))
        if not brief.visual_type.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing a visual type: {brief.topic_title}"))
        if not brief.trigger.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing the selection reason: {brief.topic_title}"))
        if not brief.image_provider.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing an image provider: {brief.topic_title}"))
        if not brief.prompt.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing an image prompt: {brief.topic_title}"))
        if plan.run_options.output_language == "zh-CN" and has_zh_placeholder_text(
            [brief.focus_point, brief.visual_type, brief.trigger, brief.prompt]
        ):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Chinese visual brief contains generic syllabus placeholder text: {brief.topic_title}",
                )
            )
    return issues


def validate_qualification_notes(plan: GuidePlan) -> list[ValidationIssue]:
    qualification = plan.qualification
    issues: list[ValidationIssue] = []
    if qualification.qualification_type == "international_gcse":
        if (
            qualification.source.listing_qualification_type
            and qualification.source.listing_qualification_type != "international_gcse"
        ):
            issues.append(ValidationIssue("error", "Source listing metadata conflicts with International GCSE type."))
        if "international students" not in qualification.audience_note.lower():
            issues.append(
                ValidationIssue(
                    "warning",
                    "GCSE audience note does not explicitly mention international students.",
                )
            )
        if (
            "outside the uk" not in qualification.audience_note.lower()
            and "outside the united kingdom" not in qualification.audience_note.lower()
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    "GCSE audience note does not explain that the course is for use outside the UK.",
                )
            )
        if "linear" not in " ".join([qualification.audience_note, *qualification.summary]).lower():
            issues.append(
                ValidationIssue("warning", "GCSE guide does not mention the linear qualification structure.")
            )
    if qualification.qualification_type == "international_as_a_level":
        if (
            qualification.source.listing_qualification_type
            and qualification.source.listing_qualification_type != "international_as_a_level"
        ):
            issues.append(ValidationIssue("error", "Source listing metadata conflicts with AS-A-level type."))
        if (
            (qualification.provider or qualification.source.provider) != "cambridge"
            and "modular" not in " ".join([qualification.audience_note, *qualification.summary]).lower()
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    "AS-A-level guide does not mention the modular qualification structure.",
                )
            )
    return issues


def validate_html_output(plan: GuidePlan, html_path: Path) -> list[ValidationIssue]:
    if not html_path.exists():
        return [ValidationIssue("error", f"HTML output is missing: {html_path}")]

    html = html_path.read_text(encoding="utf-8", errors="replace")
    options = plan.run_options
    qualification = plan.qualification
    issues: list[ValidationIssue] = []
    for label in mixed_language_label_matches(html):
        issues.append(
            ValidationIssue(
                "error",
                f"HTML contains a bilingual mixed-language label: {label}",
            )
        )
    for index, topic in enumerate(qualification.topics, start=1):
        marker = expected_topic_marker(topic.title, index, options.output_language)
        if marker not in html:
            issues.append(ValidationIssue("error", f"Topic missing from HTML: {marker}"))
    issues.extend(validate_html_language(options.output_language, html))
    issues.extend(validate_html_visual_and_diagram_blocks(plan, html))
    return issues


def validate_html_language(output_language: str, html: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if output_language == "en":
        if re.search(r"[\u4e00-\u9fff]", html):
            issues.append(
                ValidationIssue(
                    "error",
                    "English output contains Chinese characters in the student-facing HTML.",
                )
            )
        required_phrases = [
            "How to Study",
            "Study Roadmap",
            "One-Sentence Essence",
            "Method",
            "Worked Example",
            "Solution",
            "Check",
            "Exam Pitfall",
            "Source anchor",
            "Concept Map",
        ]
    else:
        for phrase in ZH_FORBIDDEN_TEMPLATE_PHRASES:
            if phrase in html:
                issues.append(
                    ValidationIssue(
                        "error",
                        f"Chinese output contains an English template phrase: {phrase}",
                    )
                )
        required_phrases = [
            "怎么用这本手册",
            "复习路线",
            "一句话本质",
            "解题套路",
            "例题",
            "解题步骤",
            "检查答案",
            "考试陷阱",
            "来源依据",
            "图文解释",
        ]
    for phrase in required_phrases:
        if phrase not in html:
            issues.append(ValidationIssue("error", f"HTML missing required section phrase: {phrase}"))
    return issues


def validate_html_visual_and_diagram_blocks(plan: GuidePlan, html: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if plan.visual_briefs:
        visual_markers = (
            [
                "Visual Worked Example",
                "Infographic Queue",
                "Generated Infographic",
                "SVG Fallback - Review Needed",
            ]
            if plan.run_options.output_language == "en"
            else ["图形例题", "信息图生成队列", "已生成信息图", "SVG 兜底图 - 需要复核"]
        )
        if not any(marker in html for marker in visual_markers):
            issues.append(ValidationIssue("error", "HTML missing required visual explanation block."))
    diagram_count = html.count('class="topic-diagram"')
    if diagram_count < len(plan.qualification.topics):
        issues.append(
            ValidationIssue(
                "error",
                f"HTML has {diagram_count} topic diagrams for {len(plan.qualification.topics)} topics.",
            )
        )
    return issues


def validate_output_package(plan: GuidePlan, output_dir: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sections_dir = output_dir / "sections"
    images_dir = output_dir / "images"
    package_manifest = output_dir / "handbook-package.json"
    if not sections_dir.exists():
        issues.append(ValidationIssue("error", f"Sections directory is missing: {sections_dir}"))
    else:
        section_count = len(list(sections_dir.glob("*.txt")))
        if section_count < 5:
            issues.append(
                ValidationIssue(
                    "error",
                    f"Sections directory has only {section_count} section files.",
                )
            )
    if not images_dir.exists():
        issues.append(ValidationIssue("error", f"Images directory is missing: {images_dir}"))
    elif plan.visual_briefs:
        issues.extend(validate_image_assets(plan, images_dir))
    if not (output_dir / "run-options.json").exists():
        issues.append(ValidationIssue("error", "Run options file is missing from output directory."))
    if not package_manifest.exists():
        issues.append(ValidationIssue("error", f"Handbook package manifest is missing: {package_manifest}"))
    return issues


def validate_image_assets(plan: GuidePlan, images_dir: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    svg_briefs = [brief for brief in plan.visual_briefs if brief.complexity == "svg-basic"]
    infographic_briefs = [brief for brief in plan.visual_briefs if brief.complexity == "infographic"]
    svg_count = len(list(images_dir.glob("*.svg")))
    if svg_count < len(svg_briefs):
        issues.append(
            ValidationIssue(
                "error",
                f"Images directory has {svg_count} SVG drafts for {len(svg_briefs)} SVG-safe visual briefs.",
            )
        )
    manifest_path = images_dir / "visual_manifest.json"
    manifest_entries = load_visual_manifest(images_dir)
    if not manifest_path.exists():
        issues.append(ValidationIssue("error", "Visual manifest is missing from images directory."))
    for entry in manifest_entries:
        filename = entry.get("file")
        if filename and not (images_dir / str(filename)).exists():
            issues.append(
                ValidationIssue(
                    "error",
                    f"Visual manifest references a missing image file: {filename}",
                )
            )
    if infographic_briefs:
        issues.extend(validate_infographic_assets(infographic_briefs, manifest_entries, images_dir))
    return issues


def validate_infographic_assets(
    infographic_briefs: list[object],
    manifest_entries: list[dict[str, object]],
    images_dir: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    generated = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic" and has_renderable_infographic(entry, images_dir)
    )
    svg_fallbacks = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic" and has_renderable_svg_fallback(entry, images_dir)
    )
    pending_external_generation = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic"
        and str(entry.get("asset_status", "")).lower() in PENDING_ASSET_STATUSES
    )
    if pending_external_generation:
        fallback_note = (
            f"; {svg_fallbacks} SVG fallback assets were written for draft review"
            if svg_fallbacks
            else ""
        )
        issues.append(
            ValidationIssue(
                "warning",
                f"{pending_external_generation} infographic briefs are queued for external image generation or review"
                f"{fallback_note}.",
            )
        )
    selected_or_generated = len(infographic_briefs) - pending_external_generation
    if generated < selected_or_generated:
        issues.append(
            ValidationIssue(
                "warning",
                f"{generated}/{selected_or_generated} selected infographic briefs have generated raster assets.",
            )
        )
    return issues


def is_placeholder_practice_question(question: str) -> bool:
    text = question.lower()
    return (
        ("how the syllabus idea" in text and "could be used in an exam question" in text)
        or "answer an original short exam-style question" in text
        or "identify the relevant evidence, choose the correct method or definition" in text
    )


def has_zh_placeholder_text(values: list[str]) -> bool:
    placeholder_patterns = [
        r"官方大纲要求",
        r"本单元第\s*\d+\s*个细分要求",
        r"第\s*\d+\s*个细分要求",
        r"知识单元\s*\d+",
        r"知识点\s*\d+",
    ]
    return any(
        re.search(pattern, value)
        for value in values
        for pattern in placeholder_patterns
    )


def duplicate_practice_question_topics(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    questions_by_topic: dict[str, set[str]] = {}
    counts_by_topic: dict[str, int] = {}
    for item in items:
        topic_title = getattr(item, "topic_title", "")
        question = normalize_practice_question(getattr(item, "question", ""))
        if not topic_title or not question:
            continue
        questions_by_topic.setdefault(topic_title, set()).add(question)
        counts_by_topic[topic_title] = counts_by_topic.get(topic_title, 0) + 1
    return [
        topic_title
        for topic_title, count in counts_by_topic.items()
        if len(questions_by_topic.get(topic_title, set())) < count
    ]


def normalize_practice_question(question: str) -> str:
    text = re.sub(
        r"^(Case file: |Real-life prompt: |Warm-up prompt: |Exam-style prompt: "
        r"|Story prompt: |Checkpoint challenge: |案件线索：|生活场景题：|热身题："
        r"|考试题：|故事题：|闯关挑战：)",
        "",
        question,
    )
    return re.sub(r"\s+", " ", text).strip().lower()


def is_contents_or_index_snippet(snippet: object) -> bool:
    text = getattr(snippet, "text", "").lower()
    page = getattr(snippet, "page", 999)
    syllabus_body_markers = [
        "content additional information",
        "students should",
        "prepare and",
        "understand",
        "calculate",
        "explain",
    ]
    if any(marker in text for marker in syllabus_body_markers):
        return False
    contents_markers = [
        "contents",
        "specification at a glance",
        "scheme of assessment",
        "general administration",
    ]
    return page <= 3 or sum(marker in text for marker in contents_markers) >= 2


def is_cross_subject_borrowed_practice(question: str, subject_area: str | None) -> bool:
    area = (subject_area or "").lower()
    if any(term in area for term in ["math", "mathematics", "further mathematics"]):
        return False
    question_lower = question.lower()
    borrowed_math_markers = [
        "mean and range",
        "median and range",
        "right-angled triangle",
        "find the hypotenuse",
        "solve 3(",
        "nth term",
        "straight line y =",
        "drink is mixed using juice and water in the ratio",
    ]
    return any(marker in question_lower for marker in borrowed_math_markers)


def mixed_language_label_matches(html: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", html)
    matches: list[str] = []
    for pattern in BILINGUAL_LABEL_PATTERNS:
        if pattern in html:
            matches.append(pattern)
    for match in BILINGUAL_SLASH_PATTERN.finditer(text):
        label = " ".join(match.group(0).split())
        if label not in matches:
            matches.append(label)
    return matches


def expected_topic_marker(topic_title: str, index: int, output_language: str) -> str:
    if output_language == "en":
        return topic_title
    match = re.match(r"^\s*([A-Z]\d+[A-Z]?|\d+(?:\.\d+)+)\b", topic_title)
    if match:
        return f"第 {match.group(1)} 节"
    return localized_topic_marker(topic_title) or f"第 {index} 节"


def localized_topic_marker(topic_title: str) -> str | None:
    text = topic_title.lower()
    keyword_titles = [
        (("measurement", "data", "graph"), "测量与数据"),
        (("force", "motion"), "力与运动"),
        (("particle", "state", "solid", "liquid", "gas"), "粒子模型与物质状态"),
        (("bond", "structure"), "结构与性质"),
        (("acid", "alkali", "ph"), "酸碱与 pH"),
        (("accounting", "ledger", "bookkeeping"), "会计记录"),
        (("financial statement", "profit", "position"), "财务报表"),
        (("ratio", "liquidity", "profitability"), "比率分析"),
        (("demand", "supply", "market"), "市场供需"),
        (("opportunity", "scarcity", "choice"), "选择与机会成本"),
        (("set", "venn"), "集合与韦恩图"),
        (("triangle", "pythagoras", "geometry"), "几何图形"),
        (("statistics", "probability"), "统计与概率"),
    ]
    for keywords, label in keyword_titles:
        if any(keyword in text for keyword in keywords):
            return label
    if re.search(r"[\u4e00-\u9fff]", topic_title):
        return topic_title[:32]
    return None


def issues_to_dict(issues: list[ValidationIssue]) -> list[dict[str, str]]:
    return [asdict(issue) for issue in issues]


def review_summary(
    plan: GuidePlan,
    html_path: Path | None = None,
    pdf_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, object]:
    qualification = plan.qualification
    topic_titles = {topic.title for topic in qualification.topics}
    practice_topics = {item.topic_title for item in plan.practice_items}
    guide_topics = {guide.topic_title for guide in plan.topic_guides}
    topics_with_source = sum(1 for topic in qualification.topics if topic.source_snippets)
    svg_safe_visuals = sum(1 for brief in plan.visual_briefs if brief.complexity == "svg-basic")
    infographic_visuals = sum(1 for brief in plan.visual_briefs if brief.complexity == "infographic")
    html = ""
    if html_path and html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
    section_files = 0
    image_files = 0
    generated_infographic_assets = 0
    svg_fallback_assets = 0
    pending_infographic_assets = 0
    has_visual_manifest = False
    has_package_manifest = False
    if output_dir:
        sections_dir = output_dir / "sections"
        images_dir = output_dir / "images"
        section_files = len(list(sections_dir.glob("*.txt"))) if sections_dir.exists() else 0
        if images_dir.exists():
            image_files = len(
                [
                    path
                    for path in images_dir.iterdir()
                    if path.suffix.lower() == ".svg" or is_raster_asset(path.name)
                ]
            )
            manifest_entries = load_visual_manifest(images_dir)
            generated_infographic_assets = sum(
                1
                for entry in manifest_entries
                if entry.get("complexity") == "infographic"
                and has_renderable_infographic(entry, images_dir)
            )
            svg_fallback_assets = sum(
                1
                for entry in manifest_entries
                if entry.get("complexity") == "infographic"
                and has_renderable_svg_fallback(entry, images_dir)
            )
            pending_infographic_assets = sum(
                1
                for entry in manifest_entries
                if entry.get("complexity") == "infographic"
                and str(entry.get("asset_status", "")).lower() in PENDING_ASSET_STATUSES
            )
        has_visual_manifest = (images_dir / "visual_manifest.json").exists()
        has_package_manifest = (output_dir / "handbook-package.json").exists()
    return {
        "requested_subject": plan.run_options.requested_subject,
        "provider": qualification.provider or qualification.source.provider,
        "source_provider": qualification.source.provider,
        "qualification_family": qualification.qualification_family or qualification.source.qualification_family,
        "specification_sha256": qualification.source.specification_sha256,
        "syllabus_year_range": qualification.source.syllabus_year_range,
        "selected_exam_year": qualification.selected_exam_year or qualification.source.selected_exam_year,
        "image_provider": plan.run_options.image_provider,
        "explanation_style": plan.run_options.explanation_style,
        "output_language": plan.run_options.output_language,
        "topics": len(qualification.topics),
        "assessments": len(qualification.assessments),
        "topic_guides": len(plan.topic_guides),
        "visual_briefs": len(plan.visual_briefs),
        "svg_safe_visuals": svg_safe_visuals,
        "infographic_visuals": infographic_visuals,
        "generated_infographic_assets": generated_infographic_assets,
        "svg_fallback_assets": svg_fallback_assets,
        "pending_infographic_assets": pending_infographic_assets,
        "practice_cards": len(plan.practice_items),
        "topics_with_practice": len(topic_titles & practice_topics),
        "topics_with_guides": len(topic_titles & guide_topics),
        "topics_with_pdf_source_snippets": topics_with_source,
        "topic_diagrams_in_html": html.count('class="topic-diagram"') if html else 0,
        "visual_examples_in_html": html.count('<figure class="visual-example') if html else 0,
        "has_html": bool(html_path and html_path.exists()),
        "has_pdf": bool(pdf_path and pdf_path.exists()),
        "section_files": section_files,
        "image_files": image_files,
        "has_visual_manifest": has_visual_manifest,
        "has_package_manifest": has_package_manifest,
        "has_listing_metadata": bool(
            qualification.source.listing_qualification_type
            or qualification.source.listing_group_label
        ),
        "listing_group_label": qualification.source.listing_group_label,
        "audience_note_mentions_international_students": "international students"
        in qualification.audience_note.lower(),
        "audience_note_mentions_outside_uk": (
            "outside the uk" in qualification.audience_note.lower()
            or "outside the united kingdom" in qualification.audience_note.lower()
        ),
        "qualification_structure": qualification.qualification_type,
    }
