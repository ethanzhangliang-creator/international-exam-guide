from __future__ import annotations

from typing import Any

from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.icons import render_icon
from intl_exam_guide.rendering.text import html_escape
from intl_exam_guide.rendering.visual_assets import (
    has_renderable_infographic,
    has_renderable_svg_fallback,
)


def render_infographic_required(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any] | None,
    source_label: str,
    language: str,
) -> str:
    if asset and has_renderable_infographic(asset):
        return _render_generated_infographic(title, visual, asset, source_label, language)
    if asset and has_renderable_svg_fallback(asset):
        return _render_svg_fallback_infographic(title, visual, asset, source_label, language)
    return _render_pending_infographic(title, visual, source_label, language)


def _render_generated_infographic(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any],
    source_label: str,
    language: str,
) -> str:
    filename = str(asset["file"])
    provider = str(asset.get("image_provider") or visual.image_provider)
    caption = "Generated Infographic" if language == "en" else "已生成信息图"
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    model_note = "reviewed visual asset" if language == "en" else "已复核视觉资源"
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


def _render_svg_fallback_infographic(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any],
    source_label: str,
    language: str,
) -> str:
    filename = str(asset["file"])
    caption = "SVG Fallback - Review Needed" if language == "en" else "SVG 兜底图 - 需要复核"
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    model_note = (
        "No callable image model was provided. This SVG is a fallback for a complex "
        "infographic, so details may be less accurate and need review."
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


def _render_pending_infographic(
    title: str,
    visual: VisualBrief,
    source_label: str,
    language: str,
) -> str:
    provider = visual.image_provider
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    if provider.startswith("ask-user"):
        status = "external infographic generation pending" if language == "en" else "复杂信息图待外部生成"
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
