from __future__ import annotations

import os

from intl_exam_guide.models import (
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.planning.anti_ai_language import polish_ai_language, polish_texts
from intl_exam_guide.planning.explanation_styles import (
    styled_explanation,
    styled_explanation_en,
)
from intl_exam_guide.planning.localization import (
    zh_point_label,
    zh_point_labels,
    zh_topic_reference,
    zh_visual_trigger,
    zh_visual_type,
)
from intl_exam_guide.planning.practice_generator import (
    build_practice_item,
    choose_command_word,
    choose_difficulty,
    concrete_example,
    concrete_example_zh,
)
from intl_exam_guide.planning.visual_routing import (
    build_visual_brief,
    choose_provider_for_visual,
    choose_visual_type,
)


STYLE_LABELS = {
    "formal": "formal exam-focused",
    "friendly": "friendly",
    "life": "real-life context",
    "story": "story-driven",
    "detective": "detective reasoning",
    "adventure": "original adventure mode",
}

IMAGE_PROVIDERS = {
    "prompt-queue",
    "deterministic-svg",
    "custom",
}
RECOMMENDED_IMAGE_MODEL_LABELS = {
    "gpt-image-2",
    "qwen-image-pro",
    "sensenova-u1-fast",
}

LANGUAGE_CHOICES = {"en", "zh-CN"}


__all__ = [
    "STYLE_LABELS",
    "IMAGE_PROVIDERS",
    "RECOMMENDED_IMAGE_MODEL_LABELS",
    "LANGUAGE_CHOICES",
    "build_guide_plan",
    "build_run_options",
    "normalize_image_provider",
    "build_topic_guide",
    "build_checklist",
    "build_revision_stages",
    "zh_point_label",
    "zh_point_labels",
    "zh_topic_reference",
    "zh_visual_trigger",
    "zh_visual_type",
    "build_practice_item",
    "choose_command_word",
    "choose_difficulty",
    "concrete_example",
    "concrete_example_zh",
    "build_visual_brief",
    "choose_provider_for_visual",
    "choose_visual_type",
    "styled_explanation",
    "styled_explanation_en",
]


def build_guide_plan(
    qualification: Qualification,
    questions_per_topic: int = 2,
    image_provider: str | None = None,
    explanation_style: str = "friendly",
    output_language: str = "en",
    requested_subject: str | None = None,
    exam_year: str | None = None,
    image_model: str | None = None,
    image_endpoint_url: str | None = None,
    image_api_key_env: str | None = None,
) -> GuidePlan:
    run_options = build_run_options(
        qualification=qualification,
        requested_subject=requested_subject,
        image_provider=image_provider,
        explanation_style=explanation_style,
        output_language=output_language,
        exam_year=exam_year,
        image_model=image_model,
        image_endpoint_url=image_endpoint_url,
        image_api_key_env=image_api_key_env,
    )
    topic_guides: list[TopicGuide] = []
    practice_items: list[PracticeItem] = []
    visual_briefs: list[VisualBrief] = []
    diagram_briefs: list[str] = []

    for topic in qualification.topics:
        points = topic.points[:4]
        if not points:
            points = [topic.title]
        guide = build_topic_guide(
            topic,
            qualification.qualification_type,
            run_options.explanation_style,
            run_options.output_language,
        )
        topic_guides.append(guide)
        visual = build_visual_brief(topic, guide, run_options, qualification.subject_area)
        if visual:
            visual_briefs.append(visual)
        diagram_briefs.append(guide.diagram_brief)
        for number in range(questions_per_topic):
            practice_items.append(
                build_practice_item(
                    topic,
                    points,
                    number,
                    qualification.qualification_type,
                    run_options.explanation_style,
                    run_options.output_language,
                    qualification.subject_area,
                )
            )

    revision_stages = build_revision_stages(
        qualification.qualification_type,
        run_options.output_language,
    )
    return GuidePlan(
        qualification=qualification,
        run_options=run_options,
        topic_guides=topic_guides,
        practice_items=practice_items,
        visual_briefs=visual_briefs,
        diagram_briefs=diagram_briefs,
        revision_stages=revision_stages,
    )

def build_run_options(
    qualification: Qualification,
    requested_subject: str | None,
    image_provider: str | None,
    explanation_style: str,
    output_language: str,
    exam_year: str | None,
    image_model: str | None,
    image_endpoint_url: str | None,
    image_api_key_env: str | None,
) -> GuideRunOptions:
    provider = normalize_image_provider(image_provider, image_model, image_endpoint_url, image_api_key_env)
    style = explanation_style if explanation_style in STYLE_LABELS else "friendly"
    language = output_language if output_language in LANGUAGE_CHOICES else "en"
    return GuideRunOptions(
        requested_subject=requested_subject or qualification.title,
        image_provider=provider,
        explanation_style=style,
        output_language=language,
        exam_year=exam_year or qualification.selected_exam_year,
        image_model=image_model,
        image_endpoint_url=image_endpoint_url,
        image_api_key_env=image_api_key_env,
    )

def normalize_image_provider(
    image_provider: str | None,
    image_model: str | None,
    image_endpoint_url: str | None,
    image_api_key_env: str | None,
) -> str:
    provider = (image_provider or "prompt-queue").strip()
    if provider in RECOMMENDED_IMAGE_MODEL_LABELS:
        # Recommended model names are not proof of a callable provider. Keep the
        # base handbook honest and queue complex visuals for external generation.
        return "prompt-queue"
    if provider == "custom":
        if (
            image_model
            and image_endpoint_url
            and image_api_key_env
            and os.environ.get(image_api_key_env)
        ):
            return "custom"
        return "prompt-queue"
    if provider in IMAGE_PROVIDERS:
        return provider
    return "prompt-queue"

def build_topic_guide(
    topic: Topic,
    qualification_type: str,
    explanation_style: str,
    output_language: str,
) -> TopicGuide:
    points = topic.points[:5] or [topic.title]
    visible_points = points if output_language == "en" else zh_point_labels(points)
    primary = visible_points[0]
    if output_language == "en":
        level_hint = "AS-A-level unit" if qualification_type == "international_as_a_level" else "GCSE topic"
    else:
        level_hint = "AS-A-level 单元" if qualification_type == "international_as_a_level" else "GCSE 知识点"
    essence, analogy, mini_worked_example, pitfall = styled_explanation(
        topic=topic,
        primary=primary,
        level_hint=level_hint,
        explanation_style=explanation_style,
        output_language=output_language,
    )
    essence, analogy, mini_worked_example, pitfall = polish_texts(
        [essence, analogy, mini_worked_example, pitfall],
        output_language,
    )
    worked_solution_steps = (
        [
            "Read the command word and circle the data or conditions in the question.",
            f"Match the question to this syllabus point: {points[0]}.",
            "Write the formula, definition, diagram relationship, or judgement rule you need.",
            "Check the unit, precision, symbols, and final sentence against the question.",
        ]
        if output_language == "en"
        else [
            "读题：圈出指令词和题目给出的数据/条件。",
            f"定位：把题目匹配到{primary}。",
            "作答：写出公式、定义、图形关系或判断过程。",
            "检查：单位、精度、符号和最终句子是否回答了题问。",
        ]
    )
    checklist = build_checklist(visible_points, output_language)
    diagram_brief = (
        (
            f"Draw a clean concept map for '{topic.title}' with the central title in the middle, "
            f"branches for {', '.join(points[:4])}, and one short exam-action label on each branch."
        )
        if output_language == "en"
        else (
            f"为“{zh_topic_reference(topic)}”绘制清晰概念图：中心放主题，分支覆盖 "
            f"{'、'.join(visible_points[:4])}，每个分支加一个简短做题动作标签。"
        )
    )
    return TopicGuide(
        topic_title=topic.title,
        essence=essence,
        analogy=analogy,
        mini_worked_example=mini_worked_example,
        worked_solution_steps=polish_texts(worked_solution_steps, output_language),
        pitfall=pitfall,
        checklist=polish_texts(checklist, output_language),
        diagram_brief=polish_ai_language(diagram_brief, output_language),
        source_snippets=topic.source_snippets[:3],
    )

def build_checklist(points: list[str], output_language: str) -> list[str]:
    if output_language == "en":
        return [
            *[f"Can explain: {point}" for point in points[:4]],
            "Can answer at least one original exam-style prompt without looking at notes.",
            "Can name one common mistake and how to avoid it.",
        ]
    return [
        *[f"能解释：{point}" for point in points[:4]],
        "不看笔记也能完成至少一道原创考试风格练习。",
        "能说出一个常见错误，并知道如何避开。",
    ]

def build_revision_stages(qualification_type: str, output_language: str = "en") -> list[str]:
    if output_language == "zh-CN":
        if qualification_type == "international_as_a_level":
            return [
                "第 1 阶段 - 单元地图：先分清 AS、A2 或模块单元，再做综合题。",
                "第 2 阶段 - 建构：把每个单元点整理成短讲解、一道应用题和一个易错点。",
                "第 3 阶段 - 测试：先按单元练，再把不同单元放在一起做综合练习。",
            ]
        return [
            "第 1 阶段 - 线性地图：先看完整门课的主题结构，再进入混合题。",
            "第 2 阶段 - 建构：把每个大纲点整理成一页笔记、一道例题和一个易错点。",
            "第 3 阶段 - 测试：练习整卷混合题，复盘错题，并每周更新检查清单。",
        ]
    if qualification_type == "international_as_a_level":
        return [
            "Stage 1 - Unit map: separate AS and A2 or modular units before mixing questions.",
            "Stage 2 - Build: turn each unit point into a short explanation, one application prompt, and one pitfall.",
            "Stage 3 - Test: practise by unit first, then combine units in mixed questions.",
        ]
    return [
        "Stage 1 - Linear map: learn the full-course topic structure before doing mixed papers.",
        "Stage 2 - Build: turn each syllabus point into a one-page note, one worked example, and one pitfall.",
        "Stage 3 - Test: practise mixed end-of-course questions, review errors, and update the checklist weekly.",
    ]
