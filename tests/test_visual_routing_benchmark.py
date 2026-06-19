from intl_exam_guide.models import Topic, VisualBrief
from intl_exam_guide.planning.guide_plan import choose_visual_type
from intl_exam_guide.planning.guide_plan import zh_visual_type
from intl_exam_guide.rendering.html import render_topic_visual_svg


def route(title: str, points: list[str], subject: str) -> tuple[str, str, str]:
    return choose_visual_type(Topic(title=title, points=points), points, subject)


def test_complex_subject_visuals_are_routed_to_infographic_queue():
    cases = [
        (
            "3.1 - Source documents and books of prime entry",
            ["source documents, books of prime entry, ledger accounts, double entry"],
            "Accounting",
            "ledger flow",
        ),
        (
            "2.1 - Markets and allocation of resources",
            ["demand, supply, equilibrium price, market changes"],
            "Economics",
            "demand-supply",
        ),
        (
            "8.3 - Gas tests",
            ["test for hydrogen, oxygen, carbon dioxide and chlorine using observations"],
            "Chemistry",
            "gas tests",
        ),
        (
            "4.1 - Set notation and Venn diagrams",
            ["use set notation including n(A), union, intersection and complement"],
            "Mathematics",
            "Venn",
        ),
        (
            "5.2 - Forces and motion",
            ["draw force arrows and explain acceleration in a real scenario"],
            "Physics",
            "force and motion",
        ),
    ]

    for title, points, subject, expected_phrase in cases:
        visual_type, complexity, trigger = route(title, points, subject)

        assert complexity == "infographic", (subject, visual_type, trigger)
        assert expected_phrase.lower() in visual_type.lower()


def test_simple_svg_routes_stay_subject_specific():
    cases = [
        (
            "1.2 - Ratio and proportion",
            ["use ratio notation and fractions on a number line"],
            "Mathematics",
            "number line",
            "Number line",
        ),
        (
            "6.1 - Right-angled triangles",
            ["use Pythagoras' theorem in a simple right-angled triangle"],
            "Mathematics",
            "triangle",
            "Right triangle",
        ),
        (
            "7.2 - Acids and alkalis",
            ["use the pH scale and describe neutralisation"],
            "Chemistry",
            "pH scale",
            "pH scale",
        ),
        (
            "3.4 - Distance-time graphs",
            ["interpret a distance-time graph"],
            "Physics",
            "distance-time",
            "Distance-time",
        ),
    ]

    for title, points, subject, visual_phrase, svg_title in cases:
        visual_type, complexity, _ = route(title, points, subject)
        svg = render_topic_visual_svg(
            VisualBrief(
                topic_title=title,
                focus_point=points[0],
                trigger="benchmark",
                visual_type=visual_type,
                complexity=complexity,
                image_provider="deterministic-svg",
                prompt="benchmark",
                source_points=points,
            ),
            index=1,
        )

        assert complexity == "svg-basic", (subject, visual_type)
        assert visual_phrase.lower() in visual_type.lower()
        assert svg_title in svg


def test_statistics_is_not_used_as_generic_fallback_for_unrelated_topics():
    unrelated_cases = [
        ("Accounting", "bank reconciliation", ["cash book, bank statement, unpresented cheques"]),
        ("Chemistry", "chromatography", ["separate dyes using chromatography and calculate Rf values"]),
        ("Economics", "opportunity cost", ["choices, scarcity, opportunity cost, trade-offs"]),
    ]

    for subject, title, points in unrelated_cases:
        visual_type, complexity, _ = route(title, points, subject)

        assert complexity == "infographic"
        assert "statistics" not in visual_type.lower()


def test_complex_svg_fallbacks_use_subject_templates():
    cases = [
        (
            "3.1 - Source documents and books of prime entry",
            ["source documents, books of prime entry, ledger accounts, double entry"],
            "Accounting",
            "Accounting records flow",
            "Prime entry",
        ),
        (
            "2.1 - Markets and allocation of resources",
            ["demand, supply, equilibrium price, market changes"],
            "Economics",
            "Demand and supply market diagram",
            "Equilibrium",
        ),
        (
            "4.1 - Set notation and Venn diagrams",
            ["use set notation including n(A), union, intersection and complement"],
            "Mathematics",
            "Set notation and Venn regions",
            "A ∩ B",
        ),
        (
            "8.3 - Gas tests",
            ["test for hydrogen, oxygen, carbon dioxide and chlorine using observations"],
            "Chemistry",
            "Common gas tests observation chart",
            "limewater",
        ),
        (
            "5.2 - Forces and motion",
            ["draw force arrows and explain acceleration in a real scenario"],
            "Physics",
            "Force and motion diagram",
            "resultant force",
        ),
    ]

    for title, points, subject, expected_title, expected_label in cases:
        visual_type, complexity, _ = route(title, points, subject)
        svg = render_topic_visual_svg(
            VisualBrief(
                topic_title=title,
                focus_point=points[0],
                trigger="benchmark",
                visual_type=visual_type,
                complexity=complexity,
                image_provider="external-generation-required",
                prompt="benchmark",
                source_points=points,
            ),
            index=1,
        )

        assert complexity == "infographic"
        assert expected_title in svg
        assert expected_label in svg
        assert "Particle model" not in svg


def test_chinese_visual_type_keeps_accounting_specific_route():
    visual_type, complexity, _ = route(
        "2.2 - Books of original entry",
        ["source documents, books of prime entry, ledger accounts"],
        "Accounting",
    )
    zh_type = zh_visual_type(visual_type)
    svg = render_topic_visual_svg(
        VisualBrief(
            topic_title="2.2 - Books of original entry",
            focus_point="原始凭证与初始记录账簿",
            trigger="benchmark",
            visual_type=zh_type,
            complexity=complexity,
            image_provider="external-generation-required",
            prompt="benchmark",
            source_points=["source documents"],
        ),
        index=1,
        language="zh-CN",
    )

    assert zh_type == "会计记录流程图"
    assert "会计记录流程" in svg
    assert "原始凭证" in svg
