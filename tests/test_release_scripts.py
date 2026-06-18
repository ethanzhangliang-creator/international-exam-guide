import json
import subprocess
import sys
from pathlib import Path


SAMPLES = {
    "mathematics-9260-sample": (90, 180, 39),
    "economics-9214-sample": (38, 76, 38),
    "chemistry-9202-sample": (35, 70, 18),
}


def test_verify_release_samples_allows_pending_assets(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=False)

    result = run_verify(outputs, "--allow-pending")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert sum(item["pending_infographics"] for item in payload["samples"]) == 95
    assert all(item["has_pdf"] is False for item in payload["samples"])


def test_verify_release_samples_fails_final_when_assets_are_pending(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=False)

    result = run_verify(outputs)

    assert result.returncode == 1
    assert "missing guide.pdf" in result.stderr
    assert "infographic asset(s) still pending" in result.stderr


def test_verify_release_samples_passes_completed_outputs(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=True)

    result = run_verify(outputs)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert sum(item["generated_infographics"] for item in payload["samples"]) == 95
    assert all(item["pending_infographics"] == 0 for item in payload["samples"])
    assert all(item["has_pdf"] is True for item in payload["samples"])


def test_verify_release_samples_rejects_mixed_language_slash_labels(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=True)
    html_path = outputs / "chemistry-9202-sample" / "guide.html"
    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(html + "<p>Learning guide / 学习手册</p>", encoding="utf-8")

    result = run_verify(outputs)

    assert result.returncode == 1
    assert "mixed-language label remains" in result.stderr


def test_import_infographic_assets_updates_manifest(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001_custom.png").write_bytes(b"fake-png")
    (asset_dir / "visual_002.png").write_bytes(b"fake-png")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {"id": "visual_001", "complexity": "infographic", "asset_status": "external-generation-required", "file": None},
                {"id": "visual_002", "complexity": "infographic", "asset_status": "external-generation-required", "file": None},
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir, "--provider", "test-provider")

    assert result.returncode == 0
    manifest = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))
    assert [entry["asset_status"] for entry in manifest] == ["manual-generated", "manual-generated"]
    assert [entry["generated_by"] for entry in manifest] == ["test-provider", "test-provider"]
    assert (images_dir / "visual_001_custom.png").exists()
    assert (images_dir / "visual_002.png").exists()


def test_import_infographic_assets_fails_when_required_asset_missing(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001.png").write_bytes(b"fake-png")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {"id": "visual_001", "complexity": "infographic", "asset_status": "external-generation-required", "file": None},
                {"id": "visual_002", "complexity": "infographic", "asset_status": "external-generation-required", "file": None},
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 1
    assert "visual_002" in result.stderr


def test_generate_pending_infographics_router_dry_run_plans_pending_assets(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True)
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "topic_title": "Example infographic",
                    "complexity": "infographic",
                    "asset_status": "external-generation-required",
                    "file": None,
                    "prompt": "Create a clean learning infographic.",
                },
                {
                    "id": "visual_002",
                    "topic_title": "SVG example",
                    "complexity": "svg-basic",
                    "asset_status": "generated",
                    "file": "visual_002.svg",
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_router_dry_run(output_dir)

    assert result.returncode == 0
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["requested"] == 1
    assert payload["planned"] == 1
    assert payload["size"] == "1536x1024"
    assert payload["quality"] == "high"


def test_scan_for_raw_keys_does_not_print_secret_value(tmp_path):
    secret = "sk-" + "A" * 30
    (tmp_path / "leaky.txt").write_text(f"token={secret}\n", encoding="utf-8")

    result = run_key_scan(tmp_path)

    assert result.returncode == 1
    assert "raw_key_matches" in result.stdout
    assert "leaky.txt" in result.stdout
    assert secret not in result.stdout
    assert secret not in result.stderr


def test_scan_for_raw_keys_passes_clean_tree(tmp_path):
    (tmp_path / "clean.txt").write_text("no secret here\n", encoding="utf-8")

    result = run_key_scan(tmp_path)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["raw_key_matches"] == 0


def test_render_intro_animation_exposes_cli_help():
    result = run_render_intro_help()

    assert result.returncode == 0
    assert "--html" in result.stdout
    assert "--mp4" in result.stdout
    assert "--gif" in result.stdout


def test_skill_instructions_include_required_preflight_choices():
    skill_path = Path(__file__).resolve().parents[1] / "skill" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")

    assert text.startswith("---\n")
    assert "name: igcse-a-level-revision-guide" in text
    assert "description:" in text
    assert "Subject choice" in text
    assert "Output language" in text
    assert "Exam year when needed" in text
    assert "Explanation style" in text
    assert "Do not ask the user to choose an image model before the base guide is generated" in text
    assert "how many complex infographic" in text
    assert "SVG fallback" in text
    assert "This is a required language lock, not a bilingual mode" in text
    assert "Do not offer a" in text
    assert "combined bilingual output" in text


def run_verify(outputs: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_release_samples.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--outputs-root",
            str(outputs),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_key_scan(root: Path) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "scan_for_raw_keys.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(root),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_import(output_dir: Path, asset_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "import_infographic_assets.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(output_dir),
            "--asset-dir",
            str(asset_dir),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_router_dry_run(output_dir: Path) -> subprocess.CompletedProcess[str]:
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "generate_pending_infographics_router.py"
    )
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(output_dir),
            "--size",
            "1536x1024",
            "--quality",
            "high",
            "--output-format",
            "png",
            "--dry-run",
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_render_intro_help() -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "render_intro_animation.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--help",
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def write_sample_outputs(outputs: Path, completed: bool) -> None:
    for sample, (topics, practice_cards, infographics) in SAMPLES.items():
        sample_dir = outputs / sample
        images_dir = sample_dir / "images"
        images_dir.mkdir(parents=True)

        (sample_dir / "run-options.json").write_text(
            json.dumps({"output_language": "en"}, indent=2),
            encoding="utf-8",
        )
        (sample_dir / "validation.json").write_text(
            json.dumps(
                {
                    "review_summary": {
                        "topics": topics,
                        "practice_cards": practice_cards,
                    },
                    "issues": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        manifest = []
        html_images = []
        for index in range(1, infographics + 1):
            if completed:
                filename = f"visual_{index:03d}.png"
                (images_dir / filename).write_bytes(b"fake-png")
                status = "codex-router-generated"
                html_images.append(f'<img src="images/{filename}" alt="visual {index}">')
            else:
                filename = None
                status = "external-generation-required"
            manifest.append(
                {
                    "id": f"visual_{index:03d}",
                    "complexity": "infographic",
                    "asset_status": status,
                    "file": filename,
                }
            )
        (images_dir / "visual_manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        pending = "" if completed else "<section>Infographic Queue</section>"
        (sample_dir / "guide.html").write_text(
            f"<html lang=\"en\"><body><h1>{sample}</h1>{''.join(html_images)}{pending}</body></html>",
            encoding="utf-8",
        )
        if completed:
            (sample_dir / "guide.pdf").write_bytes(b"%PDF-1.4\n")
