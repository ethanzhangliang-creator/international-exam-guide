from __future__ import annotations


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
  padding: 34px max(24px, calc((100vw - 1120px) / 2));
  background: white;
  border-bottom: 1px solid var(--line);
}
.band > *,
.topic > * {
  max-width: 1120px;
  margin-left: auto;
  margin-right: auto;
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
.topic-nav {
  position: sticky;
  top: 0;
  z-index: 3;
  background: #f7fbff;
  box-shadow: 0 8px 18px rgba(23, 32, 51, .08);
}
.topic-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}
.topic-nav a {
  display: flex;
  gap: 8px;
  align-items: center;
  min-width: 0;
  padding: 8px 10px;
  color: var(--ink);
  text-decoration: none;
  background: #ffffff;
  border: 1px solid var(--line);
}
.topic-nav span {
  flex: 0 0 auto;
  color: var(--red);
  font-weight: 800;
}
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
  .topic-nav { position: static; }
}
@media print {
  body { background: white; }
  .cover { min-height: 270mm; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .band, .topic { break-inside: avoid; padding: 22px 10mm; }
  a { color: inherit; text-decoration: none; }
}
"""
