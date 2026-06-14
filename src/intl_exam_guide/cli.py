from __future__ import annotations

import argparse
import json
import sys
from importlib import resources
from pathlib import Path

from intl_exam_guide.models import Qualification
from intl_exam_guide.planning.guide_plan import build_guide_plan
from intl_exam_guide.providers.oxfordaqa import OxfordAQAProvider
from intl_exam_guide.rendering.html import render_html
from intl_exam_guide.rendering.pdf import export_pdf
from intl_exam_guide.validation.checks import issues_to_dict, review_summary, validate_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="intl-exam-guide")
    subcommands = parser.add_subparsers(dest="command", required=True)

    discover = subcommands.add_parser("discover", help="List OxfordAQA subject pages or qualifications.")
    discover.add_argument("--subject-url", help="Optional OxfordAQA subject page URL.")

    generate = subcommands.add_parser("generate", help="Generate a revision guide.")
    generate.add_argument("--query", required=True, help="Subject name, code, slug, or qualification URL.")
    generate.add_argument(
        "--level",
        choices=["gcse", "igcse", "a-level", "alevel", "as-a-level"],
        help="Qualification level.",
    )
    generate.add_argument("--out", required=True, help="Output directory.")
    generate.add_argument("--questions-per-topic", type=int, default=2)
    generate.add_argument("--skip-pdf", action="store_true")

    demo = subcommands.add_parser("demo", help="Generate an offline synthetic demo guide.")
    demo.add_argument("--out", required=True, help="Output directory.")
    demo.add_argument("--questions-per-topic", type=int, default=2)
    demo.add_argument("--skip-pdf", action="store_true")

    args = parser.parse_args(argv)
    provider = OxfordAQAProvider()

    if args.command == "discover":
        if args.subject_url:
            for item in provider.list_qualifications(args.subject_url):
                print(
                    "\t".join(
                        [
                            item.text,
                            item.qualification_type or "unknown",
                            item.subject_heading or "",
                            item.group_label or "",
                            item.href,
                        ]
                    )
                )
        else:
            for item in provider.discover_subject_pages():
                print(f"{item.text}\t{item.href}")
        return 0

    if args.command == "generate":
        out_dir = Path(args.out)
        source_dir = out_dir / "source"
        out_dir.mkdir(parents=True, exist_ok=True)

        link = provider.find_qualification(args.query, args.level)
        qualification = provider.parse_qualification(link.href)
        qualification = provider.apply_listing_metadata(qualification, link)
        qualification = provider.download_specification(qualification, source_dir)
        return write_guide_outputs(qualification, out_dir, args.questions_per_topic, args.skip_pdf)

    if args.command == "demo":
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        qualification = load_demo_qualification()
        return write_guide_outputs(qualification, out_dir, args.questions_per_topic, args.skip_pdf)

    return 2


def load_demo_qualification() -> Qualification:
    data = json.loads(
        resources.files("intl_exam_guide")
        .joinpath("assets/demo_qualification.json")
        .read_text(encoding="utf-8")
    )
    return Qualification.from_dict(data)


def write_guide_outputs(
    qualification: Qualification,
    out_dir: Path,
    questions_per_topic: int,
    skip_pdf: bool,
) -> int:
    plan = build_guide_plan(qualification, questions_per_topic=questions_per_topic)

    qualification_path = out_dir / "qualification.json"
    plan_path = out_dir / "guide-plan.json"
    html_path = out_dir / "guide.html"
    pdf_path = out_dir / "guide.pdf"
    validation_path = out_dir / "validation.json"

    qualification_path.write_text(
        json.dumps(qualification.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    plan_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    render_html(plan, html_path)

    pdf_error: str | None = None
    if not skip_pdf:
        try:
            export_pdf(html_path, pdf_path)
        except Exception as exc:  # pragma: no cover - depends on local browser
            pdf_error = str(exc)

    issues = validate_plan(plan, html_path=html_path, pdf_path=None if skip_pdf else pdf_path)
    payload = {
        "qualification": qualification.title,
        "html": str(html_path),
        "pdf": str(pdf_path) if pdf_path.exists() else None,
        "pdf_error": pdf_error,
        "review_summary": review_summary(
            plan,
            html_path=html_path,
            pdf_path=None if skip_pdf else pdf_path,
        ),
        "issues": issues_to_dict(issues),
    }
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
