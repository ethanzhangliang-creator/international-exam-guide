from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


SAMPLE_COMMANDS = [
    {
        "query": "9260",
        "level": "igcse",
        "out": "mathematics-9260-sample",
        "questions": "2",
        "image_provider": "prompt-queue",
        "style": "detective",
        "language": "en",
    },
    {
        "query": "economics",
        "level": "igcse",
        "out": "economics-9214-sample",
        "questions": "2",
        "image_provider": "prompt-queue",
        "style": "life",
        "language": "en",
    },
    {
        "query": "chemistry",
        "level": "igcse",
        "out": "chemistry-9202-sample",
        "questions": "2",
        "image_provider": "prompt-queue",
        "style": "friendly",
        "language": "en",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the showcase release samples, export PDFs, and verify final completeness."
    )
    parser.add_argument("--outputs-root", default="./outputs")
    parser.add_argument("--skip-verify", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    outputs_root = Path(args.outputs_root).resolve()
    env = os.environ.copy()
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = (
        src_path if not env.get("PYTHONPATH") else src_path + os.pathsep + env["PYTHONPATH"]
    )

    for sample in SAMPLE_COMMANDS:
        command = [
            sys.executable,
            "-m",
            "intl_exam_guide.cli",
            "generate",
            "--query",
            sample["query"],
            "--level",
            sample["level"],
            "--out",
            str(outputs_root / sample["out"]),
            "--questions-per-topic",
            sample["questions"],
            "--image-provider",
            sample["image_provider"],
            "--explanation-style",
            sample["style"],
            "--language",
            sample["language"],
        ]
        print(" ".join(command))
        result = subprocess.run(command, cwd=repo_root, env=env)
        if result.returncode != 0:
            return result.returncode

    if args.skip_verify:
        return 0

    verify = [
        sys.executable,
        str(repo_root / "scripts" / "verify_release_samples.py"),
        "--outputs-root",
        str(outputs_root),
    ]
    return subprocess.run(verify, cwd=repo_root, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
