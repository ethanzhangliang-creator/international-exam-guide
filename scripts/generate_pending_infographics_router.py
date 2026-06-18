from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


PENDING_STATUSES = {
    "external-generation-required",
    "provider-selected-pending-generation",
    "infographic-provider-required",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate pending infographic assets with the GPT Image 2 Codex-only "
            "Router script from image-gen-flow."
        )
    )
    parser.add_argument("output_dirs", nargs="+", help="Generated guide output directories.")
    parser.add_argument("--router-script", help="Path to image-gen-flow gpt_image2_router.py.")
    parser.add_argument("--api-key-env", default="YAIROUTER_API_KEY")
    parser.add_argument("--size", default="1536x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--output-format", default="png")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--retry-delay", type=int, default=30)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    router_script = resolve_router_script(args.router_script)
    env = os.environ.copy()
    api_key = resolve_env_value(args.api_key_env)
    if api_key:
        env[args.api_key_env] = api_key

    if not args.dry_run:
        if not router_script.exists():
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "router_script_missing",
                        "router_script": str(router_script),
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 1
        if not api_key:
            print(
                json.dumps(
                    {"ok": False, "error": "missing_api_key_env", "env": args.api_key_env},
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 1

    requested = 0
    generated = 0
    for output_dir_value in args.output_dirs:
        output_dir = Path(output_dir_value).resolve()
        images_dir = output_dir / "images"
        manifest_path = images_dir / "visual_manifest.json"
        manifest = load_manifest(manifest_path)
        changed = False
        for entry in manifest:
            if args.limit is not None and requested >= args.limit:
                break
            if not should_generate(entry, images_dir, args.force):
                continue
            requested += 1
            ok = generate_one(
                entry=entry,
                images_dir=images_dir,
                router_script=router_script,
                env=env,
                size=args.size,
                quality=args.quality,
                output_format=args.output_format,
                timeout=args.timeout,
                retries=args.retries,
                retry_delay=args.retry_delay,
                dry_run=args.dry_run,
            )
            if not ok:
                save_manifest(manifest_path, manifest)
                return 1
            generated += 1
            changed = changed or not args.dry_run
            if changed:
                save_manifest(manifest_path, manifest)
        if changed:
            save_manifest(manifest_path, manifest)

    result_key = "planned" if args.dry_run else "generated"
    print(
        json.dumps(
            {
                "ok": True,
                "requested": requested,
                result_key: generated,
                "size": args.size,
                "quality": args.quality,
                "output_format": args.output_format,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0


def resolve_router_script(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    env_value = os.environ.get("IMAGE_GEN_FLOW_GPT_ROUTER_SCRIPT")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return (
        Path.home()
        / ".agents"
        / "skills"
        / "image-gen-flow"
        / "scripts"
        / "gpt_image2_router.py"
    )


def resolve_env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    if os.name != "nt":
        return None
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            registry_value, _ = winreg.QueryValueEx(key, name)
            return str(registry_value) if registry_value else None
    except OSError:
        return None


def load_manifest(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"missing manifest: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit(f"visual manifest must be a list: {path}")
    return payload


def save_manifest(path: Path, manifest: list[dict[str, object]]) -> None:
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def should_generate(entry: dict[str, object], images_dir: Path, force: bool) -> bool:
    if entry.get("complexity") != "infographic":
        return False
    file_name = entry.get("file")
    if file_name and (images_dir / str(file_name)).exists() and not force:
        return False
    return force or str(entry.get("asset_status")) in PENDING_STATUSES or not file_name


def generate_one(
    entry: dict[str, object],
    images_dir: Path,
    router_script: Path,
    env: dict[str, str],
    size: str,
    quality: str,
    output_format: str,
    timeout: int,
    retries: int,
    retry_delay: int,
    dry_run: bool,
) -> bool:
    visual_id = str(entry.get("id") or "visual")
    topic = str(entry.get("topic_title") or visual_id)
    image_name = f"{visual_id}_{slugify(topic)}.{output_format}"
    prompt_dir = images_dir / "prompts"
    response_dir = images_dir / "responses"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    response_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = prompt_dir / f"{visual_id}.txt"
    out_path = images_dir / image_name
    response_path = response_dir / f"{visual_id}.json"
    prompt_path.write_text(str(entry.get("prompt") or ""), encoding="utf-8")

    if dry_run:
        print(
            json.dumps(
                {"dry_run": True, "id": visual_id, "out": str(out_path)},
                ensure_ascii=False,
            ),
            flush=True,
        )
        return True

    command = [
        sys.executable,
        str(router_script),
        "--prompt-file",
        str(prompt_path),
        "--size",
        size,
        "--quality",
        quality,
        "--output-format",
        output_format,
        "--out",
        str(out_path),
        "--response-json",
        str(response_path),
        "--timeout",
        str(timeout),
    ]
    max_attempts = max(1, retries)
    last_failure: dict[str, object] | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                env=env,
                timeout=timeout + 30,
            )
        except subprocess.TimeoutExpired as exc:
            last_failure = {
                "ok": False,
                "id": visual_id,
                "topic": topic,
                "attempt": attempt,
                "error": "router_subprocess_timeout",
                "timeout_seconds": timeout + 30,
                "stdout_tail": (exc.stdout or "")[-1000:],
                "stderr_tail": (exc.stderr or "")[-1000:],
            }
        else:
            if result.returncode == 0:
                break
            last_failure = {
                "ok": False,
                "id": visual_id,
                "topic": topic,
                "attempt": attempt,
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-1000:],
                "stderr_tail": result.stderr[-1000:],
            }
        if attempt < max_attempts:
            print(json.dumps(last_failure, ensure_ascii=False), file=sys.stderr, flush=True)
            time.sleep(max(0, retry_delay))
    else:
        print(json.dumps(last_failure or {"ok": False, "id": visual_id}, ensure_ascii=False), file=sys.stderr, flush=True)
        return False

    entry["file"] = image_name
    entry["asset_status"] = "codex-router-generated"
    entry["generated_by"] = "gpt-image-2 codex-only router"
    entry["image_size"] = size
    entry["image_quality"] = quality
    entry["output_format"] = output_format
    entry["response_json"] = str(response_path)
    print(
        json.dumps({"ok": True, "id": visual_id, "image": str(out_path)}, ensure_ascii=False),
        flush=True,
    )
    return True


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:54] or "infographic"


if __name__ == "__main__":
    raise SystemExit(main())
