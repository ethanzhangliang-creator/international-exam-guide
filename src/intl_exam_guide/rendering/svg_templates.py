from __future__ import annotations

import html
import re

from intl_exam_guide.models import VisualBrief


def render_topic_visual_svg(visual: VisualBrief, index: int, language: str = "en") -> str:
    if language == "zh-CN":
        return render_zh_visual_svg(visual, index)
    text = visual.visual_type.lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    if any(word in text for word in ["ledger", "book-of-prime-entry", "source-document", "accounting process"]):
        return render_accounting_flow_svg(index, "en")
    if any(word in text for word in ["reconciliation", "verification", "trial balance"]):
        return render_reconciliation_svg(index, "en")
    if any(word in text for word in ["financial-statement", "financial statement", "ratio-analysis", "ratio analysis"]):
        return render_financial_statement_svg(index, "en")
    if any(word in text for word in ["demand-supply", "demand supply", "market scenario"]):
        return render_market_svg(index, "en")
    if any(word in text for word in ["factors of production", "production-chain", "opportunity-cost", "opportunity cost"]):
        return render_economic_flow_svg(index, "en")
    if any(word in text for word in ["set notation", "venn"]):
        return render_venn_svg(index, "en")
    if any(word in text for word in ["force and motion", "force arrows"]):
        return render_force_svg(index, "en")
    if any(word in text for word in ["gas tests", "common gas"]):
        return render_gas_tests_svg(index, "en")
    if any(word in tokens for word in ["acid", "acids", "base", "bases", "salt", "salts", "ph"]):
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
    if any(word in text for word in ["distance-time", "motion graph"]):
        return render_motion_svg(index)
    if any(word in text for word in ["rate", "equilibrium"]):
        return render_rate_svg(index)
    if any(word in text for word in ["energy", "exothermic", "endothermic"]):
        return render_energy_svg(index)
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
    if any(word in text for word in ["data table", "graph interpretation"]):
        return render_statistics_svg(index)
    return render_concept_fallback_svg(index, visual.visual_type or "Study visual")


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

def render_accounting_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("原始凭证", "日记账", "分类账", "试算平衡")
        if zh
        else ("Source document", "Prime entry", "Ledger", "Trial balance")
    )
    title = "会计记录流程" if zh else "Accounting records flow"
    return render_flow_svg(index, title, labels, "#1354a5", "#1f7a5b")


def render_reconciliation_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("现金账", "银行对账单", "差异项目", "调整后余额")
        if zh
        else ("Cash book", "Bank statement", "Timing items", "Adjusted balance")
    )
    title = "核对与调节流程" if zh else "Verification and reconciliation"
    return render_flow_svg(index, title, labels, "#1f7a5b", "#d99a24")


def render_financial_statement_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "财务报表结构" if zh else "Financial statement layout"
    labels = (
        ("收入", "成本", "利润", "资产", "负债", "资本")
        if zh
        else ("Revenue", "Cost", "Profit", "Assets", "Liabilities", "Capital")
    )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="64" y="104" width="260" height="198" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="396" y="104" width="260" height="198" rx="14" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <text x="88" y="142" font-size="20" font-weight="800" fill="#b83246">{html_escape(labels[0])}</text>
  <text x="88" y="182" font-size="20" font-weight="800" fill="#172033">- {html_escape(labels[1])}</text>
  <path d="M88 205h190" stroke="#d7deea" stroke-width="4"/>
  <text x="88" y="246" font-size="22" font-weight="800" fill="#1f7a5b">= {html_escape(labels[2])}</text>
  <text x="420" y="142" font-size="20" font-weight="800" fill="#1354a5">{html_escape(labels[3])}</text>
  <text x="420" y="184" font-size="20" font-weight="800" fill="#b83246">- {html_escape(labels[4])}</text>
  <path d="M420 205h190" stroke="#d7deea" stroke-width="4"/>
  <text x="420" y="246" font-size="22" font-weight="800" fill="#1f7a5b">= {html_escape(labels[5])}</text>
</svg>
"""


def render_market_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "市场供需图" if zh else "Demand and supply market diagram"
    demand = "需求" if zh else "Demand"
    supply = "供给" if zh else "Supply"
    price = "价格" if zh else "Price"
    qty = "数量" if zh else "Quantity"
    equilibrium = "均衡" if zh else "Equilibrium"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <path d="M118 284V92M118 284h470" stroke="#172033" stroke-width="4"/>
  <path d="M150 118L548 260" stroke="#b83246" stroke-width="6"/>
  <path d="M150 260L548 118" stroke="#1f7a5b" stroke-width="6"/>
  <circle cx="350" cy="188" r="10" fill="#d99a24"/>
  <path d="M350 188v96M118 188h232" stroke="#d99a24" stroke-width="3" stroke-dasharray="7 6"/>
  <text x="555" y="266" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)}</text>
  <text x="552" y="126" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)}</text>
  <text x="132" y="96" font-size="17" font-weight="800">{html_escape(price)}</text>
  <text x="520" y="314" font-size="17" font-weight="800">{html_escape(qty)}</text>
  <text x="366" y="184" font-size="17" font-weight="800" fill="#9b6a10">{html_escape(equilibrium)}</text>
</svg>
"""


def render_economic_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("选择", "资源限制", "机会成本", "经济结果")
        if zh
        else ("Choice", "Scarce resources", "Opportunity cost", "Economic outcome")
    )
    title = "经济选择流程" if zh else "Economic choice flow"
    return render_flow_svg(index, title, labels, "#d99a24", "#1354a5")


def render_venn_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "集合与韦恩图" if zh else "Set notation and Venn regions"
    union = "并集" if zh else "Union"
    intersect = "交集" if zh else "Intersection"
    outside = "补集" if zh else "Complement"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="86" y="104" width="360" height="198" rx="16" fill="#f7fbff" stroke="#172033" stroke-width="3"/>
  <circle cx="228" cy="200" r="82" fill="#1354a5" fill-opacity=".35" stroke="#1354a5" stroke-width="4"/>
  <circle cx="310" cy="200" r="82" fill="#b83246" fill-opacity=".32" stroke="#b83246" stroke-width="4"/>
  <text x="178" y="202" font-size="22" font-weight="800">A</text>
  <text x="350" y="202" font-size="22" font-weight="800">B</text>
  <text x="250" y="205" font-size="18" font-weight="800" fill="#172033">A ∩ B</text>
  <rect x="488" y="118" width="150" height="46" rx="10" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="488" y="178" width="150" height="46" rx="10" fill="#fff1f3" stroke="#e5aab4"/>
  <rect x="488" y="238" width="150" height="46" rx="10" fill="#fffaf1" stroke="#d99a24"/>
  <text x="508" y="148" font-size="18" font-weight="800" fill="#1354a5">{html_escape(union)}</text>
  <text x="508" y="208" font-size="18" font-weight="800" fill="#b83246">{html_escape(intersect)}</text>
  <text x="508" y="268" font-size="18" font-weight="800" fill="#9b6a10">{html_escape(outside)}</text>
</svg>
"""


def render_force_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "力与运动示意图" if zh else "Force and motion diagram"
    force = "合力" if zh else "resultant force"
    accel = "加速度方向" if zh else "acceleration"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="258" y="152" width="170" height="88" rx="16" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M248 196h-126" stroke="#b83246" stroke-width="7" marker-end="url(#force-left-{index})"/>
  <path d="M438 196h164" stroke="#1f7a5b" stroke-width="9" marker-end="url(#force-right-{index})"/>
  <defs>
    <marker id="force-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="force-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
  </defs>
  <text x="284" y="204" font-size="22" font-weight="800">object</text>
  <text x="110" y="164" font-size="17" font-weight="800" fill="#b83246">smaller force</text>
  <text x="452" y="164" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(force)}</text>
  <text x="452" y="274" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(accel)} →</text>
</svg>
"""


def render_gas_tests_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "气体检验观察图" if zh else "Common gas tests observation chart"
    headers = (
        ("气体", "检验", "观察")
        if zh
        else ("Gas", "Test", "Observation")
    )
    rows = (
        (("氧气", "带火星木条", "复燃"), ("氢气", "燃着木条", "爆鸣"), ("二氧化碳", "石灰水", "变浑浊"))
        if zh
        else (("Oxygen", "glowing splint", "relights"), ("Hydrogen", "lit splint", "squeaky pop"), ("CO₂", "limewater", "turns cloudy"))
    )
    row_svg = []
    for row_index, row in enumerate(rows):
        y = 130 + row_index * 56
        row_svg.append(f'<rect x="70" y="{y - 30}" width="580" height="48" fill="#fbfcff" stroke="#d7deea"/>')
        row_svg.append(f'<text x="92" y="{y}" font-size="17" font-weight="800" fill="#1354a5">{html_escape(row[0])}</text>')
        row_svg.append(f'<text x="258" y="{y}" font-size="17" fill="#172033">{html_escape(row[1])}</text>')
        row_svg.append(f'<text x="486" y="{y}" font-size="17" fill="#1f7a5b">{html_escape(row[2])}</text>')
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <text x="92" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[0])}</text>
  <text x="258" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[1])}</text>
  <text x="486" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[2])}</text>
  {''.join(row_svg)}
</svg>
"""


def render_flow_svg(
    index: int,
    title: str,
    labels: tuple[str, str, str, str],
    primary: str,
    secondary: str,
) -> str:
    cards = []
    for position, label in enumerate(labels):
        x = 64 + position * 160
        color = primary if position % 2 == 0 else secondary
        cards.append(
            f'<rect x="{x}" y="138" width="124" height="84" rx="14" fill="#ffffff" stroke="{color}" stroke-width="4"/>'
            f'<text x="{x + 62}" y="188" font-size="16" font-weight="800" fill="{color}" text-anchor="middle">{html_escape(label)}</text>'
        )
        if position < 3:
            ax = x + 132
            cards.append(
                f'<path d="M{ax} 180h38" stroke="#172033" stroke-width="4" marker-end="url(#flow-arrow-{index})"/>'
            )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="78" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <defs><marker id="flow-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {''.join(cards)}
</svg>
"""


def render_concept_fallback_svg(index: int, title: str) -> str:
    heading = title or "Study visual"
    labels = ("Key idea", "Question evidence", "Checked answer")
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(heading)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="76" font-size="24" font-weight="800" fill="#1354a5">{html_escape(heading[:48])}</text>
  <rect x="82" y="130" width="158" height="96" rx="16" fill="#edf4ff" stroke="#9cbce8" stroke-width="3"/>
  <rect x="282" y="130" width="158" height="96" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="482" y="130" width="158" height="96" rx="16" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <path d="M246 178h30M446 178h30" stroke="#172033" stroke-width="4" marker-end="url(#concept-arrow-{index})"/>
  <defs><marker id="concept-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="161" y="184" font-size="18" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(labels[0])}</text>
  <text x="361" y="184" font-size="18" font-weight="800" fill="#9b6a10" text-anchor="middle">{html_escape(labels[1])}</text>
  <text x="561" y="184" font-size="18" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(labels[2])}</text>
</svg>
"""


def render_zh_visual_svg(visual: VisualBrief, index: int) -> str:
    title = visual.visual_type or "图文结合学习图"
    text = title.lower()
    if any(word in text for word in ["会计记录", "原始", "分类账", "初始记录"]):
        return render_accounting_flow_svg(index, "zh-CN")
    if any(word in text for word in ["核对", "银行对账", "试算平衡"]):
        return render_reconciliation_svg(index, "zh-CN")
    if any(word in text for word in ["财务报表", "比率"]):
        return render_financial_statement_svg(index, "zh-CN")
    if any(word in text for word in ["会计调整", "影响"]):
        return render_accounting_flow_svg(index, "zh-CN")
    if any(word in text for word in ["市场", "曲线", "供需"]):
        return render_market_svg(index, "zh-CN")
    if any(word in text for word in ["生产要素", "机会成本", "经济选择"]):
        return render_economic_flow_svg(index, "zh-CN")
    if any(word in text for word in ["集合", "韦恩"]):
        return render_venn_svg(index, "zh-CN")
    if any(word in text for word in ["力与运动", "合力"]):
        return render_force_svg(index, "zh-CN")
    if any(word in text for word in ["气体检验", "气体"]):
        return render_gas_tests_svg(index, "zh-CN")
    if any(word in text for word in ["粒子"]):
        return render_particles_svg(index)
    if any(word in text for word in ["酸碱", "ph"]):
        return render_ph_svg(index)
    if any(word in text for word in ["几何"]):
        return render_triangle_svg(index)
    if any(word in text for word in ["统计", "概率"]):
        return render_statistics_svg(index)
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

def html_escape(value: str) -> str:
    return html.escape(value, quote=True)
