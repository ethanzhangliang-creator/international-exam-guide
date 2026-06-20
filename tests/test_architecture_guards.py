from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_html_renderer_stays_below_monolith_limit():
    html_renderer = REPO_ROOT / "src" / "intl_exam_guide" / "rendering" / "html.py"

    line_count = len(html_renderer.read_text(encoding="utf-8").splitlines())

    assert line_count <= 1000


def test_svg_and_styles_are_split_out_of_html_renderer():
    rendering_dir = REPO_ROOT / "src" / "intl_exam_guide" / "rendering"

    assert (rendering_dir / "svg_templates.py").exists()
    assert (rendering_dir / "styles.py").exists()
    assert (rendering_dir / "infographics.py").exists()


def test_guide_plan_responsibilities_stay_split_out():
    planning_dir = REPO_ROOT / "src" / "intl_exam_guide" / "planning"
    guide_plan = planning_dir / "guide_plan.py"

    line_count = len(guide_plan.read_text(encoding="utf-8").splitlines())

    assert line_count <= 450
    assert (planning_dir / "visual_routing.py").exists()
    assert (planning_dir / "practice_generator.py").exists()
    assert (planning_dir / "explanation_styles.py").exists()
    assert (planning_dir / "localization.py").exists()


def test_practice_generator_stays_below_monolith_limit():
    practice_generator = (
        REPO_ROOT / "src" / "intl_exam_guide" / "planning" / "practice_generator.py"
    )

    line_count = len(practice_generator.read_text(encoding="utf-8").splitlines())

    assert line_count <= 1000
