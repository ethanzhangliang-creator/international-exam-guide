from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from intl_exam_guide.models import GuidePlan


@dataclass
class ValidationIssue:
    severity: str
    message: str


def validate_plan(plan: GuidePlan, html_path: Path | None = None, pdf_path: Path | None = None) -> list[ValidationIssue]:
    qualification = plan.qualification
    issues: list[ValidationIssue] = []

    if not qualification.source.page_url:
        issues.append(ValidationIssue("error", "Missing source qualification page URL."))
    if not qualification.source.specification_url:
        issues.append(ValidationIssue("error", "Missing specification PDF URL."))
    if not qualification.source.specification_sha256:
        issues.append(ValidationIssue("warning", "Specification PDF hash was not recorded."))
    if not qualification.topics:
        issues.append(ValidationIssue("error", "No syllabus topics were extracted."))
    if not qualification.assessments:
        issues.append(ValidationIssue("warning", "No assessment papers were extracted."))
    if len(plan.practice_items) < len(qualification.topics):
        issues.append(ValidationIssue("warning", "Practice coverage is below one item per topic."))
    if len(plan.topic_guides) != len(qualification.topics):
        issues.append(ValidationIssue("error", "Topic guide coverage does not match topic count."))

    guide_topics = {guide.topic_title for guide in plan.topic_guides}
    practice_topics = {item.topic_title for item in plan.practice_items}
    for topic in qualification.topics:
        if topic.title not in guide_topics:
            issues.append(ValidationIssue("error", f"Missing authored guide block for topic: {topic.title}"))
        if topic.title not in practice_topics:
            issues.append(ValidationIssue("error", f"Missing practice item for topic: {topic.title}"))
        if not topic.source_snippets:
            issues.append(ValidationIssue("warning", f"No PDF source snippet matched for topic: {topic.title}"))

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
            issues.append(ValidationIssue("warning", f"Worked example has fewer than 4 public steps: {guide.topic_title}"))
        if len(guide.checklist) < 3:
            issues.append(ValidationIssue("warning", f"Checklist is too short: {guide.topic_title}"))

    for item in plan.practice_items:
        if not item.command_word.strip():
            issues.append(ValidationIssue("error", f"Practice item is missing a command word: {item.topic_title}"))
        if not item.difficulty.strip():
            issues.append(ValidationIssue("error", f"Practice item is missing a difficulty: {item.topic_title}"))
        if not item.focus_point.strip():
            issues.append(ValidationIssue("error", f"Practice item is missing a focus point: {item.topic_title}"))
        if len(item.public_solution_steps) < 4:
            issues.append(ValidationIssue("error", f"Practice item has too few solution steps: {item.topic_title}"))
        if len(item.answer_checkpoints) < 3:
            issues.append(ValidationIssue("error", f"Practice item has too few answer checkpoints: {item.topic_title}"))
        if not item.source_points:
            issues.append(ValidationIssue("error", f"Practice item has no source points: {item.topic_title}"))

    if qualification.qualification_type == "international_gcse":
        if qualification.source.listing_qualification_type and qualification.source.listing_qualification_type != "international_gcse":
            issues.append(ValidationIssue("error", "Source listing metadata conflicts with International GCSE type."))
        if "international students" not in qualification.audience_note.lower():
            issues.append(ValidationIssue("warning", "GCSE audience note does not explicitly mention international students."))
        if "outside the uk" not in qualification.audience_note.lower() and "outside the united kingdom" not in qualification.audience_note.lower():
            issues.append(ValidationIssue("warning", "GCSE audience note does not explain that the course is for use outside the UK."))
        if "linear" not in " ".join([qualification.audience_note, *qualification.summary]).lower():
            issues.append(ValidationIssue("warning", "GCSE guide does not mention the linear qualification structure."))
    if qualification.qualification_type == "international_as_a_level":
        if qualification.source.listing_qualification_type and qualification.source.listing_qualification_type != "international_as_a_level":
            issues.append(ValidationIssue("error", "Source listing metadata conflicts with AS/A-level type."))
        if "modular" not in " ".join([qualification.audience_note, *qualification.summary]).lower():
            issues.append(ValidationIssue("warning", "AS/A-level guide does not mention the modular qualification structure."))

    if html_path:
        if not html_path.exists():
            issues.append(ValidationIssue("error", f"HTML output is missing: {html_path}"))
        else:
            html = html_path.read_text(encoding="utf-8", errors="replace")
            for topic in qualification.topics:
                if topic.title not in html:
                    issues.append(ValidationIssue("error", f"Topic missing from HTML: {topic.title}"))
            required_phrases = [
                "一句话本质",
                "Mini Worked Example",
                "practice card",
                "Public solution steps",
                "Answer checkpoints",
                "考试陷阱",
                "Source check",
                "Concept map / 图文解释",
                "图文解释规划",
                "Language Policy",
            ]
            for phrase in required_phrases:
                if phrase not in html:
                    issues.append(ValidationIssue("error", f"HTML missing required section phrase: {phrase}"))
            diagram_count = html.count('class="topic-diagram"')
            if diagram_count < len(qualification.topics):
                issues.append(
                    ValidationIssue(
                        "error",
                        f"HTML has {diagram_count} topic diagrams for {len(qualification.topics)} topics.",
                    )
                )

    if pdf_path and not pdf_path.exists():
        issues.append(ValidationIssue("warning", f"PDF output is missing: {pdf_path}"))

    return issues


def issues_to_dict(issues: list[ValidationIssue]) -> list[dict[str, str]]:
    return [asdict(issue) for issue in issues]


def review_summary(
    plan: GuidePlan,
    html_path: Path | None = None,
    pdf_path: Path | None = None,
) -> dict[str, object]:
    qualification = plan.qualification
    topic_titles = {topic.title for topic in qualification.topics}
    practice_topics = {item.topic_title for item in plan.practice_items}
    guide_topics = {guide.topic_title for guide in plan.topic_guides}
    topics_with_source = sum(1 for topic in qualification.topics if topic.source_snippets)
    html = ""
    if html_path and html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
    return {
        "topics": len(qualification.topics),
        "assessments": len(qualification.assessments),
        "topic_guides": len(plan.topic_guides),
        "practice_cards": len(plan.practice_items),
        "topics_with_practice": len(topic_titles & practice_topics),
        "topics_with_guides": len(topic_titles & guide_topics),
        "topics_with_pdf_source_snippets": topics_with_source,
        "topic_diagrams_in_html": html.count('class="topic-diagram"') if html else 0,
        "has_html": bool(html_path and html_path.exists()),
        "has_pdf": bool(pdf_path and pdf_path.exists()),
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
