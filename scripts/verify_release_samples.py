from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SAMPLES = {
    "mathematics-9260-sample": {
        "topics": 90,
        "practice_cards": 180,
        "infographics": 39,
        "language": "en",
    },
    "economics-9214-sample": {
        "topics": 38,
        "practice_cards": 76,
        "infographics": 38,
        "language": "en",
    },
    "chemistry-9202-sample": {
        "topics": 35,
        "practice_cards": 70,
        "infographics": 18,
        "language": "en",
    },
}

GENERATED_STATUSES = {
    "generated",
    "reviewed",
    "reviewed-generated",
    "provider-selected-generated",
    "manual-generated",
    "codex-router-generated",
}
PENDING_STATUSES = {
    "external-generation-required",
    "provider-selected-pending-generation",
    "infographic-provider-required",
}
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
BAD_MIXED_LABELS = [
    "Chinese / English",
    "中文 / English",
    "图文学习页 / Visual Guide",
    "复习路线 / Study Roadmap",
    "例题 / Worked Example",
]
MIXED_LANGUAGE_SLASH_PATTERN = re.compile(
    r"(?:[\u4e00-\u9fff][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[A-Za-z]"
    r"|[A-Za-z][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[\u4e00-\u9fff])"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release sample guide completeness.")
    parser.add_argument(
        "--outputs-root",
        default="./outputs",
        help="Directory containing mathematics/economics/chemistry sample outputs.",
    )
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Allow pending infographic assets. Use only before final image generation.",
    )
    args = parser.parse_args()

    outputs_root = Path(args.outputs_root).resolve()
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for sample, expected in SAMPLES.items():
        row, sample_failures = verify_sample(outputs_root / sample, sample, expected, args.allow_pending)
        rows.append(row)
        failures.extend(sample_failures)

    print(json.dumps({"outputs_root": str(outputs_root), "samples": rows}, ensure_ascii=False, indent=2))
    if failures:
        print("\nRelease sample verification failed:", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    return 0


def verify_sample(
    sample_dir: Path,
    sample: str,
    expected: dict[str, int | str],
    allow_pending: bool,
) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    validation_path = sample_dir / "validation.json"
    run_options_path = sample_dir / "run-options.json"
    manifest_path = sample_dir / "images" / "visual_manifest.json"
    html_path = sample_dir / "guide.html"
    pdf_path = sample_dir / "guide.pdf"

    required_files = [validation_path, run_options_path, manifest_path, html_path]
    if not allow_pending:
        required_files.append(pdf_path)
    for path in required_files:
        if not path.exists():
            failures.append(f"{sample}: missing {path.name}")

    validation = read_json(validation_path, {})
    run_options = read_json(run_options_path, {})
    manifest = read_json(manifest_path, [])
    html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
    review = validation.get("review_summary", {}) if isinstance(validation, dict) else {}
    issues = validation.get("issues", []) if isinstance(validation, dict) else []
    issue_errors = [issue for issue in issues if issue.get("severity") == "error"]
    if issue_errors:
        failures.append(f"{sample}: validation has {len(issue_errors)} error issue(s)")

    if review.get("topics") != expected["topics"]:
        failures.append(f"{sample}: expected {expected['topics']} topics, got {review.get('topics')}")
    if review.get("practice_cards") != expected["practice_cards"]:
        failures.append(
            f"{sample}: expected {expected['practice_cards']} practice cards, got {review.get('practice_cards')}"
        )
    if run_options.get("output_language") != expected["language"]:
        failures.append(
            f"{sample}: expected language {expected['language']}, got {run_options.get('output_language')}"
        )
    duplicate_topics = count_duplicate_practice_topics(validation)
    if duplicate_topics:
        failures.append(f"{sample}: {duplicate_topics} topic(s) have duplicate practice questions")

    generated, pending, missing_files = count_infographics(sample_dir / "images", manifest)
    if pending and not allow_pending:
        failures.append(f"{sample}: {pending} infographic asset(s) still pending")
    if generated != expected["infographics"] and not allow_pending:
        failures.append(
            f"{sample}: expected {expected['infographics']} generated infographics, got {generated}"
        )
    if missing_files:
        failures.append(f"{sample}: {missing_files} manifest image file(s) are missing")

    broken_images = count_broken_html_images(sample_dir, html)
    if broken_images:
        failures.append(f"{sample}: {broken_images} HTML image(s) reference missing files")
    if not allow_pending and "Infographic Queue" in html:
        failures.append(f"{sample}: HTML still contains pending Infographic Queue blocks")
    if expected["language"] == "en" and re.search(r"[\u4e00-\u9fff]", html):
        failures.append(f"{sample}: English HTML contains Chinese characters")
    for label in mixed_language_label_matches(html):
        failures.append(f"{sample}: mixed-language label remains: {label}")

    row = {
        "sample": sample,
        "topics": review.get("topics"),
        "practice_cards": review.get("practice_cards"),
        "language": run_options.get("output_language"),
        "generated_infographics": generated,
        "pending_infographics": pending,
        "missing_manifest_files": missing_files,
        "broken_html_images": broken_images,
        "has_html": html_path.exists(),
        "has_pdf": pdf_path.exists(),
        "validation_errors": len(issue_errors),
    }
    return row, failures


def read_json(path: Path, fallback: object) -> object:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def count_infographics(images_dir: Path, manifest: object) -> tuple[int, int, int]:
    if not isinstance(manifest, list):
        return 0, 0, 0
    generated = 0
    pending = 0
    missing = 0
    for entry in manifest:
        if not isinstance(entry, dict) or entry.get("complexity") != "infographic":
            continue
        status = str(entry.get("asset_status") or "")
        filename = str(entry.get("file") or "")
        is_raster = Path(filename).suffix.lower() in RASTER_EXTENSIONS
        exists = bool(filename) and (images_dir / filename).exists()
        if status in GENERATED_STATUSES and is_raster and exists:
            generated += 1
        elif status in PENDING_STATUSES or not exists:
            pending += 1
        if filename and not exists:
            missing += 1
    return generated, pending, missing


def count_broken_html_images(sample_dir: Path, html: str) -> int:
    broken = 0
    for match in re.finditer(r'<img[^>]+src="([^"]+)"', html):
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            continue
        if not (sample_dir / src).exists():
            broken += 1
    return broken


def count_duplicate_practice_topics(validation: object) -> int:
    if not isinstance(validation, dict):
        return 0
    # validation.json stores summary only, so inspect guide-plan.json next to it when available.
    html_value = validation.get("html")
    if not isinstance(html_value, str):
        return 0
    plan_path = Path(html_value).with_name("guide-plan.json")
    plan = read_json(plan_path, {})
    if not isinstance(plan, dict):
        return 0
    practice_items = plan.get("practice_items", [])
    if not isinstance(practice_items, list):
        return 0
    by_topic: dict[str, set[str]] = {}
    counts: dict[str, int] = {}
    for item in practice_items:
        if not isinstance(item, dict):
            continue
        topic = str(item.get("topic_title") or "")
        question = normalize_question(str(item.get("question") or ""))
        if not topic or not question:
            continue
        by_topic.setdefault(topic, set()).add(question)
        counts[topic] = counts.get(topic, 0) + 1
    return sum(1 for topic, count in counts.items() if len(by_topic.get(topic, set())) < count)


def normalize_question(question: str) -> str:
    question = re.sub(
        r"^(Case file: |Real-life prompt: |Warm-up prompt: |Exam-style prompt: |Story prompt: |Checkpoint challenge: )",
        "",
        question,
    )
    return re.sub(r"\s+", " ", question).strip().lower()


def mixed_language_label_matches(html: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", html)
    matches: list[str] = []
    for label in BAD_MIXED_LABELS:
        if label in html:
            matches.append(label)
    for match in MIXED_LANGUAGE_SLASH_PATTERN.finditer(text):
        label = " ".join(match.group(0).split())
        if label not in matches:
            matches.append(label)
    return matches


if __name__ == "__main__":
    raise SystemExit(main())
