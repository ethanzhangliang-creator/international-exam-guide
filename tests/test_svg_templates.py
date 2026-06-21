from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.svg_templates import (
    html_escape,
    render_accounting_flow_svg,
    render_algebra_svg,
    render_analysis_svg,
    render_bonding_svg,
    render_concept_fallback_svg,
    render_energy_svg,
    render_financial_statement_svg,
    render_flow_svg,
    render_force_svg,
    render_gas_tests_svg,
    render_market_svg,
    render_motion_svg,
    render_number_svg,
    render_organic_svg,
    render_particles_svg,
    render_ph_svg,
    render_rate_svg,
    render_reconciliation_svg,
    render_statistics_svg,
    render_topic_visual_svg,
    render_triangle_svg,
    render_zh_visual_svg,
    svg_multiline_text,
    wrap_words,
)


def visual(visual_type: str) -> VisualBrief:
    return VisualBrief(
        topic_title="Topic",
        focus_point="focus",
        trigger="trigger",
        visual_type=visual_type,
        complexity="svg-basic",
        image_provider="deterministic-svg",
        prompt="prompt",
        source_points=[],
    )


def assert_svg_contract(svg: str, title: str, index: int = 1) -> None:
    assert '<svg class="visual-svg"' in svg
    assert 'role="img"' in svg
    assert f'aria-labelledby="visual-title-{index}"' in svg
    assert f'<title id="visual-title-{index}">{title}</title>' in svg


def test_svg_topic_router_covers_english_subject_routes():
    route_expectations = [
        ("ledger flow diagram", "Accounting records flow"),
        ("bank reconciliation verification", "Verification and reconciliation"),
        ("financial statement ratio-analysis", "Financial statement layout"),
        ("demand-supply market scenario", "Demand and supply market diagram"),
        ("factors of production opportunity cost", "Economic choice flow"),
        ("set notation venn", "Set notation and Venn regions"),
        ("force and motion force arrows", "Force and motion diagram"),
        ("common gas tests", "Common gas tests observation chart"),
        ("acid base ph", "pH scale and salt preparation"),
        ("particle solid liquid atom", "Particle model diagram"),
        ("bond ionic covalent structure", "Bonding and structure diagram"),
        ("organic hydrocarbon carbon", "Hydrocarbon chain diagram"),
        ("chemical analysis chromatography", "Chromatography diagram"),
        ("distance-time motion graph", "Distance-time graph"),
        ("rate equilibrium", "Rate of reaction graph"),
        ("energy exothermic endothermic", "Reaction energy profile"),
        ("number line fraction ratio", "Number line, fraction bar, and ratio diagram"),
        ("function graph equation-balance algebra", "Function graph and equation balance"),
        ("statistics chart probability", "Statistics chart and probability visual"),
        ("geometry diagram triangle pythagoras", "Right triangle diagram"),
        ("data table graph interpretation", "Statistics chart and probability visual"),
    ]

    for index, (visual_type, expected_title) in enumerate(route_expectations, start=1):
        svg = render_topic_visual_svg(visual(visual_type), index, "en")
        assert_svg_contract(svg, expected_title, index)

    fallback = render_topic_visual_svg(visual("unmatched custom visual"), 99, "en")
    assert_svg_contract(fallback, "unmatched custom visual", 99)


def test_svg_topic_router_covers_chinese_subject_routes():
    route_expectations = [
        ("会计记录流程图", "会计记录流程"),
        ("银行对账核对图", "核对与调节流程"),
        ("财务报表比率图", "财务报表结构"),
        ("会计调整影响图", "会计记录流程"),
        ("市场供需曲线", "市场供需图"),
        ("生产要素和机会成本", "经济选择流程"),
        ("集合韦恩图", "集合与韦恩图"),
        ("力与运动合力", "力与运动示意图"),
        ("气体检验观察", "气体检验观察图"),
        ("粒子模型", "Particle model diagram"),
        ("酸碱 pH", "pH scale and salt preparation"),
        ("几何三角形", "Right triangle diagram"),
        ("统计概率图", "Statistics chart and probability visual"),
    ]

    for index, (visual_type, expected_title) in enumerate(route_expectations, start=1):
        svg = render_topic_visual_svg(visual(visual_type), index, "zh-CN")
        assert_svg_contract(svg, expected_title, index)

    fallback = render_zh_visual_svg(visual("复杂自定义图文学习图"), 77)
    assert_svg_contract(fallback, "中文图文学习图", 77)
    assert "复杂自定义图文学习图" in fallback


def test_direct_svg_helpers_escape_titles_and_keep_core_labels():
    assert "Accounting records flow" in render_accounting_flow_svg(1, "en")
    assert "Verification and reconciliation" in render_reconciliation_svg(1, "en")
    assert "Financial statement layout" in render_financial_statement_svg(1, "en")
    assert "Demand and supply market diagram" in render_market_svg(1, "en")
    assert "Force and motion diagram" in render_force_svg(1, "en")
    assert "Common gas tests observation chart" in render_gas_tests_svg(1, "en")
    assert "Number sense" in render_number_svg(1)
    assert "Algebra links symbols to shapes" in render_algebra_svg(1)
    assert "Data becomes evidence" in render_statistics_svg(1)
    assert "Particle model" in render_particles_svg(1)
    assert "Right triangle diagram" in render_triangle_svg(1)
    assert "Distance-time graph" in render_motion_svg(1)
    assert "Rate of reaction graph" in render_rate_svg(1)
    assert "Reaction energy profile" in render_energy_svg(1)
    assert "pH scale" in render_ph_svg(1)
    assert "hydrocarbon model" in render_organic_svg(1)
    assert "Chromatography diagram" in render_analysis_svg(1)
    assert "bonding model" in render_bonding_svg(1)
    assert "Economic choice flow" in render_flow_svg(
        1,
        "Economic choice flow",
        ("Choice", "Scarce resources", "Opportunity cost", "Outcome"),
        "#111111",
        "#222222",
    )

    escaped = render_concept_fallback_svg(2, "A&B <topic>")
    assert "A&amp;B &lt;topic&gt;" in escaped
    assert "Key idea" in escaped
    assert html_escape('"quoted" & <tag>') == "&quot;quoted&quot; &amp; &lt;tag&gt;"


def test_svg_text_wrapping_helpers_are_deterministic():
    assert wrap_words("alpha beta gamma", max_chars=10) == ["alpha beta", "gamma"]
    assert wrap_words("abcdefghijkl", max_chars=5) == ["abcde"]
    assert wrap_words("alpha/beta gamma", max_chars=10) == ["alpha /", "beta gamma"]
    assert wrap_words("", max_chars=5) == [""]

    text = svg_multiline_text(
        "alpha beta gamma delta",
        x=10,
        y=20,
        max_chars=11,
        line_height=12,
        size=14,
        weight=600,
        fill="#000000",
    )

    assert '<text x="10" y="20" fill="#000000" font-size="14" font-weight="600">' in text
    assert '<tspan x="10" dy="0">alpha beta</tspan>' in text
    assert '<tspan x="10" dy="12">gamma delta</tspan>' in text

    truncated = svg_multiline_text(
        "one two three four five six seven eight nine ten",
        x=10,
        y=20,
        max_chars=8,
        line_height=12,
    )

    assert truncated.count("<tspan") == 3
    assert "seven" not in truncated
