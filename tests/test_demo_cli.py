import json

from intl_exam_guide.cli import main


def test_demo_cli_generates_offline_guide(tmp_path):
    output_dir = tmp_path / "demo"
    result = main(["demo", "--out", str(output_dir), "--skip-pdf"])
    assert result == 0
    assert (output_dir / "guide.html").exists()
    assert (output_dir / "guide-plan.json").exists()
    assert (output_dir / "qualification.json").exists()
    html = (output_dir / "guide.html").read_text(encoding="utf-8")
    assert html.count('class="topic-diagram"') == 3
    assert "Concept map / 图文解释" in html
    assert "practice card" in html
    assert "Public solution steps" in html
    assert "Answer checkpoints" in html
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["qualification"] == "International GCSE Demo Science (9000)"
    assert validation["issues"] == []
