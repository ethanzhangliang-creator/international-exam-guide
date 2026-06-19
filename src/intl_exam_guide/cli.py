from __future__ import annotations

import argparse
import json
import os
import sys
from importlib import resources
from pathlib import Path

from intl_exam_guide.models import Qualification
from intl_exam_guide.planning.guide_plan import (
    IMAGE_PROVIDERS,
    LANGUAGE_CHOICES,
    STYLE_LABELS,
    build_guide_plan,
)
from intl_exam_guide.providers import PROVIDER_NAMES, get_provider, infer_provider_from_url
from intl_exam_guide.rendering.handbook_package import write_handbook_package
from intl_exam_guide.rendering.html import render_html
from intl_exam_guide.rendering.pdf import PdfExportError, export_pdf
from intl_exam_guide.validation.checks import issues_to_dict, review_summary, validate_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="intl-exam-guide")
    subcommands = parser.add_subparsers(dest="command", required=True)

    discover = subcommands.add_parser("discover", help="List exam-board subject pages or qualifications.")
    discover.add_argument(
        "--provider",
        default="oxfordaqa",
        help=f"Exam board provider ({', '.join(PROVIDER_NAMES)}).",
    )
    discover.add_argument("--subject-url", help="Optional provider subject page URL.")

    generate = subcommands.add_parser("generate", help="Generate a revision guide.")
    generate.add_argument("--query", required=True, help="Subject name, code, slug, or qualification URL.")
    generate.add_argument(
        "--provider",
        default=None,
        help=f"Exam board provider ({', '.join(PROVIDER_NAMES)}). Inferred from --query URL when omitted.",
    )
    generate.add_argument(
        "--level",
        choices=["gcse", "igcse", "a-level", "alevel", "as-a-level"],
        help="Qualification level.",
    )
    generate.add_argument(
        "--exam-year",
        help="Exam year used by year-ranged syllabuses, especially Cambridge subject pages.",
    )
    generate.add_argument("--out", required=True, help="Output directory.")
    generate.add_argument("--questions-per-topic", type=int, default=2)
    add_generation_choice_args(generate)
    generate.add_argument("--skip-pdf", action="store_true")

    demo = subcommands.add_parser("demo", help="Generate an offline synthetic demo guide.")
    demo.add_argument("--out", required=True, help="Output directory.")
    demo.add_argument("--questions-per-topic", type=int, default=2)
    add_generation_choice_args(demo)
    demo.add_argument("--skip-pdf", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "discover":
        provider = get_provider(args.provider)
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
        validate_generation_choices(parser, args)
        provider = get_provider(resolve_provider(args.provider, args.query))
        out_dir = Path(args.out)
        source_dir = out_dir / "source"
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            link = provider.find_qualification(args.query, args.level, args.exam_year)
            qualification = provider.parse_qualification(link.href, args.level, args.exam_year)
            qualification = provider.apply_listing_metadata(qualification, link)
            qualification = provider.download_specification(qualification, source_dir, args.exam_year)
        except (ValueError, NotImplementedError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        return write_guide_outputs(
            qualification,
            out_dir,
            args.questions_per_topic,
            args.skip_pdf,
            args.image_provider,
            args.explanation_style,
            args.language,
            args.query,
            args.exam_year,
            args.image_model,
            args.image_endpoint_url,
            args.image_api_key_env,
        )

    if args.command == "demo":
        validate_generation_choices(parser, args)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        qualification = load_demo_qualification()
        return write_guide_outputs(
            qualification,
            out_dir,
            args.questions_per_topic,
            args.skip_pdf,
            args.image_provider,
            args.explanation_style,
            args.language,
            "demo science",
            None,
            args.image_model,
            args.image_endpoint_url,
            args.image_api_key_env,
        )

    return 2


def add_generation_choice_args(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--image-provider",
        default="prompt-queue",
        choices=sorted(IMAGE_PROVIDERS),
        help=(
            "Optional visual route. Defaults to prompt-queue, which writes source-bound "
            "visual briefs for complex infographics. Real image generation/import requires "
            "a callable external skill, API, script, asset directory, or custom provider."
        ),
    )
    command.add_argument(
        "--explanation-style",
        required=True,
        choices=sorted(STYLE_LABELS),
        help="User-selected writing style for topic explanations and worked examples.",
    )
    command.add_argument(
        "--language",
        required=True,
        choices=sorted(LANGUAGE_CHOICES),
        help="User-selected guide language. Template labels and generated explanations should not be bilingual.",
    )
    command.add_argument("--image-model", help="Model name when --image-provider custom.")
    command.add_argument("--image-endpoint-url", help="Custom image API endpoint URL.")
    command.add_argument(
        "--image-api-key-env",
        help="Environment variable name that stores the custom image API key. Do not pass raw keys.",
    )


def validate_generation_choices(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.image_provider != "custom":
        return
    missing = [
        flag
        for flag, value in [
            ("--image-model", args.image_model),
            ("--image-endpoint-url", args.image_endpoint_url),
            ("--image-api-key-env", args.image_api_key_env),
        ]
        if not value
    ]
    if missing:
        parser.error("--image-provider custom requires " + ", ".join(missing))
    if not os.environ.get(args.image_api_key_env):
        parser.error(
            "--image-provider custom requires environment variable "
            f"{args.image_api_key_env} to be set"
        )


def resolve_provider(provider: str | None, query: str) -> str:
    """Return provider name: explicit choice, URL inference, or OxfordAQA default."""
    if provider:
        return provider
    if query.lower().startswith(("http://", "https://")):
        return infer_provider_from_url(query) or "oxfordaqa"
    return "oxfordaqa"


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
    image_provider: str | None,
    explanation_style: str,
    output_language: str,
    requested_subject: str,
    exam_year: str | None,
    image_model: str | None,
    image_endpoint_url: str | None,
    image_api_key_env: str | None,
) -> int:
    plan = build_guide_plan(
        qualification,
        questions_per_topic=questions_per_topic,
        image_provider=image_provider,
        explanation_style=explanation_style,
        output_language=output_language,
        requested_subject=requested_subject,
        exam_year=exam_year,
        image_model=image_model,
        image_endpoint_url=image_endpoint_url,
        image_api_key_env=image_api_key_env,
    )

    qualification_path = out_dir / "qualification.json"
    plan_path = out_dir / "guide-plan.json"
    html_path = out_dir / "guide.html"
    pdf_path = out_dir / "guide.pdf"
    validation_path = out_dir / "validation.json"
    run_options_path = out_dir / "run-options.json"
    if pdf_path.exists():
        pdf_path.unlink()

    qualification_path.write_text(
        json.dumps(qualification.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    run_options_path.write_text(
        json.dumps(plan.run_options.__dict__, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    plan_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    package_manifest = write_handbook_package(plan, out_dir)
    render_html(plan, html_path, out_dir / "images" / "visual_manifest.json")

    pdf_error: str | None = None
    if not skip_pdf:
        try:
            export_pdf(html_path, pdf_path)
        except PdfExportError as exc:  # pragma: no cover - depends on local browser
            pdf_error = str(exc)

    issues = validate_plan(
        plan,
        html_path=html_path,
        pdf_path=None if skip_pdf else pdf_path,
        output_dir=out_dir,
    )
    payload = {
        "qualification": qualification.title,
        "html": str(html_path),
        "pdf": str(pdf_path) if pdf_path.exists() else None,
        "pdf_error": pdf_error,
        "package": package_manifest,
        "review_summary": review_summary(
            plan,
            html_path=html_path,
            pdf_path=None if skip_pdf else pdf_path,
            output_dir=out_dir,
        ),
        "issues": issues_to_dict(issues),
    }
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
