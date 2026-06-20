from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    Qualification,
    SourceRecord,
    Topic,
    TopicGuide,
)
from intl_exam_guide.planning.anti_ai_language import (
    has_ai_language_smell,
    polish_ai_language,
)
from intl_exam_guide.planning.guide_plan import build_guide_plan
from intl_exam_guide.validation.checks import validate_guides


def test_polish_removes_safe_english_transition():
    assert polish_ai_language("In conclusion, the answer is 5.", "en") == "the answer is 5."


def test_detector_keeps_semantic_contrasts_as_warning_only():
    assert has_ai_language_smell(["This is not just a topic but also a tool."], "en")


def test_polish_removes_safe_chinese_transition():
    assert polish_ai_language("总之，机会成本是放弃的次优选择。", "zh-CN") == "机会成本是放弃的次优选择。"


def test_build_guide_plan_applies_polish_to_generated_text():
    qualification = Qualification(
        title="International GCSE Example (9999)",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Example",
        page_url="https://example.test/",
        summary=[],
        topics=[Topic(title="Opportunity cost", points=["scarcity and choice"])],
        assessments=[AssessmentPaper(title="Paper 1")],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/",
            specification_url="https://example.test/spec.pdf",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )

    plan = build_guide_plan(qualification, questions_per_topic=1, output_language="en")

    visible_text = " ".join(
        [
            plan.topic_guides[0].essence,
            plan.topic_guides[0].analogy,
            plan.practice_items[0].question,
            *plan.practice_items[0].public_solution_steps,
        ]
    )
    assert "In conclusion" not in visible_text
    assert "Overall" not in visible_text


def test_validation_warns_about_formulaic_ai_wording():
    plan = GuidePlan(
        qualification=Qualification(
            title="International GCSE Example (9999)",
            code="9999",
            qualification_type="international_gcse",
            subject_area="Example",
            page_url="https://example.test/",
            summary=[],
            topics=[Topic(title="Topic", points=["Point"])],
            assessments=[AssessmentPaper(title="Paper 1")],
            source=SourceRecord(
                provider="test",
                page_url="https://example.test/",
                specification_url="https://example.test/spec.pdf",
            ),
            audience_note="International GCSE linear qualification for international students outside the UK.",
        ),
        run_options=GuideRunOptions(
            requested_subject="Example",
            image_provider="prompt-queue",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[
            TopicGuide(
                topic_title="Topic",
                essence="Overall, this topic helps revision.",
                analogy="Treat it as a tool.",
                mini_worked_example="Use one example.",
                worked_solution_steps=["Step 1", "Step 2", "Step 3", "Step 4"],
                pitfall="Avoid vague answers.",
                checklist=["One", "Two", "Three"],
                diagram_brief="Draw a concept map.",
            )
        ],
        practice_items=[],
        visual_briefs=[],
        diagram_briefs=[],
        revision_stages=[],
    )

    issues = validate_guides(plan)

    assert any(
        issue.severity == "warning" and "formulaic AI-style wording" in issue.message
        for issue in issues
    )
