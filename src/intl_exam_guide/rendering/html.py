from __future__ import annotations

import html
from pathlib import Path

from intl_exam_guide.models import GuidePlan, PracticeItem, Qualification, SourceSnippet, Topic, TopicGuide


def render_html(plan: GuidePlan, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qualification = plan.qualification
    parts = [
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">",
        f"<title>{escape(qualification.title)} Revision Guide</title>",
        f"<style>{stylesheet()}</style></head><body>",
        render_cover(qualification),
        render_source_note(qualification),
        render_language_policy(),
        render_summary(qualification),
        render_assessments(qualification),
        render_topic_map(qualification.topics),
        render_revision_stages(plan.revision_stages),
        render_topics(qualification.topics, plan.topic_guides, plan.practice_items),
        render_diagram_briefs(plan.diagram_briefs),
        render_final_checklist(qualification, len(plan.practice_items)),
        "</body></html>",
    ]
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def render_cover(qualification: Qualification) -> str:
    qtype = "International GCSE" if qualification.qualification_type == "international_gcse" else "International AS/A-level"
    return f"""
<section class="cover">
  <div class="kicker">{escape(qtype)} Revision Guide / 复习指南</div>
  <h1>{escape(qualification.title)}</h1>
  <p class="subtitle">Source-traceable final revision guide generated from OxfordAQA public syllabus materials.</p>
  <div class="cover-grid">
    <div><span>Code</span><strong>{escape(qualification.code or "Unknown")}</strong></div>
    <div><span>Topics</span><strong>{len(qualification.topics)}</strong></div>
    <div><span>Assessment papers</span><strong>{len(qualification.assessments)}</strong></div>
  </div>
</section>
"""


def render_source_note(qualification: Qualification) -> str:
    listing_note = render_listing_note(qualification)
    return f"""
<section class="band source">
  <h2>适用对象与来源 / Audience and Sources</h2>
  <p>{escape(qualification.audience_note)}</p>
  {listing_note}
  <ul>
    <li>Qualification page: <a href="{escape(qualification.page_url)}">{escape(qualification.page_url)}</a></li>
    <li>Specification PDF: {link_or_missing(qualification.source.specification_url)}</li>
    <li>PDF SHA-256: <code>{escape(qualification.source.specification_sha256 or "not downloaded")}</code></li>
  </ul>
</section>
"""


def render_language_policy() -> str:
    return """
<section class="band language-policy">
  <h2>语言策略 / Language Policy</h2>
  <ul class="plain">
    <li>Official qualification titles, topic titles, paper titles, syllabus points, and source snippets are kept in English from OxfordAQA.</li>
    <li>Template navigation labels are bilingual: Chinese first, then English.</li>
    <li>Chinese topic translations should be added only from a reviewed glossary or subject-specialist authoring pass.</li>
  </ul>
</section>
"""


def render_listing_note(qualification: Qualification) -> str:
    source = qualification.source
    if not source.listing_group_label and not source.listing_subject:
        return ""
    pieces = []
    if source.listing_subject:
        pieces.append(f"Subject group: {escape(source.listing_subject)}")
    if source.listing_group_label:
        pieces.append(f"Website group: {escape(source.listing_group_label)}")
    if source.listing_style_class:
        pieces.append(f"Detected class: {escape(source.listing_style_class)}")
    return f"<p class=\"listing-note\">{' · '.join(pieces)}</p>"


def render_summary(qualification: Qualification) -> str:
    items = "\n".join(f"<li>{escape(item)}</li>" for item in qualification.summary[:5])
    return f"""
<section class="band">
  <h2>课程定位 / Course Position</h2>
  <ul class="plain">{items}</ul>
</section>
"""


def render_assessments(qualification: Qualification) -> str:
    cards = []
    for paper in qualification.assessments:
        details = "".join(f"<li>{escape(item)}</li>" for item in paper.details[:8])
        cards.append(f"<article class=\"assessment\"><h3>{escape(paper.title)}</h3><ul>{details}</ul></article>")
    body = "\n".join(cards) if cards else "<p class=\"warning\">No assessment structure was extracted. Review the source page manually.</p>"
    return f"<section class=\"band\"><h2>考试结构 / Assessment Structure</h2><div class=\"assessment-grid\">{body}</div></section>"


def render_topic_map(topics: list[Topic]) -> str:
    rows = []
    for index, topic in enumerate(topics, start=1):
        points = ", ".join(topic.points[:4]) if topic.points else "Use the specification text for detailed statements."
        rows.append(
            "<tr>"
            f"<td>{index}</td><td>{escape(topic.title)}</td><td>{escape(points)}</td>"
            "<td>概念边界 -> 例题 -> 错题回看</td>"
            "</tr>"
        )
    return f"""
<section class="band">
  <h2>知识地图 / Knowledge Map</h2>
  <table><thead><tr><th>#</th><th>Topic / 官方主题</th><th>Official syllabus points / 官方大纲要点</th><th>Revision route / 复习路径</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>
"""


def render_revision_stages(stages: list[str]) -> str:
    items = "".join(f"<li>{escape(stage)}</li>" for stage in stages)
    return f"<section class=\"band\"><h2>三阶段复习法 / Three-Stage Revision</h2><ol class=\"stage-list\">{items}</ol></section>"


def render_topics(
    topics: list[Topic],
    topic_guides: list[TopicGuide],
    practice_items: list[PracticeItem],
) -> str:
    grouped: dict[str, list[PracticeItem]] = {}
    for item in practice_items:
        grouped.setdefault(item.topic_title, []).append(item)
    guides = {guide.topic_title: guide for guide in topic_guides}

    sections = []
    for index, topic in enumerate(topics, start=1):
        guide = guides.get(topic.title)
        points = "".join(f"<li>{escape(point)}</li>" for point in topic.points)
        if not points:
            points = "<li>Use the official specification text to expand this topic into teachable sub-points.</li>"
        examples = "\n".join(render_practice(item) for item in grouped.get(topic.title, [])[:2])
        guide_block = render_topic_guide(guide) if guide else ""
        diagram_block = render_topic_diagram(topic, guide, index) if guide else ""
        source_block = render_source_snippets(topic.source_snippets)
        sections.append(
            f"""
<section class="topic">
  <h2>T{index}. {escape(topic.title)}</h2>
  <p class="language-note">官方大纲标题保留英文原文 / Official syllabus title retained in English.</p>
  <div class="topic-grid">
    <div>
      <h3>官方边界 / Official Boundary</h3>
      <ul>{points}</ul>
    </div>
    <div class="logic-card">
      <h3>学习逻辑 / Study Logic</h3>
      <p><strong>一句话目标 / One-line goal:</strong> 先判断本 topic 在考什么，再把每个 syllabus point 变成可解释、可计算或可评价的动作。</p>
      <p><strong>常见失分点 / Common mark-loss point:</strong> 只背关键词但没有回应 command word；只写结论但没有把题干信息用进去。</p>
    </div>
  </div>
  {guide_block}
  {diagram_block}
  {source_block}
  <div class="practice-block">{examples}</div>
</section>
"""
        )
    return "\n".join(sections)


def render_topic_guide(guide: TopicGuide) -> str:
    steps = "".join(f"<li>{escape(step)}</li>" for step in guide.worked_solution_steps)
    checklist = "".join(f"<li>{escape(item)}</li>" for item in guide.checklist)
    return f"""
<div class="guide-grid">
  <article class="essence"><h3>一句话本质 / One-Sentence Essence</h3><p>{escape(guide.essence)}</p></article>
  <article class="analogy"><h3>生活化类比 / Everyday Analogy</h3><p>{escape(guide.analogy)}</p></article>
  <article class="worked"><h3>Mini Worked Example / 小例题推导</h3><p>{escape(guide.mini_worked_example)}</p><ol>{steps}</ol></article>
  <article class="pitfall"><h3>考试陷阱 / Exam Pitfall</h3><p>{escape(guide.pitfall)}</p><ul>{checklist}</ul></article>
</div>
"""


def render_topic_diagram(topic: Topic, guide: TopicGuide, index: int) -> str:
    points = topic.points[:4] or guide.checklist[:4] or [topic.title]
    branches = []
    branch_positions = [(510, 62), (510, 126), (510, 190), (510, 254)]
    colors = ["#1354a5", "#1f7a5b", "#b83246", "#d99a24"]
    for number, point in enumerate(points[:4]):
        x, y = branch_positions[number]
        color = colors[number % len(colors)]
        label = svg_multiline_text(point, x + 18, y + 3, max_chars=26, line_height=16)
        branches.append(
            f"""
<line x1="300" y1="160" x2="{x}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="0.65"/>
<circle cx="{x}" cy="{y}" r="8" fill="{color}"/>
<rect x="{x + 14}" y="{y - 25}" width="238" height="54" rx="12" fill="#ffffff" stroke="{color}" opacity="0.98"/>
{label}
"""
        )

    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = (
        f"Source: p.{source.page} - {source.matched_term}" if source else "Source: review required"
    )
    return f"""
<figure class="topic-diagram" aria-label="Concept map for {escape(topic.title)}">
  <figcaption>Concept map / 图文解释</figcaption>
  <svg viewBox="0 0 820 320" role="img" aria-labelledby="diagram-title-{index}">
    <title id="diagram-title-{index}">Concept map for {escape(topic.title)}</title>
    <rect x="0" y="0" width="820" height="320" rx="18" fill="#f7f9fc"/>
    <rect x="24" y="24" width="310" height="272" rx="18" fill="#124f9b"/>
    <text x="52" y="68" fill="#ffe4a9" font-size="13" font-weight="800">TOPIC {index}</text>
    {svg_multiline_text(topic.title, 52, 112, max_chars=20, line_height=28, size=24, weight=800, fill="#ffffff")}
    <text x="52" y="260" fill="#dceaff" font-size="13">{escape(source_label)}</text>
    {''.join(branches)}
  </svg>
</figure>
"""


def render_practice(item: PracticeItem) -> str:
    frame = "".join(f"<li>{escape(step)}</li>" for step in item.answer_frame)
    solution = "".join(f"<li>{escape(step)}</li>" for step in item.public_solution_steps)
    checkpoints = "".join(f"<li>{escape(point)}</li>" for point in item.answer_checkpoints)
    source = render_source_snippets(item.source_snippets, compact=True)
    return f"""
<article class="practice">
  <h3>{escape(item.topic_title)} - practice card / 练习卡</h3>
  <div class="practice-meta">
    <span>Command: {escape(item.command_word)}</span>
    <span>Difficulty: {escape(item.difficulty)}</span>
    <span>Focus: {escape(item.focus_point)}</span>
  </div>
  <p class="practice-question">{escape(item.question)}</p>
  <h4>Answer frame / 答题框架</h4>
  <ol>{frame}</ol>
  <h4>Public solution steps / 公开解题步骤</h4>
  <ol>{solution}</ol>
  <h4>Answer checkpoints / 答案检查点</h4>
  <ul>{checkpoints}</ul>
  {source}
</article>
"""


def render_diagram_briefs(briefs: list[str]) -> str:
    items = "".join(f"<li>{escape(brief)}</li>" for brief in briefs[:12])
    return f"""
<section class="band">
  <h2>图文解释规划 / Diagram Plan</h2>
  <p>These diagram briefs are intentionally source-bounded. A future image or illustration adapter should render them without adding unsourced syllabus claims.</p>
  <ul>{items}</ul>
</section>
"""


def render_final_checklist(qualification: Qualification, practice_count: int) -> str:
    topics = len(qualification.topics)
    return f"""
<section class="band final">
  <h2>质量检查清单 / Quality Checklist</h2>
  <ul>
    <li>Every topic from the public syllabus summary appears in the guide: {topics} topics.</li>
    <li>Every generated practice item is an original frame, not copied from past papers: {practice_count} items.</li>
    <li>Before giving this to a child, a subject specialist should add or approve worked examples for each topic.</li>
    <li>Confirm the downloaded PDF hash and qualification version before each exam season.</li>
  </ul>
</section>
"""


def render_source_snippets(snippets: list[SourceSnippet], compact: bool = False) -> str:
    if not snippets:
        return "<p class=\"warning\">No page-level source snippet was matched for this section. Review manually.</p>"
    css_class = "source-snippets compact" if compact else "source-snippets"
    items = []
    for snippet in snippets:
        text = snippet.text
        if compact and len(text) > 220:
            text = f"{text[:220].rstrip()}..."
        items.append(
            "<li>"
            f"<strong>p.{snippet.page}</strong> "
            f"<span>{escape(snippet.matched_term)}</span>"
            f"<blockquote>{escape(text)}</blockquote>"
            "</li>"
        )
    return f"<div class=\"{css_class}\"><h3>Source check / 来源核对</h3><ul>{''.join(items)}</ul></div>"


def link_or_missing(value: str | None) -> str:
    if not value:
        return "<span class=\"warning\">missing</span>"
    return f"<a href=\"{escape(value)}\">{escape(value)}</a>"


def escape(value: str) -> str:
    return html.escape(value, quote=True)


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
        tspans.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
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
.cover-grid { display: grid; grid-template-columns: repeat(3, minmax(140px, 1fr)); gap: 12px; max-width: 760px; margin-top: 30px; }
.cover-grid div { border: 1px solid rgba(255,255,255,.32); padding: 16px; background: rgba(255,255,255,.1); }
.cover-grid span { display: block; color: #ffe4a9; font-size: 12px; text-transform: uppercase; }
.cover-grid strong { display: block; font-size: 26px; margin-top: 4px; }
.band, .topic {
  margin: 0 auto;
  padding: 34px 8vw;
  background: white;
  border-bottom: 1px solid var(--line);
}
.source { background: var(--paper); }
.listing-note { padding: 10px 12px; background: #ffffff; border-left: 4px solid var(--gold); }
.language-policy { background: #f7fbff; }
.language-note { margin: -8px 0 16px; color: var(--muted); font-size: 13px; }
h2 { margin: 0 0 16px; font-size: 28px; line-height: 1.15; color: var(--blue); letter-spacing: 0; }
h3 { margin: 0 0 10px; font-size: 17px; color: var(--red); letter-spacing: 0; }
h4 { margin: 12px 0 6px; font-size: 14px; color: var(--blue); letter-spacing: 0; }
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
.topic-diagram svg {
  display: block;
  width: 100%;
  height: auto;
}
.source-snippets { margin-top: 14px; padding: 14px; background: #fffaf1; border: 1px solid #efd7a0; }
.source-snippets h3 { color: var(--green); }
.source-snippets blockquote { margin: 6px 0 8px; color: var(--muted); font-size: 13px; }
.source-snippets.compact { background: transparent; border: 0; padding: 0; }
.source-snippets.compact h3 { font-size: 13px; margin-top: 10px; }
.source-snippets.compact blockquote { display: none; }
.stage-list li { padding: 10px 12px; background: #f3f7fb; border-left: 4px solid var(--green); }
.warning { color: var(--red); font-weight: 700; }
.final { background: #f4fff9; }
@media (max-width: 760px) {
  h1 { font-size: 38px; }
  .cover-grid, .assessment-grid, .topic-grid, .practice-block, .guide-grid { grid-template-columns: 1fr; }
}
@media print {
  body { background: white; }
  .cover { min-height: 270mm; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .band, .topic { break-inside: avoid; padding: 22px 10mm; }
  a { color: inherit; text-decoration: none; }
}
"""
