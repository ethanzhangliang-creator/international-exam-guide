from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from intl_exam_guide.models import (
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.rendering.cover import render_cover
from intl_exam_guide.rendering.icons import render_icon
from intl_exam_guide.rendering.infographics import render_infographic_required
from intl_exam_guide.rendering.styles import stylesheet
from intl_exam_guide.rendering.story_modes import chinese_story_lines, english_story_lines
from intl_exam_guide.rendering.svg_templates import render_topic_visual_svg
from intl_exam_guide.rendering.text import html_escape, subject_display_name
from intl_exam_guide.rendering.visual_assets import (
    build_visual_asset_lookup,
    load_visual_manifest,
    visual_asset_key_from_brief,
)


def render_html(
    plan: GuidePlan,
    output_path: Path,
    visual_manifest_path: Path | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qualification = plan.qualification
    language = plan.run_options.output_language
    manifest_path = visual_manifest_path or output_path.parent / "images" / "visual_manifest.json"
    visual_assets = build_visual_asset_lookup(load_visual_manifest(manifest_path))
    html_lang = "zh-CN" if language == "zh-CN" else "en"
    page_title = (
        f"{qualification.title} Revision Guide"
        if language == "en"
        else f"{subject_display_name(qualification)}学习复习手册"
    )
    parts = [
        f"<!doctype html><html lang=\"{html_lang}\"><head><meta charset=\"utf-8\">",
        f"<title>{html_escape(page_title)}</title>",
        f"<style>{stylesheet()}</style></head><body>",
        render_cover(qualification, plan.run_options),
        render_student_overview(qualification, plan.revision_stages, plan.run_options),
        render_topic_map(qualification.topics, language, plan.topic_guides),
        render_topic_nav(qualification.topics, language),
        render_topics(
            qualification.topics,
            plan.topic_guides,
            plan.practice_items,
            plan.visual_briefs,
            visual_assets,
            language,
        ),
        render_reference_appendix(qualification, len(plan.practice_items), language),
        "</body></html>",
    ]
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def render_student_overview(
    qualification: Qualification,
    stages: list[str],
    options: GuideRunOptions,
) -> str:
    summary = "".join(f"<li>{html_escape(item)}</li>" for item in qualification.summary[:4])
    if options.output_language == "zh-CN":
        summary = "".join(
            f"<li>{html_escape(item)}</li>"
            for item in [
                "本手册根据官方课程页面和考试大纲 PDF 整理。",
                "知识单元按大纲抽取结果展开，便于逐节复习。",
                "官方英文来源保留在结构化文件中，正文按中文学习手册排版。",
            ]
        )
    stage_items = "".join(f"<li>{html_escape(stage)}</li>" for stage in stages)
    if options.output_language == "en":
        return f"""
<section class="band student-overview">
  <h2>How to Study</h2>
  <div class="overview-grid">
    <article>
      <h3>Study Order</h3>
      <ol>{stage_items}</ol>
    </article>
    <article>
      <h3>Course Focus</h3>
      <ul>{summary}</ul>
    </article>
    <article>
      <h3>Guide Setup</h3>
      <ul>
        <li>Subject request: {html_escape(options.requested_subject)}</li>
        <li>Output language: English</li>
        <li>Illustrations: {html_escape(image_provider_display(options, options.output_language))}</li>
        <li>Writing style: {html_escape(style_display(options.explanation_style, options.output_language))}</li>
      </ul>
    </article>
  </div>
</section>
"""
    subject_request = subject_display_name(qualification)
    if subject_request == "本课程":
        subject_request = re.sub(r"\s*\([^)]*\)\s*$", "", qualification.title).strip()
        for prefix in ("International GCSE", "International AS-A-level"):
            if subject_request.lower().startswith(prefix.lower()):
                subject_request = subject_request[len(prefix) :].strip(" -–—:")
                break
    return f"""
<section class="band student-overview">
  <h2>怎么用这本手册</h2>
  <div class="overview-grid">
    <article>
      <h3>学习顺序</h3>
      <ol>{stage_items}</ol>
    </article>
    <article>
      <h3>课程重点</h3>
      <ul>{summary}</ul>
    </article>
    <article>
      <h3>手册设置</h3>
      <ul>
        <li>科目：{html_escape(subject_request)}</li>
        <li>输出语言：中文</li>
        <li>插图说明：{html_escape(image_provider_display(options, options.output_language))}</li>
        <li>讲解语气：{html_escape(style_display(options.explanation_style, options.output_language))}</li>
      </ul>
    </article>
  </div>
</section>
"""


def style_display(style: str, language: str = "en") -> str:
    labels = (
        {
            "formal": "Formal",
            "friendly": "Friendly",
            "life": "Life Scene",
            "story": "Story",
            "detective": "Detective",
            "adventure": "Adventure",
        }
        if language == "en"
        else {
            "formal": "正经严谨",
            "friendly": "轻松愉快",
            "life": "生活场景",
            "story": "故事性强",
            "detective": "侦探推理",
            "adventure": "原创闯关",
        }
    )
    return labels.get(style, style)


def image_provider_display(options: GuideRunOptions, language: str = "en") -> str:
    if options.image_provider == "custom":
        model = options.image_model or ("custom model" if language == "en" else "自定义模型")
        return f"custom illustration model: {model}" if language == "en" else f"自定义插图模型：{model}"
    if options.image_provider == "prompt-queue":
        return (
            "infographic prompts prepared; final illustrations still need review"
            if language == "en"
            else "已整理复杂信息图提示词，插图需要生成或复核后使用"
        )
    if options.image_provider == "deterministic-svg":
        return (
            "simple diagrams are included; complex infographics need generation or review"
            if language == "en"
            else "简单示意图已随手册生成，复杂信息图需要生成或复核后使用"
        )
    return options.image_provider


def render_source_note(qualification: Qualification, language: str = "en") -> str:
    listing_note = render_listing_note(qualification, language)
    heading = "Audience and Sources" if language == "en" else "适用对象与来源"
    page_label = "Qualification page" if language == "en" else "课程页面"
    spec_label = "Specification PDF" if language == "en" else "考试大纲 PDF"
    hash_value = qualification.source.specification_sha256 or ("not downloaded" if language == "en" else "未下载")
    audience_note = (
        qualification.audience_note
        if language == "en"
        else "本手册面向学习该国际课程的学生；官方英文说明保留在结构化来源文件中供复核。"
    )
    return f"""
<section class="band source">
  <h2>{html_escape(heading)}</h2>
  <p>{html_escape(audience_note)}</p>
  {listing_note}
  <ul>
    <li>{html_escape(page_label)}: <a href="{html_escape(qualification.page_url)}">{html_escape(qualification.page_url)}</a></li>
    <li>{html_escape(spec_label)}: {link_or_missing(qualification.source.specification_url, language)}</li>
    <li>PDF SHA-256: <code>{html_escape(hash_value)}</code></li>
  </ul>
</section>
"""


def render_language_policy() -> str:
    return """
<section class="band language-policy">
  <h2>Language Policy</h2>
  <ul class="plain">
    <li>The student-facing handbook follows one selected output language.</li>
    <li>Template labels, explanations, worked examples, and image prompts are not rendered as bilingual pairs.</li>
    <li>Official source text remains available for traceability in structured files or a separated review appendix.</li>
  </ul>
</section>
"""


def render_listing_note(qualification: Qualification, language: str = "en") -> str:
    source = qualification.source
    if not source.listing_group_label and not source.listing_subject:
        return ""
    pieces = []
    if source.listing_subject:
        label = "Subject group" if language == "en" else "科目组"
        pieces.append(f"{label}: {html_escape(source.listing_subject)}")
    if source.listing_group_label:
        label = "Website group" if language == "en" else "官网分组"
        pieces.append(f"{label}: {html_escape(source.listing_group_label)}")
    if source.listing_style_class:
        label = "Detected class" if language == "en" else "识别类型"
        pieces.append(f"{label}: {html_escape(source.listing_style_class)}")
    return f"<p class=\"listing-note\">{' · '.join(pieces)}</p>"


def render_summary(qualification: Qualification, language: str = "en") -> str:
    if language == "en":
        summary_items = qualification.summary[:5]
    else:
        summary_items = [
            "课程定位来自官方课程页面和考试大纲。",
            "详细学习内容按 PDF 大纲抽取结果整理。",
            "英文来源保留在结构化文件中，学生正文保持中文。",
        ]
    items = "\n".join(f"<li>{html_escape(item)}</li>" for item in summary_items)
    heading = "Course Position" if language == "en" else "课程定位"
    return f"""
<section class="band">
  <h2>{html_escape(heading)}</h2>
  <ul class="plain">{items}</ul>
</section>
"""


def render_assessments(qualification: Qualification, language: str = "en") -> str:
    cards = []
    for index, paper in enumerate(qualification.assessments, start=1):
        if language == "en":
            title = paper.title
            detail_items = paper.details[:8]
        else:
            title = f"试卷 {index}"
            detail_items = [
                "考试时长、分值和占比以官方大纲为准。",
                "结构化输出中保留官方英文考试信息，便于老师或维护者复核。",
            ]
        details = "".join(f"<li>{html_escape(item)}</li>" for item in detail_items)
        cards.append(f"<article class=\"assessment\"><h3>{html_escape(title)}</h3><ul>{details}</ul></article>")
    if cards:
        body = "\n".join(cards)
    else:
        body = (
            "<p class=\"warning\">No assessment structure was extracted. Review the source page manually.</p>"
            if language == "en"
            else "<p class=\"warning\">没有抽取到考试结构，需要人工复核来源页面。</p>"
        )
    heading = "Assessment Structure" if language == "en" else "考试结构"
    return f"<section class=\"band\"><h2>{html_escape(heading)}</h2><div class=\"assessment-grid\">{body}</div></section>"


def render_topic_map(
    topics: list[Topic],
    language: str,
    topic_guides: list[TopicGuide] | None = None,
) -> str:
    rows = []
    guides = {guide.topic_title: guide for guide in topic_guides or []}
    for index, topic in enumerate(topics, start=1):
        guide = guides.get(topic.title)
        if language == "en":
            points = (
                ", ".join(topic.points[:4])
                if topic.points
                else "Use the specification text for detailed statements."
            )
            title = topic.title
        else:
            title = display_topic_title(topic, index, language)
            if guide:
                points = "；".join(guide.checklist[:3])
            else:
                points = "使用考试大纲抽取结果补全本节细分要求。"
        title_link = f'<a href="#{topic_anchor(index)}">{html_escape(title)}</a>'
        rows.append(
            "<tr>"
            f"<td>{index}</td><td>{title_link}</td><td>{html_escape(points)}</td>"
            "</tr>"
        )
    if language == "en":
        heading = "Study Roadmap"
        columns = "<tr><th>#</th><th>Knowledge unit</th><th>What to master</th></tr>"
    else:
        heading = "复习路线"
        columns = "<tr><th>#</th><th>知识单元</th><th>要掌握什么</th></tr>"
    return f"""
<section class="band">
  <h2>{heading}</h2>
  <table><thead>{columns}</thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>
"""


def render_topic_nav(topics: list[Topic], language: str) -> str:
    heading = "Quick Navigation" if language == "en" else "快速目录"
    links = []
    for index, topic in enumerate(topics, start=1):
        title = display_topic_title(topic, index, language)
        links.append(
            f'<a href="#{topic_anchor(index)}"><span>T{index}</span>{html_escape(title)}</a>'
        )
    return f"""
<nav class="band topic-nav" aria-label="{html_escape(heading)}">
  <h2>{html_escape(heading)}</h2>
  <div class="topic-nav-grid">{''.join(links)}</div>
</nav>
"""


def topic_anchor(index: int) -> str:
    return f"topic-{index}"


def render_revision_stages(stages: list[str], language: str = "en") -> str:
    items = "".join(f"<li>{html_escape(stage)}</li>" for stage in stages)
    heading = "Three-Stage Revision" if language == "en" else "三阶段复习法"
    return f"<section class=\"band\"><h2>{html_escape(heading)}</h2><ol class=\"stage-list\">{items}</ol></section>"


def render_topics(
    topics: list[Topic],
    topic_guides: list[TopicGuide],
    practice_items: list[PracticeItem],
    visual_briefs: list[VisualBrief],
    visual_assets: dict[str, dict[str, Any]] | None = None,
    language: str = "en",
) -> str:
    grouped: dict[str, list[PracticeItem]] = {}
    for item in practice_items:
        grouped.setdefault(item.topic_title, []).append(item)
    guides = {guide.topic_title: guide for guide in topic_guides}
    visuals = {brief.topic_title: brief for brief in visual_briefs}

    sections = []
    for index, topic in enumerate(topics, start=1):
        guide = guides.get(topic.title)
        title = display_topic_title(topic, index, language)
        if language == "en":
            point_values = topic.points
        elif guide:
            point_values = guide.checklist[:4]
        else:
            point_values = ["根据官方大纲抽取结果复习本节内容。"]
        points = "".join(f"<li>{html_escape(point)}</li>" for point in point_values)
        if not points:
            points = (
                "<li>Use the official specification text to expand this topic into teachable sub-points.</li>"
                if language == "en"
                else "<li>根据官方大纲抽取结果复习本节内容。</li>"
            )
        examples = "\n".join(
            render_practice(item, language, title)
            for item in grouped.get(topic.title, [])[:2]
        )
        guide_block = render_topic_guide(guide, language) if guide else ""
        diagram_block = render_topic_diagram(topic, guide, index, language) if guide else ""
        visual = visuals.get(topic.title)
        visual_block = (
            render_visual_example(topic, guide, visual, index, visual_assets, language)
            if guide and visual
            else ""
        )
        source_block = render_source_snippets(topic.source_snippets, language=language)
        key_heading = "Key Ideas" if language == "en" else "本节要掌握"
        logic_heading = "Exam Logic" if language == "en" else "做题逻辑"
        logic_goal = (
            "Goal: identify what this unit is testing, then turn the syllabus point into a calculation, explanation, or judgement step."
            if language == "en"
            else "一句话目标：先判断本节在考什么，再把知识点变成可计算、可解释或可判断的步骤。"
        )
        logic_pitfall = (
            "Common mark loss: memorising key terms without answering the command word, or giving a conclusion without using the question evidence."
            if language == "en"
            else "常见失分点：只背关键词，不回应指令词；只写结论，不把题干信息用进去。"
        )
        sections.append(
            f"""
<section class="topic" id="{topic_anchor(index)}">
  <h2>T{index}. {html_escape(title)}</h2>
  <div class="topic-grid">
    <div>
      <h3>{html_escape(key_heading)}</h3>
      <ul>{points}</ul>
    </div>
    <div class="logic-card">
      <h3>{html_escape(logic_heading)}</h3>
      <p>{html_escape(logic_goal)}</p>
      <p>{html_escape(logic_pitfall)}</p>
    </div>
  </div>
  {guide_block}
  {diagram_block}
  {visual_block}
  {render_story_modes(topic, guide, language, index) if guide else ""}
  {source_block}
  <div class="practice-block">{examples}</div>
</section>
"""
        )
    return "\n".join(sections)


def render_topic_guide(guide: TopicGuide, language: str) -> str:
    steps = "".join(f"<li>{html_escape(step)}</li>" for step in guide.worked_solution_steps)
    checklist = "".join(f"<li>{html_escape(item)}</li>" for item in guide.checklist)
    labels = (
        {
            "essence": "One-Sentence Essence",
            "analogy": "Everyday Analogy",
            "worked": "Method",
            "pitfall": "Exam Pitfall",
        }
        if language == "en"
        else {
            "essence": "一句话本质",
            "analogy": "生活化类比",
            "worked": "解题套路",
            "pitfall": "考试陷阱",
        }
    )
    return f"""
<div class="guide-grid">
  <article class="essence"><h3>{render_icon("target")}<span>{labels["essence"]}</span></h3><p>{html_escape(guide.essence)}</p></article>
  <article class="analogy"><h3>{render_icon("bridge")}<span>{labels["analogy"]}</span></h3><p>{html_escape(guide.analogy)}</p></article>
  <article class="worked"><h3>{render_icon("steps")}<span>{labels["worked"]}</span></h3><p>{html_escape(guide.mini_worked_example)}</p><ol>{steps}</ol></article>
  <article class="pitfall"><h3>{render_icon("alert")}<span>{labels["pitfall"]}</span></h3><p>{html_escape(guide.pitfall)}</p><ul>{checklist}</ul></article>
</div>
"""


def render_topic_diagram(topic: Topic, guide: TopicGuide, index: int, language: str) -> str:
    points = topic.points[:4] if language == "en" else guide.checklist[:4]
    points = points or guide.checklist[:4] or [display_topic_title(topic, index, language)]
    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = format_source_reference(source, language, include_prefix=True)
    caption = "Concept Map" if language == "en" else "图文解释"
    action = "learn -> apply -> check" if language == "en" else "学习 -> 应用 -> 检查"
    topic_label = "TOPIC" if language == "en" else "主题"
    title = display_topic_title(topic, index, language)
    cards = []
    for number, point in enumerate(points[:4], start=1):
        cards.append(
            "<li>"
            f"<span>{number}</span>"
            f"<strong>{html_escape(point)}</strong>"
            f"<em>{html_escape(action)}</em>"
            "</li>"
        )
    return f"""
<figure class="topic-diagram" aria-label="Concept map for {html_escape(title)}">
  <figcaption>{html_escape(caption)}</figcaption>
  <div class="concept-html-map">
    <div class="concept-core">
      <span>{html_escape(topic_label)} {index}</span>
      <strong>{html_escape(title)}</strong>
      <small>{html_escape(source_label)}</small>
    </div>
    <ol>{''.join(cards)}</ol>
  </div>
</figure>
"""


def render_visual_example(
    topic: Topic,
    guide: TopicGuide,
    visual: VisualBrief,
    index: int,
    visual_assets: dict[str, dict[str, Any]] | None = None,
    language: str = "en",
) -> str:
    title = display_topic_title(topic, index, language)
    if visual.complexity == "infographic":
        asset = (visual_assets or {}).get(visual_asset_key_from_brief(visual))
        source = topic.source_snippets[0] if topic.source_snippets else None
        source_label = format_source_reference(source, language)
        return render_infographic_required(title, visual, asset, source_label, language)

    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = format_source_reference(source, language)
    model_note = (
        (
            "Local SVG draft"
            if language == "en"
            else "本地矢量图草图"
        )
        if visual.image_provider == "deterministic-svg"
        else (
            f"Image model slot: {visual.image_provider}"
            if language == "en"
            else f"生图模型：{visual.image_provider}"
        )
    )
    caption = "Visual Worked Example" if language == "en" else "图形例题"
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    question = (
        "Use the diagram to explain or apply:"
        if language == "en"
        else "用这张图解释或应用："
    )
    visual_steps = (
        [
            "Label the visual feature that matches the syllabus point.",
            "Connect the label to one precise syllabus term.",
            "Finish with a sentence that answers the command word.",
        ]
        if language == "en"
        else [
            "标出图中对应大纲点的视觉特征。",
            "把标签连接到一个准确的大纲术语。",
            "用一句回应指令词的话收尾。",
        ]
    )
    step_items = "".join(f"<li>{html_escape(step)}</li>" for step in visual_steps)
    return f"""
<figure class="visual-example" aria-label="Visual worked example for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="visual-grid">
    {render_topic_visual_svg(visual, index, language)}
    <div class="visual-notes">
      <div class="visual-model">{html_escape(model_note)}</div>
      <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
      <p class="visual-question">{html_escape(question)} <strong>{html_escape(visual.focus_point)}</strong>.</p>
      <ol>{step_items}</ol>
    </div>
  </div>
</figure>
"""



def render_story_modes(topic: Topic, guide: TopicGuide, language: str, index: int) -> str:
    focus = topic.points[0] if topic.points else guide.topic_title
    if language == "en":
        life, detective, quest = english_story_lines(topic.title, focus, index)
        return f"""
<div class="story-modes" aria-label="Narrative explanation styles for {html_escape(topic.title)}">
  <article>
    <h3>{render_icon("life")}<span>Life Scene</span></h3>
    <p>{life}</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>Detective Mode</span></h3>
    <p>{detective}</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>Adventure Mode</span></h3>
    <p>{quest}</p>
  </article>
</div>
"""
    title = display_topic_title(topic, index, language)
    focus = guide.checklist[0] if guide.checklist else "本节核心要求"
    life, detective, quest = chinese_story_lines(title, focus, index)
    return f"""
<div class="story-modes" aria-label="叙事化讲解风格：{html_escape(title)}">
  <article>
    <h3>{render_icon("life")}<span>生活场景</span></h3>
    <p>{life}</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>侦探推理</span></h3>
    <p>{detective}</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>闯关感讲解</span></h3>
    <p>{quest}</p>
  </article>
</div>
"""


def render_practice(item: PracticeItem, language: str, display_title: str | None = None) -> str:
    frame = "".join(f"<li>{html_escape(step)}</li>" for step in item.answer_frame)
    solution = "".join(f"<li>{html_escape(step)}</li>" for step in item.public_solution_steps)
    checkpoints = "".join(f"<li>{html_escape(point)}</li>" for point in item.answer_checkpoints)
    source = render_source_snippets(item.source_snippets, compact=True, language=language)
    labels = (
        {
            "worked": "Worked Example",
            "command": "Command",
            "difficulty": "Difficulty",
            "focus": "Focus",
            "try": "Try First",
            "solution": "Solution",
            "check": "Check",
        }
        if language == "en"
        else {
            "worked": "例题",
            "command": "指令词",
            "difficulty": "难度",
            "focus": "聚焦",
            "try": "先自己想",
            "solution": "解题步骤",
            "check": "检查答案",
        }
    )
    title = item.topic_title if language == "en" else (display_title or "本节内容")
    return f"""
<article class="practice">
  <h3>{render_icon("practice")}<span>{html_escape(title)} - {labels["worked"]}</span></h3>
  <div class="practice-meta">
    <span>{render_icon("command")}{labels["command"]}: {html_escape(item.command_word)}</span>
    <span>{render_icon("level")}{labels["difficulty"]}: {html_escape(item.difficulty)}</span>
    <span>{render_icon("focus")}{labels["focus"]}: {html_escape(item.focus_point)}</span>
  </div>
  <p class="practice-question">{html_escape(item.question)}</p>
  <h4>{render_icon("frame")}{labels["try"]}</h4>
  <ol>{frame}</ol>
  <h4>{render_icon("steps")}{labels["solution"]}</h4>
  <ol>{solution}</ol>
  <h4>{render_icon("check")}{labels["check"]}</h4>
  <ul>{checkpoints}</ul>
  {source}
</article>
"""


def render_reference_appendix(qualification: Qualification, practice_count: int, language: str) -> str:
    listing_note = render_listing_note(qualification, language)
    assessment = render_assessments(qualification, language)
    heading = "Source Appendix" if language == "en" else "附录：来源与考试信息"
    practice_label = "Generated practice examples" if language == "en" else "生成例题数量"
    page_label = "Qualification page" if language == "en" else "课程页面"
    spec_label = "Specification PDF" if language == "en" else "考试大纲 PDF"
    hash_value = qualification.source.specification_sha256 or ("not downloaded" if language == "en" else "未下载")
    audience_note = (
        qualification.audience_note
        if language == "en"
        else "官方英文来源和考试结构已保存在结构化输出中，供复核；学生手册正文保持所选中文输出。"
    )
    return f"""
<section class="band source appendix">
  <h2>{html_escape(heading)}</h2>
  <p>{html_escape(audience_note)}</p>
  {listing_note}
  <ul>
    <li>{html_escape(page_label)}: <a href="{html_escape(qualification.page_url)}">{html_escape(qualification.page_url)}</a></li>
    <li>{html_escape(spec_label)}: {link_or_missing(qualification.source.specification_url, language)}</li>
    <li>PDF SHA-256: <code>{html_escape(hash_value)}</code></li>
    <li>{html_escape(practice_label)}: {practice_count}</li>
  </ul>
</section>
{assessment}
"""


def render_source_snippets(snippets: list[SourceSnippet], compact: bool = False, language: str = "en") -> str:
    summary = "Source anchor" if language == "en" else "来源依据"
    if not snippets:
        message = (
            "No page-level source snippet was matched for this section. Review manually."
            if language == "en"
            else "本节没有匹配到页码级来源片段，需要人工复核。"
        )
        return f"<details class=\"source-snippets\"><summary>{html_escape(summary)}</summary><p class=\"warning\">{html_escape(message)}</p></details>"
    css_class = "source-snippets compact" if compact else "source-snippets"
    if language == "zh-CN":
        review_note = "官方英文来源片段已保存在结构化输出中，供老师或维护者复核；学生正文不混排英文原文。"
        items = []
        for snippet in snippets:
            items.append(
                "<li>"
                f"<strong>第 {snippet.page} 页</strong> "
                f"<span>{html_escape(review_note)}</span>"
                "</li>"
            )
        return f"<details class=\"{css_class}\"><summary>{html_escape(summary)}</summary><ul>{''.join(items)}</ul></details>"
    items = []
    for snippet in snippets:
        text = snippet.text
        if compact and len(text) > 220:
            text = f"{text[:220].rstrip()}..."
        items.append(
            "<li>"
            f"<strong>p.{snippet.page}</strong> "
            f"<span>{html_escape(snippet.matched_term)}</span>"
            f"<blockquote>{html_escape(text)}</blockquote>"
            "</li>"
        )
    return f"<details class=\"{css_class}\"><summary>{html_escape(summary)}</summary><ul>{''.join(items)}</ul></details>"


def format_source_reference(
    snippet: SourceSnippet | None,
    language: str = "en",
    include_prefix: bool = False,
) -> str:
    if not snippet:
        return "Source: review required" if language == "en" else "来源：需要复核"
    if language == "en":
        value = f"p.{snippet.page} - {snippet.matched_term}"
        return f"Source: {value}" if include_prefix else value
    value = f"第 {snippet.page} 页（官方原文见结构化来源文件）"
    return f"来源：{value}" if include_prefix else value


def link_or_missing(value: str | None, language: str = "en") -> str:
    if not value:
        missing = "missing" if language == "en" else "缺失"
        return f"<span class=\"warning\">{html_escape(missing)}</span>"
    return f"<a href=\"{html_escape(value)}\">{html_escape(value)}</a>"


def display_topic_title(topic: Topic, index: int, language: str) -> str:
    if language == "en":
        return topic.title
    match = re.match(r"^\s*([A-Z]\d+[A-Z]?|\d+(?:\.\d+)+)\b", topic.title)
    if match:
        return f"第 {match.group(1)} 节"
    keyword_title = localized_topic_title(topic.title, index)
    if keyword_title:
        return keyword_title
    return f"第 {index} 节"


def localized_topic_title(title: str, index: int) -> str | None:
    text = title.lower()
    keyword_titles = [
        (("measurement", "data", "graph"), "测量与数据"),
        (("force", "motion"), "力与运动"),
        (("material", "change"), "材料与变化"),
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
    if re.search(r"[\u4e00-\u9fff]", title):
        return title[:32]
    return None
