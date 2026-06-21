from intl_exam_guide.models import Topic
from intl_exam_guide.planning.explanation_styles import (
    styled_explanation,
    styled_explanation_en,
)


def test_english_explanation_styles_cover_all_public_branches():
    topic = Topic(title="Market forces")
    expected_fragments = {
        "formal": "command word",
        "life": "real situation",
        "story": "short story",
        "detective": "case-solving tool",
        "adventure": "learning mission",
        "friendly": "core task",
    }

    first_lines = []
    for style, fragment in expected_fragments.items():
        lines = styled_explanation_en(topic, "demand shift", "unit", style)

        assert len(lines) == 4
        assert fragment in lines[0]
        assert "demand shift" in " ".join(lines)
        first_lines.append(lines[0])

    assert len(set(first_lines)) == len(expected_fragments)


def test_styled_explanation_delegates_english_output_to_english_styles():
    topic = Topic(title="Ledger entries")

    assert styled_explanation(
        topic,
        "source document",
        "unit",
        "detective",
        "en",
    ) == styled_explanation_en(topic, "source document", "unit", "detective")


def test_chinese_explanation_styles_cover_all_public_branches_without_bilingual_fallback():
    topic = Topic(title="A2 Ledger entries")
    styles = ["formal", "life", "story", "detective", "adventure", "friendly"]

    outputs = {
        style: styled_explanation(
            topic,
            "source document",
            "unit",
            style,
            "zh-CN",
        )
        for style in styles
    }

    for lines in outputs.values():
        joined = " ".join(lines)
        assert len(lines) == 4
        assert "source document" in joined
        assert "This unit asks" not in joined
        assert "learning mission" not in joined

    assert len({lines[0] for lines in outputs.values()}) == len(styles)
