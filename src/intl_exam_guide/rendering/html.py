from __future__ import annotations

import html
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
from intl_exam_guide.rendering.visual_assets import (
    build_visual_asset_lookup,
    has_renderable_infographic,
    has_renderable_svg_fallback,
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


def render_cover(qualification: Qualification, options: GuideRunOptions) -> str:
    if options.output_language == "en":
        qtype = "International GCSE" if qualification.qualification_type == "international_gcse" else "International AS-A-level"
        return f"""
<section class="cover">
  <div class="kicker">{html_escape(qtype)} Study and Revision Guide</div>
  <h1>{html_escape(qualification.title)}</h1>
  <p class="subtitle">Built from the official specification into learnable, practicable, and checkable knowledge units. Understand first, inspect the visual, then answer the worked examples.</p>
  <div class="cover-grid">
    <div><span>Code</span><strong>{html_escape(qualification.code or "Unknown")}</strong></div>
    <div><span>Knowledge units</span><strong>{len(qualification.topics)}</strong></div>
    <div><span>Assessment papers</span><strong>{len(qualification.assessments)}</strong></div>
    <div><span>Style</span><strong>{html_escape(style_display(options.explanation_style, options.output_language))}</strong></div>
  </div>
</section>
"""
    qtype = "国际 GCSE" if qualification.qualification_type == "international_gcse" else "国际 AS-A-level"
    return f"""
<section class="cover">
  <div class="kicker">{html_escape(qtype)} 学习复习手册</div>
  <h1>{html_escape(subject_display_name(qualification))}学习复习手册</h1>
  <p class="subtitle">按官方大纲拆成可学习、可做题、可检查的知识单元。先理解，再看图，再做例题。</p>
  <div class="cover-grid">
    <div><span>课程编号</span><strong>{html_escape(qualification.code or "未知")}</strong></div>
    <div><span>知识单元</span><strong>{len(qualification.topics)}</strong></div>
    <div><span>考试试卷</span><strong>{len(qualification.assessments)}</strong></div>
    <div><span>讲解风格</span><strong>{html_escape(style_display(options.explanation_style, options.output_language))}</strong></div>
  </div>
</section>
"""


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
      <h3>Preflight Choices</h3>
      <ul>
        <li>Subject request: {html_escape(options.requested_subject)}</li>
        <li>Output language: English</li>
        <li>Image route: {html_escape(image_provider_display(options, options.output_language))}</li>
        <li>Explanation style: {html_escape(style_display(options.explanation_style, options.output_language))}</li>
      </ul>
    </article>
  </div>
</section>
"""
    subject_request = subject_display_name(qualification)
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
      <h3>生成前选择</h3>
      <ul>
        <li>科目：{html_escape(subject_request)}</li>
        <li>输出语言：中文</li>
        <li>生图方式：{html_escape(image_provider_display(options, options.output_language))}</li>
        <li>讲解风格：{html_escape(style_display(options.explanation_style, options.output_language))}</li>
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
        endpoint = options.image_endpoint_url or ("endpoint not set" if language == "en" else "未填写接口地址")
        return f"custom / {model} / {endpoint}" if language == "en" else f"自定义：{model}，{endpoint}"
    if options.image_provider == "prompt-queue":
        return (
            "prompt queue only; complex infographics are not final yet"
            if language == "en"
            else "只生成提示词队列，复杂信息图尚未最终生成"
        )
    if options.image_provider == "deterministic-svg":
        return (
            "deterministic SVG for safe diagrams; complex infographics stay queued"
            if language == "en"
            else "安全图形使用确定性矢量图，复杂信息图进入待生成队列"
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
        route = "concept boundary -> worked example -> error review" if language == "en" else "概念边界 -> 例题 -> 错题回看"
        rows.append(
            "<tr>"
            f"<td>{index}</td><td>{html_escape(title)}</td><td>{html_escape(points)}</td>"
            f"<td>{html_escape(route)}</td>"
            "</tr>"
        )
    if language == "en":
        heading = "Study Roadmap"
        columns = "<tr><th>#</th><th>Knowledge unit</th><th>What to master</th><th>Study route</th></tr>"
    else:
        heading = "复习路线"
        columns = "<tr><th>#</th><th>知识单元</th><th>要掌握什么</th><th>学习路径</th></tr>"
    return f"""
<section class="band">
  <h2>{heading}</h2>
  <table><thead>{columns}</thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>
"""


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
            point_values = ["根据官方大纲抽取结果复习本知识单元。"]
        points = "".join(f"<li>{html_escape(point)}</li>" for point in point_values)
        if not points:
            points = (
                "<li>Use the official specification text to expand this topic into teachable sub-points.</li>"
                if language == "en"
                else "<li>根据官方大纲抽取结果复习本知识单元。</li>"
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
<section class="topic">
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
  {render_story_modes(topic, guide, language) if guide else ""}
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
        return render_infographic_required(topic, visual, index, asset, language)

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


def render_infographic_required(
    topic: Topic,
    visual: VisualBrief,
    index: int,
    asset: dict[str, Any] | None = None,
    language: str = "en",
) -> str:
    title = display_topic_title(topic, index, language)
    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = format_source_reference(source, language)
    if asset and has_renderable_infographic(asset):
        filename = str(asset["file"])
        provider = str(asset.get("image_provider") or visual.image_provider)
        caption = "Generated Infographic" if language == "en" else "已生成信息图"
        source_prefix = "Source anchor" if language == "en" else "来源依据"
        model_note = "reviewed visual asset" if language == "en" else "已复核视觉资产"
        question = "Use the infographic to explain or apply:" if language == "en" else "用这张信息图解释或应用："
        prompt_label = "Generation prompt" if language == "en" else "生图提示词"
        visual_steps = (
            [
                "Read the labels and locate the key relationship.",
                "Match the visual evidence to one precise syllabus term.",
                "Write the final answer in the command word's form.",
            ]
            if language == "en"
            else [
                "阅读标签，定位核心关系。",
                "把图中证据对应到一个准确的大纲术语。",
                "按指令词要求写出最终答案。",
            ]
        )
        step_items = "".join(f"<li>{html_escape(step)}</li>" for step in visual_steps)
        return f"""
<figure class="visual-example generated-infographic" aria-label="Generated infographic for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="generated-infographic-grid">
    <img class="infographic-image" src="images/{html_escape(filename)}" alt="{html_escape(title)} infographic for {html_escape(visual.focus_point)}">
    <div class="visual-notes">
      <div class="visual-model">{html_escape(provider)} - {html_escape(model_note)}</div>
      <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
      <p class="visual-question">{html_escape(question)} <strong>{html_escape(visual.focus_point)}</strong>.</p>
      <ol>{step_items}</ol>
      <details class="visual-prompt">
        <summary>{html_escape(prompt_label)}</summary>
        <p>{html_escape(visual.prompt)}</p>
      </details>
    </div>
  </div>
</figure>
"""
    if asset and has_renderable_svg_fallback(asset):
        filename = str(asset["file"])
        caption = "SVG Fallback - Review Needed" if language == "en" else "SVG 兜底图 - 需要复核"
        source_prefix = "Source anchor" if language == "en" else "来源依据"
        model_note = (
            "No callable image model was provided. This SVG is a fallback for a complex infographic, so details may be less accurate and need review."
            if language == "en"
            else "未提供可调用生图模型或方式；这是复杂信息图的 SVG 兜底图，细节可能不够准确，需要复核。"
        )
        question = "Use this draft only as a study aid for:" if language == "en" else "这张草图仅用于辅助理解："
        prompt_label = "External image brief" if language == "en" else "外部生图需求"
        visual_steps = (
            [
                "Check whether the shape, labels, and relationships match the syllabus point.",
                "Replace this SVG with a reviewed infographic if a suitable image model or designer is available.",
                "Do not treat this fallback as a factual source.",
            ]
            if language == "en"
            else [
                "先检查形状、标签和关系是否符合大纲知识点。",
                "如果有合适的生图模型或人工设计方式，应替换成复核后的信息图。",
                "不要把这张兜底图当作事实来源。",
            ]
        )
        step_items = "".join(f"<li>{html_escape(step)}</li>" for step in visual_steps)
        return f"""
<figure class="visual-example svg-fallback" aria-label="SVG fallback for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="generated-infographic-grid">
    <img class="infographic-image" src="images/{html_escape(filename)}" alt="{html_escape(title)} SVG fallback for {html_escape(visual.focus_point)}">
    <div class="visual-notes">
      <div class="visual-model">{html_escape(model_note)}</div>
      <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
      <p class="visual-question">{html_escape(question)} <strong>{html_escape(visual.focus_point)}</strong>.</p>
      <ol>{step_items}</ol>
      <details class="visual-prompt">
        <summary>{html_escape(prompt_label)}</summary>
        <p>{html_escape(visual.prompt)}</p>
      </details>
    </div>
  </div>
</figure>
"""
    provider = visual.image_provider
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    if provider.startswith("ask-user"):
        status = (
            "external infographic generation pending"
            if language == "en"
            else "复杂信息图待外部生成"
        )
    else:
        status = (
            f"waiting for reviewed image asset from {provider}"
            if language == "en"
            else f"等待 {provider} 生成并复核"
        )
    caption = "Infographic Queue" if language == "en" else "信息图生成队列"
    why_label = "Why not SVG" if language == "en" else "为什么需要信息图模型"
    type_label = "Visual type" if language == "en" else "图形类型"
    focus_label = "Focus" if language == "en" else "聚焦知识点"
    prompt_label = "Prompt queue" if language == "en" else "生图提示词"
    return f"""
<figure class="visual-example infographic-required" aria-label="Infographic required for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="infographic-card">
    <div class="visual-model">{html_escape(status)}</div>
    <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
    <p><strong>{html_escape(why_label)}:</strong> {html_escape(visual.trigger)}</p>
    <p><strong>{html_escape(type_label)}:</strong> {html_escape(visual.visual_type)}</p>
    <p><strong>{html_escape(focus_label)}:</strong> {html_escape(visual.focus_point)}</p>
    <details class="visual-prompt">
      <summary>{html_escape(prompt_label)}</summary>
      <p>{html_escape(visual.prompt)}</p>
    </details>
  </div>
</figure>
"""


def render_topic_visual_svg(visual: VisualBrief, index: int, language: str = "en") -> str:
    if language == "zh-CN":
        return render_zh_visual_svg(visual, index)
    text = visual.visual_type.lower()
    if any(word in text for word in ["number line", "fraction", "ratio"]):
        return render_number_svg(index)
    if any(word in text for word in ["function graph", "equation-balance", "algebra"]):
        return render_algebra_svg(index)
    if any(word in text for word in ["statistics chart", "probability"]):
        return render_statistics_svg(index)
    if any(
        word in text
        for word in ["geometry diagram", "triangle", "trigonometry", "pythagoras", "transformation"]
    ):
        return render_triangle_svg(index)
    if any(word in text for word in ["distance-time", "motion graph"]):
        return render_motion_svg(index)
    if any(word in text for word in ["data table", "graph interpretation"]):
        return render_statistics_svg(index)
    if any(word in text for word in ["rate", "equilibrium"]):
        return render_rate_svg(index)
    if any(word in text for word in ["energy", "exothermic", "endothermic"]):
        return render_energy_svg(index)
    if any(word in text for word in ["acid", "base", "salt", "ph"]):
        return render_ph_svg(index)
    if any(word in text for word in ["solid", "liquid", "particle", "atom"]):
        return render_particles_svg(index)
    if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
        return render_bonding_svg(index)
    if any(word in text for word in ["organic", "hydrocarbon", "carbon"]):
        return render_organic_svg(index)
    if any(
        word in text
        for word in ["chemical analysis", "chromatography", "identification of common gases", "identification of ions"]
    ):
        return render_analysis_svg(index)
    return render_particles_svg(index)


def render_story_modes(topic: Topic, guide: TopicGuide, language: str) -> str:
    focus = topic.points[0] if topic.points else guide.topic_title
    if language == "en":
        return f"""
<div class="story-modes" aria-label="Narrative explanation styles for {html_escape(topic.title)}">
  <article>
    <h3>{render_icon("life")}<span>Life Scene</span></h3>
    <p>Understand <strong>{html_escape(topic.title)}</strong> through a real situation: observe what happens, then explain it using <strong>{html_escape(focus)}</strong>.</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>Detective Mode</span></h3>
    <p>Answer like a case: the question data are clues, the syllabus term is evidence, and the conclusion must match the command word.</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>Adventure Mode</span></h3>
    <p>Break the topic into a mission: unlock the term, avoid the common trap, and finish with one check sentence. The framing is original and does not copy protected IP.</p>
  </article>
</div>
"""
    title = "本知识单元"
    focus = guide.checklist[0] if guide.checklist else "本节核心要求"
    return f"""
<div class="story-modes" aria-label="叙事化讲解风格：{html_escape(title)}">
  <article>
    <h3>{render_icon("life")}<span>生活场景</span></h3>
    <p>把 <strong>{html_escape(title)}</strong> 当成身边的一件事来理解：先找现象，再用 <strong>{html_escape(focus)}</strong> 解释它为什么发生。</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>侦探推理</span></h3>
    <p>像破案一样答题：线索是题干数据，证据是大纲术语，结论必须回到指令词。</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>闯关感讲解</span></h3>
    <p>把知识点拆成任务：解锁术语、避开常见陷阱、用一句检查句完成本关。默认使用原创冒险语气，不复刻具体作品设定。</p>
  </article>
</div>
"""


def render_number_svg(index: int) -> str:
    ticks = []
    labels = []
    for value in range(-3, 4):
        x = 104 + (value + 3) * 56
        ticks.append(f'<path d="M{x} 170v16" stroke="#172033" stroke-width="3"/>')
        labels.append(
            f'<text x="{x - 7}" y="212" font-size="17" font-weight="800" fill="#172033">{value}</text>'
        )
    fraction_segments = []
    for number in range(4):
        color = "#1354a5" if number < 3 else "#edf4ff"
        fraction_segments.append(
            f'<rect x="{456 + number * 42}" y="112" width="42" height="56" fill="{color}" stroke="#172033" stroke-width="2"/>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Number line, fraction bar, and ratio diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="70" fill="#1354a5" font-size="23" font-weight="800">Number sense</text>
  <path d="M88 178h368" stroke="#172033" stroke-width="4" marker-end="url(#numarrow-{index})"/>
  <defs><marker id="numarrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {''.join(ticks)}
  {''.join(labels)}
  <circle cx="328" cy="178" r="10" fill="#b83246"/>
  <text x="92" y="238" font-size="15" fill="#5b677a">
    <tspan x="92" dy="0">compare positions</tspan>
    <tspan x="92" dy="20">then check decimals and bounds</tspan>
  </text>
  <text x="454" y="94" font-size="19" font-weight="800" fill="#b83246">3 / 4</text>
  {''.join(fraction_segments)}
  <text x="454" y="198" font-size="16" fill="#5b677a">fraction bar: part-whole</text>
  <rect x="456" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="522" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="596" y="238" width="58" height="40" rx="8" fill="#fff1f3" stroke="#b83246" stroke-width="3"/>
  <text x="462" y="304" font-size="18" font-weight="800" fill="#1f7a5b">2</text>
  <text x="598" y="304" font-size="18" font-weight="800" fill="#b83246">1</text>
  <text x="504" y="314" font-size="15" fill="#5b677a">ratio blocks</text>
</svg>
"""


def render_algebra_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Function graph and equation balance</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Algebra links symbols to shapes</text>
  <rect x="58" y="92" width="282" height="210" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M96 262V118M96 262h210" stroke="#172033" stroke-width="4"/>
  <path d="M100 244C130 228 160 204 190 174C226 138 256 126 302 126" fill="none" stroke="#b83246" stroke-width="5"/>
  <path d="M97 207h208M145 262V120M195 262V120M245 262V120" stroke="#d7deea" stroke-width="2"/>
  <text x="110" y="136" font-size="18" font-weight="800" fill="#b83246">graph of a rule</text>
  <text x="248" y="286" font-size="17" font-weight="800">x</text>
  <text x="76" y="130" font-size="17" font-weight="800">y</text>
  <rect x="396" y="104" width="260" height="178" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <path d="M526 138v88M448 226h156" stroke="#172033" stroke-width="5" stroke-linecap="round"/>
  <path d="M468 154l-42 72h84z" fill="#edf4ff" stroke="#1354a5" stroke-width="3"/>
  <path d="M584 154l-42 72h84z" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <text x="436" y="205" font-size="25" font-weight="800" fill="#1354a5">x + 3</text>
  <text x="564" y="205" font-size="25" font-weight="800" fill="#1f7a5b">7</text>
  <text x="430" y="82" font-size="18" font-weight="800" fill="#d99a24">equation balance</text>
  <text x="418" y="314" font-size="16" fill="#5b677a">transform both sides, then check the solution</text>
</svg>
"""


def render_statistics_svg(index: int) -> str:
    points = [(300, 228), (328, 205), (358, 214), (388, 174), (424, 158), (456, 126)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#b83246"/>' for x, y in points)
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Statistics chart and probability visual</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Data becomes evidence</text>
  <rect x="58" y="94" width="178" height="190" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M92 246V126M92 246h112" stroke="#172033" stroke-width="4"/>
  <rect x="108" y="200" width="24" height="46" fill="#1354a5"/>
  <rect x="144" y="170" width="24" height="76" fill="#1f7a5b"/>
  <rect x="180" y="140" width="24" height="106" fill="#d99a24"/>
  <text x="78" y="274" font-size="14" fill="#5b677a">compare groups</text>
  <rect x="268" y="94" width="210" height="190" rx="14" fill="#fffaf1" stroke="#d99a24"/>
  <path d="M300 246V120M300 246h168" stroke="#172033" stroke-width="4"/>
  {dots}
  <path d="M300 236L462 124" stroke="#1f7a5b" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="310" y="274" font-size="14" fill="#5b677a">describe trend</text>
  <rect x="510" y="94" width="150" height="190" rx="14" fill="#fff7f8" stroke="#e5aab4"/>
  <circle cx="545" cy="164" r="7" fill="#b83246"/>
  <path d="M552 164h28M580 164l38-42M580 164l38 42" stroke="#172033" stroke-width="3" fill="none"/>
  <circle cx="624" cy="122" r="7" fill="#1f7a5b"/>
  <circle cx="624" cy="206" r="7" fill="#d99a24"/>
  <text x="528" y="238" font-size="14" fill="#5b677a">probability tree</text>
</svg>
"""


def render_particles_svg(index: int) -> str:
    dots = []
    for row in range(3):
        for col in range(4):
            dots.append(f'<circle cx="{92 + col * 22}" cy="{102 + row * 22}" r="7" fill="#1354a5"/>')
    liquid = [
        '<circle cx="330" cy="118" r="8" fill="#1f7a5b"/>',
        '<circle cx="356" cy="132" r="8" fill="#1f7a5b"/>',
        '<circle cx="315" cy="150" r="8" fill="#1f7a5b"/>',
        '<circle cx="372" cy="164" r="8" fill="#1f7a5b"/>',
        '<circle cx="342" cy="176" r="8" fill="#1f7a5b"/>',
    ]
    gas = [
        '<circle cx="535" cy="92" r="8" fill="#b83246"/>',
        '<circle cx="606" cy="125" r="8" fill="#b83246"/>',
        '<circle cx="558" cy="180" r="8" fill="#b83246"/>',
    ]
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Particle model diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="48" y="58" fill="#b83246" font-size="20" font-weight="800">Particle model</text>
  <rect x="70" y="82" width="130" height="130" rx="14" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="290" y="82" width="130" height="130" rx="14" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="510" y="82" width="130" height="130" rx="14" fill="#fff1f3" stroke="#e5aab4"/>
  {''.join(dots)}
  {''.join(liquid)}
  {''.join(gas)}
  <path d="M220 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <path d="M440 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <defs><marker id="arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
  <text x="92" y="250" font-size="22" font-weight="800" fill="#1354a5">solid</text>
  <text x="322" y="250" font-size="22" font-weight="800" fill="#1f7a5b">liquid</text>
  <text x="552" y="250" font-size="22" font-weight="800" fill="#b83246">gas</text>
  <text x="70" y="292" font-size="16" fill="#5b677a">arrangement and movement explain state changes</text>
</svg>
"""


def render_triangle_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Right triangle diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="62" y="70" fill="#1354a5" font-size="22" font-weight="800">5-12-13 right triangle</text>
  <path d="M220 285h92L220 65z" fill="#ffffff" stroke="#111827" stroke-width="5"/>
  <path d="M220 259h26v26" fill="none" stroke="#111827" stroke-width="4"/>
  <text x="187" y="67" font-size="34" font-weight="800">A</text>
  <text x="320" y="306" font-size="34" font-weight="800">B</text>
  <text x="187" y="306" font-size="34" font-weight="800">C</text>
  <text x="245" y="324" font-size="25" font-weight="700">5 cm</text>
  <text x="120" y="184" font-size="25" font-weight="700">12 cm</text>
  <text x="288" y="166" font-size="25" font-weight="700">13 cm</text>
  <rect x="440" y="108" width="190" height="130" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <text x="466" y="150" font-size="22" font-weight="800" fill="#b83246">c² = a² + b²</text>
  <text x="466" y="188" font-size="19" fill="#172033">5² + 12² = 169</text>
  <text x="466" y="222" font-size="19" fill="#172033">c = 13 cm</text>
</svg>
"""


def render_motion_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Distance-time graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="23" font-weight="800">Distance-time graph</text>
  <path d="M100 280V92M100 280h500" stroke="#172033" stroke-width="4"/>
  <path d="M105 255L235 195L365 195L540 105" fill="none" stroke="#1354a5" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="105" cy="255" r="7" fill="#b83246"/>
  <circle cx="235" cy="195" r="7" fill="#b83246"/>
  <circle cx="365" cy="195" r="7" fill="#b83246"/>
  <circle cx="540" cy="105" r="7" fill="#b83246"/>
  <path d="M235 195h130" stroke="#d99a24" stroke-width="5"/>
  <text x="118" y="104" font-size="17" font-weight="800" fill="#b83246">distance</text>
  <text x="552" y="310" font-size="17" font-weight="800" fill="#1f7a5b">time</text>
  <text x="128" y="236" font-size="16" fill="#5b677a">moving</text>
  <text x="260" y="184" font-size="16" fill="#9b6a10">stationary</text>
  <text x="430" y="136" font-size="16" fill="#5b677a">faster speed</text>
  <text x="104" y="322" font-size="15" fill="#5b677a">steeper line = greater speed</text>
</svg>
"""


def render_rate_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Rate of reaction graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M95 275V70M95 275h520" stroke="#172033" stroke-width="4"/>
  <path d="M100 260C180 150 255 100 410 94C500 91 565 91 615 91" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M100 260C170 190 250 160 420 156C505 154 570 154 615 154" fill="none" stroke="#d99a24" stroke-width="6"/>
  <text x="118" y="66" font-size="18" font-weight="800" fill="#b83246">product formed</text>
  <text x="548" y="306" font-size="18" font-weight="800" fill="#1f7a5b">time</text>
  <text x="430" y="88" font-size="18" fill="#1354a5">faster rate</text>
  <text x="430" y="150" font-size="18" fill="#9b6a10">slower rate</text>
</svg>
"""


def render_energy_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Reaction energy profile</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M90 280V70M90 280h540" stroke="#172033" stroke-width="4"/>
  <path d="M120 245C230 245 235 88 350 88C465 88 470 185 600 185" fill="none" stroke="#b83246" stroke-width="6"/>
  <path d="M145 245h92M505 185h92" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M350 98v135" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="120" y="270" font-size="17" font-weight="800">reactants</text>
  <text x="500" y="210" font-size="17" font-weight="800">products</text>
  <text x="365" y="160" font-size="18" fill="#9b6a10">activation energy</text>
  <text x="110" y="62" font-size="18" font-weight="800" fill="#b83246">energy</text>
</svg>
"""


def render_ph_svg(index: int) -> str:
    segments = []
    colors = ["#b83246", "#d45c3f", "#d99a24", "#95b84a", "#1f7a5b", "#217c9b", "#1354a5"]
    for i, color in enumerate(colors):
        segments.append(f'<rect x="{84 + i * 76}" y="146" width="76" height="54" fill="{color}"/>')
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">pH scale and salt preparation</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="88" font-size="24" font-weight="800" fill="#1354a5">pH scale</text>
  {''.join(segments)}
  <text x="86" y="226" font-size="18" font-weight="800">0</text>
  <text x="300" y="226" font-size="18" font-weight="800">7</text>
  <text x="590" y="226" font-size="18" font-weight="800">14</text>
  <text x="94" y="130" font-size="18" fill="#b83246">acid</text>
  <text x="312" y="130" font-size="18" fill="#1f7a5b">neutral</text>
  <text x="548" y="130" font-size="18" fill="#1354a5">alkali</text>
</svg>
"""


def render_organic_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Hydrocarbon chain diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="82" font-size="24" font-weight="800" fill="#1354a5">hydrocarbon model</text>
  <path d="M178 178h100h100h100" stroke="#172033" stroke-width="5"/>
  <g fill="#1354a5" stroke="#172033" stroke-width="3">
    <circle cx="178" cy="178" r="32"/><circle cx="278" cy="178" r="32"/>
    <circle cx="378" cy="178" r="32"/><circle cx="478" cy="178" r="32"/>
  </g>
  <g fill="#ffffff" font-size="24" font-weight="800" text-anchor="middle">
    <text x="178" y="187">C</text><text x="278" y="187">C</text>
    <text x="378" y="187">C</text><text x="478" y="187">C</text>
  </g>
  <text x="160" y="272" font-size="18" fill="#5b677a">structure helps explain reactions and properties</text>
</svg>
"""


def render_analysis_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Chromatography diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="140" y="72" width="170" height="235" rx="18" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <path d="M170 250h110" stroke="#1354a5" stroke-width="4"/>
  <path d="M225 250V98" stroke="#172033" stroke-width="3"/>
  <circle cx="225" cy="223" r="11" fill="#b83246"/>
  <circle cx="225" cy="178" r="11" fill="#d99a24"/>
  <circle cx="225" cy="130" r="11" fill="#1f7a5b"/>
  <path d="M430 96h105M430 154h105M430 212h105" stroke="#d7deea" stroke-width="4"/>
  <text x="430" y="88" font-size="18" font-weight="800" fill="#1f7a5b">separated spots</text>
  <text x="430" y="246" font-size="18" fill="#5b677a">compare position and colour</text>
</svg>
"""


def render_bonding_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Bonding and structure diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="74" font-size="24" font-weight="800" fill="#1354a5">bonding model</text>
  <rect x="74" y="104" width="150" height="150" rx="16" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="285" y="104" width="150" height="150" rx="16" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="496" y="104" width="150" height="150" rx="16" fill="#fff1f3" stroke="#e5aab4"/>
  <g fill="#1354a5"><circle cx="124" cy="150" r="16"/><circle cx="174" cy="150" r="16"/><circle cx="124" cy="202" r="16"/><circle cx="174" cy="202" r="16"/></g>
  <g fill="#ffffff" font-size="15" font-weight="800" text-anchor="middle"><text x="124" y="155">+</text><text x="174" y="155">-</text><text x="124" y="207">-</text><text x="174" y="207">+</text></g>
  <g stroke="#172033" stroke-width="4"><path d="M332 178h56"/><path d="M360 150v56"/></g>
  <g fill="#1f7a5b"><circle cx="332" cy="178" r="18"/><circle cx="388" cy="178" r="18"/><circle cx="360" cy="150" r="18"/><circle cx="360" cy="206" r="18"/></g>
  <g fill="#b83246"><circle cx="542" cy="150" r="16"/><circle cx="600" cy="150" r="16"/><circle cx="542" cy="204" r="16"/><circle cx="600" cy="204" r="16"/></g>
  <path d="M526 176h90M571 132v92" stroke="#d99a24" stroke-width="3" stroke-dasharray="6 6"/>
  <text x="116" y="286" font-size="20" font-weight="800" fill="#1354a5">ionic</text>
  <text x="315" y="286" font-size="20" font-weight="800" fill="#1f7a5b">covalent</text>
  <text x="530" y="286" font-size="20" font-weight="800" fill="#b83246">metallic</text>
</svg>
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
    title = item.topic_title if language == "en" else (display_title or "本知识单元")
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


def render_icon(name: str) -> str:
    paths = {
        "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
        "bridge": '<path d="M4 15c3-7 13-7 16 0"/><path d="M4 15h16"/><path d="M8 15v-3"/><path d="M16 15v-3"/>',
        "steps": '<path d="M5 18h4v-4h4v-4h4V6h2"/><path d="M5 18h14"/>',
        "alert": '<path d="M12 4 3 20h18L12 4z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
        "practice": '<path d="M6 4h9l3 3v13H6z"/><path d="M14 4v4h4"/><path d="M9 13h6"/><path d="M9 17h4"/>',
        "command": '<path d="M7 8h10"/><path d="M7 12h7"/><path d="M7 16h4"/>',
        "level": '<path d="M5 17h3v-5H5z"/><path d="M11 17h3V7h-3z"/><path d="M17 17h3V4h-3z"/>',
        "focus": '<circle cx="12" cy="12" r="7"/><path d="M12 9v3l2 2"/>',
        "frame": '<rect x="5" y="6" width="14" height="12" rx="2"/><path d="M8 10h8"/><path d="M8 14h6"/>',
        "check": '<path d="m5 12 4 4 10-10"/>',
        "visual": '<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m7 17 4-4 3 3 2-2 2 3"/>',
        "life": '<path d="M4 12 12 5l8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-5h4v5"/>',
        "detective": '<circle cx="11" cy="11" r="5"/><path d="m15 15 5 5"/><path d="M8 11h6"/>',
        "quest": '<path d="M12 3 4 7v6c0 5 3.5 7.5 8 8 4.5-.5 8-3 8-8V7z"/><path d="M9 12l2 2 4-5"/>',
    }
    path = paths.get(name, paths["target"])
    return (
        '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{path}</svg>'
    )


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


def subject_display_name(qualification: Qualification) -> str:
    source = f"{qualification.subject_area or ''} {qualification.title}".lower()
    subject_map = [
        ("mathematics", "数学"),
        ("maths", "数学"),
        ("chemistry", "化学"),
        ("economics", "经济学"),
        ("accounting", "会计学"),
        ("business", "商务"),
        ("physics", "物理"),
        ("biology", "生物"),
        ("computer science", "计算机科学"),
        ("english", "英语"),
    ]
    for key, label in subject_map:
        if key in source:
            return label
    return "本课程"


def display_topic_title(topic: Topic, index: int, language: str) -> str:
    if language == "en":
        return topic.title
    match = re.match(r"^\s*([A-Z]\d+[A-Z]?|\d+(?:\.\d+)+)\b", topic.title)
    if match:
        return f"大纲点 {match.group(1)}"
    return f"知识单元 {index}"


def html_escape(value: str) -> str:
    return html.escape(value, quote=True)


def render_zh_visual_svg(visual: VisualBrief, index: int) -> str:
    title = visual.visual_type or "图文结合学习图"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">中文图文学习图</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="54" y="58" width="210" height="244" rx="18" fill="#edf4ff" stroke="#9cbce8" stroke-width="3"/>
  <rect x="292" y="58" width="170" height="104" rx="16" fill="#ecf8f3" stroke="#a7d5c3" stroke-width="3"/>
  <rect x="292" y="198" width="170" height="104" rx="16" fill="#fff3d8" stroke="#e6c36d" stroke-width="3"/>
  <rect x="492" y="58" width="174" height="244" rx="18" fill="#fff1f3" stroke="#e5aab4" stroke-width="3"/>
  <path d="M264 180h28M462 110h30M462 250h30" stroke="#172033" stroke-width="4" marker-end="url(#arrow-zh-{index})"/>
  <defs><marker id="arrow-zh-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="92" y="106" font-size="25" font-weight="800" fill="#1354a5">图解</text>
  {svg_multiline_text(title, 92, 148, 10, 28, 24, 800, "#172033")}
  <text x="326" y="106" font-size="22" font-weight="800" fill="#1f7a5b">观察</text>
  <text x="326" y="246" font-size="22" font-weight="800" fill="#8a5f11">方法</text>
  <text x="530" y="108" font-size="22" font-weight="800" fill="#b83246">检查</text>
  <text x="326" y="136" font-size="16" fill="#5b677a">先看图中关系</text>
  <text x="326" y="276" font-size="16" fill="#5b677a">再写解题步骤</text>
  <text x="530" y="144" font-size="16" fill="#5b677a">最后回到题问</text>
  <text x="530" y="176" font-size="16" fill="#5b677a">术语、单位、结论</text>
</svg>
"""


def svg_multiline_text(
    value: str,
    x: int,
    y: int,
    max_chars: int,
    line_height: int,
    size: int = 12,
    weight: int = 700,
    fill: str = "#172033",
) -> str:
    lines = wrap_words(value, max_chars=max_chars)[:3]
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x}" dy="{dy}">{html_escape(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}">{"".join(tspans)}</text>'
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    words = value.replace("/", " / ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word[:max_chars]
    if current:
        lines.append(current)
    return lines or [value[:max_chars]]


def stylesheet() -> str:
    return """
:root {
  --ink: #172033;
  --muted: #5b677a;
  --paper: #fffaf1;
  --blue: #1354a5;
  --red: #b83246;
  --green: #1f7a5b;
  --gold: #d99a24;
  --line: #d7deea;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background: #eef2f7;
  font: 15px/1.65 "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}
a { color: var(--blue); }
.cover {
  min-height: 92vh;
  padding: 54px 8vw;
  color: white;
  background:
    linear-gradient(90deg, #124f9b 0 72%, #b83246 72% 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-bottom: 12px solid var(--gold);
}
.kicker { color: #ffe4a9; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
h1 { max-width: 920px; font-size: 52px; line-height: 1.05; margin: 18px 0; letter-spacing: 0; }
.subtitle { max-width: 760px; font-size: 19px; color: #f7f1e6; }
.cover-grid { display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; max-width: 920px; margin-top: 30px; }
.cover-grid div { border: 1px solid rgba(255,255,255,.32); padding: 16px; background: rgba(255,255,255,.1); }
.cover-grid span { display: block; color: #ffe4a9; font-size: 12px; text-transform: uppercase; }
.cover-grid strong { display: block; font-size: 26px; margin-top: 4px; }
.band, .topic {
  margin: 0 auto;
  padding: 34px 8vw;
  background: white;
  border-bottom: 1px solid var(--line);
}
.student-overview { background: #fffaf1; }
.overview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.overview-grid article {
  border: 1px solid var(--line);
  border-left: 5px solid var(--green);
  padding: 16px;
  background: #ffffff;
}
.source { background: var(--paper); }
.listing-note { padding: 10px 12px; background: #ffffff; border-left: 4px solid var(--gold); }
.language-policy { background: #f7fbff; }
.language-note { margin: -8px 0 16px; color: var(--muted); font-size: 13px; }
h2 { margin: 0 0 16px; font-size: 28px; line-height: 1.15; color: var(--blue); letter-spacing: 0; }
h3 { margin: 0 0 10px; font-size: 17px; color: var(--red); letter-spacing: 0; }
h4 { margin: 12px 0 6px; font-size: 14px; color: var(--blue); letter-spacing: 0; }
.icon {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  vertical-align: -4px;
  margin-right: 6px;
}
.guide-grid h3,
.practice h3,
.practice h4,
.story-modes h3,
.visual-example figcaption {
  display: flex;
  align-items: center;
  gap: 6px;
}
ul, ol { padding-left: 22px; }
li { margin: 5px 0; }
code { overflow-wrap: anywhere; color: var(--red); }
table { width: 100%; border-collapse: collapse; margin-top: 14px; }
th { background: var(--blue); color: #fff; text-align: left; }
th, td { border: 1px solid var(--line); padding: 10px 12px; vertical-align: top; }
.assessment-grid, .topic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.assessment, .logic-card, .practice {
  border: 1px solid var(--line);
  border-left: 5px solid var(--gold);
  padding: 16px;
  background: #fbfcff;
}
.guide-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.guide-grid article {
  border: 1px solid var(--line);
  padding: 14px;
  background: white;
}
.essence { border-left: 5px solid var(--gold) !important; }
.analogy { border-left: 5px solid var(--green) !important; }
.worked { border-left: 5px solid var(--blue) !important; }
.pitfall { border-left: 5px solid var(--red) !important; }
.topic:nth-of-type(odd) { background: #fbfcff; }
.practice-block { margin-top: 16px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.practice-meta { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 10px; }
.practice-meta span {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 999px;
  background: #edf4ff;
  color: var(--blue);
  font-size: 12px;
  font-weight: 800;
}
.practice-question { font-weight: 700; }
.visual-example {
  margin: 18px 0 0;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--red);
}
.visual-example figcaption {
  margin-bottom: 12px;
  color: var(--red);
  font-weight: 800;
}
.visual-grid {
  display: grid;
  grid-template-columns: minmax(0, .58fr) minmax(240px, .42fr);
  gap: 16px;
  align-items: stretch;
}
.visual-svg {
  display: block;
  width: 100%;
  height: auto;
}
.visual-notes {
  border: 1px solid var(--line);
  padding: 16px;
  background: #fbfcff;
}
.infographic-required {
  border-left-color: var(--gold);
}
.generated-infographic {
  border-left-color: var(--green);
}
.generated-infographic-grid {
  display: grid;
  grid-template-columns: minmax(0, .64fr) minmax(240px, .36fr);
  gap: 16px;
  align-items: stretch;
}
.infographic-image {
  display: block;
  width: 100%;
  max-height: 560px;
  object-fit: contain;
  background: #ffffff;
  border: 1px solid var(--line);
}
.infographic-card {
  border: 1px solid var(--line);
  padding: 16px;
  background: #fffaf1;
}
.visual-model,
.visual-source {
  display: inline-block;
  margin: 0 6px 12px 0;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}
.visual-model { background: #edf4ff; color: var(--blue); }
.visual-source { background: #fff3d8; color: #8a5f11; }
.visual-question {
  margin: 0 0 10px;
  font-weight: 700;
}
.visual-prompt {
  margin-top: 12px;
  padding: 10px 12px;
  background: #ffffff;
  border: 1px solid var(--line);
}
.visual-prompt summary {
  cursor: pointer;
  color: var(--red);
  font-weight: 800;
}
.visual-prompt p {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 13px;
}
.story-modes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}
.story-modes article {
  border: 1px solid var(--line);
  padding: 14px;
  background: #ffffff;
}
.story-modes article:nth-child(1) { border-left: 5px solid var(--green); }
.story-modes article:nth-child(2) { border-left: 5px solid var(--blue); }
.story-modes article:nth-child(3) { border-left: 5px solid var(--gold); }
.story-modes p { margin: 0; }
.topic-diagram {
  margin: 16px 0 0;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--green);
}
.topic-diagram figcaption {
  margin-bottom: 10px;
  color: var(--green);
  font-weight: 800;
}
.concept-html-map {
  display: grid;
  grid-template-columns: minmax(220px, .38fr) minmax(0, .62fr);
  gap: 14px;
}
.concept-core {
  padding: 18px;
  color: white;
  background: #124f9b;
}
.concept-core span {
  display: block;
  color: #ffe4a9;
  font-size: 12px;
  font-weight: 800;
}
.concept-core strong {
  display: block;
  margin: 12px 0;
  font-size: 22px;
  line-height: 1.2;
}
.concept-core small {
  display: block;
  color: #dceaff;
}
.concept-html-map ol {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.concept-html-map li {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--line);
  background: #fbfcff;
}
.concept-html-map li span {
  grid-row: span 2;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: white;
  background: var(--green);
  display: grid;
  place-items: center;
  font-weight: 800;
}
.concept-html-map li strong {
  min-width: 0;
}
.concept-html-map li em {
  color: var(--muted);
  font-size: 12px;
  font-style: normal;
}
.source-snippets { margin-top: 14px; padding: 12px 14px; background: #f8fafc; border: 1px solid var(--line); }
.source-snippets summary { cursor: pointer; font-weight: 800; color: var(--blue); }
.source-snippets blockquote { margin: 6px 0 8px; color: var(--muted); font-size: 13px; }
.source-snippets.compact { background: transparent; border: 0; padding: 0; }
.source-snippets.compact blockquote { display: none; }
.stage-list li { padding: 10px 12px; background: #f3f7fb; border-left: 4px solid var(--green); }
.warning { color: var(--red); font-weight: 700; }
.final { background: #f4fff9; }
@media (max-width: 760px) {
  h1 { font-size: 38px; }
  .cover-grid, .overview-grid, .assessment-grid, .topic-grid, .practice-block, .guide-grid, .visual-grid, .generated-infographic-grid, .story-modes, .concept-html-map, .concept-html-map ol { grid-template-columns: 1fr; }
}
@media print {
  body { background: white; }
  .cover { min-height: 270mm; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .band, .topic { break-inside: avoid; padding: 22px 10mm; }
  a { color: inherit; text-decoration: none; }
}
"""
