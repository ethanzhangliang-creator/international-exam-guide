from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


GENERATED_ASSET_STATUSES = {
    "generated",
    "reviewed",
    "reviewed-generated",
    "provider-selected-generated",
    "manual-generated",
    "codex-router-generated",
}
PENDING_ASSET_STATUSES = {
    "external-generation-required",
    "provider-selected-pending-generation",
    "infographic-provider-required",
    "svg-fallback-needs-review",
}
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SVG_EXTENSIONS = {".svg"}

SCIENTIFIC_VECTOR_TERMS = {
    "axis",
    "bar",
    "chart",
    "curve",
    "data",
    "distance-time",
    "energy",
    "equation",
    "fraction",
    "function",
    "graph",
    "line",
    "motion",
    "number",
    "ph",
    "probability",
    "rate",
    "ratio",
    "scatter",
    "statistics",
    "table",
    "triangle",
}


def visual_asset_key(
    topic_title: str,
    focus_point: str,
    visual_type: str,
    complexity: str,
) -> str:
    return "||".join(
        normalize_key_part(value)
        for value in [topic_title, focus_point, visual_type, complexity]
    )


def visual_asset_key_from_brief(brief: Any) -> str:
    return visual_asset_key(
        brief.topic_title,
        brief.focus_point,
        brief.visual_type,
        brief.complexity,
    )


def visual_asset_key_from_entry(entry: dict[str, Any]) -> str:
    return str(
        entry.get("key")
        or visual_asset_key(
            str(entry.get("topic_title", "")),
            str(entry.get("focus_point", "")),
            str(entry.get("visual_type", "")),
            str(entry.get("complexity", "")),
        )
    )


def load_visual_manifest(path_or_dir: Path) -> list[dict[str, Any]]:
    manifest_path = (
        path_or_dir
        if path_or_dir.name == "visual_manifest.json"
        else path_or_dir / "visual_manifest.json"
    )
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if isinstance(entry, dict)]


def build_visual_asset_lookup(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {visual_asset_key_from_entry(entry): entry for entry in entries}


def is_generated_asset(entry: dict[str, Any]) -> bool:
    return str(entry.get("asset_status", "")).lower() in GENERATED_ASSET_STATUSES


def is_raster_asset(filename: str | None) -> bool:
    if not filename:
        return False
    return Path(filename).suffix.lower() in RASTER_EXTENSIONS


def is_svg_asset(filename: str | None) -> bool:
    if not filename:
        return False
    return Path(filename).suffix.lower() in SVG_EXTENSIONS


def has_renderable_infographic(entry: dict[str, Any], images_dir: Path | None = None) -> bool:
    filename = str(entry.get("file") or "")
    if not is_generated_asset(entry) or not is_raster_asset(filename):
        return False
    return images_dir is None or (images_dir / filename).exists()


def has_renderable_svg_fallback(entry: dict[str, Any], images_dir: Path | None = None) -> bool:
    filename = str(entry.get("file") or "")
    if str(entry.get("asset_status", "")).lower() != "svg-fallback-needs-review":
        return False
    if not is_svg_asset(filename):
        return False
    return images_dir is None or (images_dir / filename).exists()


def scientific_vector_route(visual_type: str) -> str:
    """Classify SVG fallbacks that should follow scientific plotting rules."""
    tokens = set(re.findall(r"[a-z0-9-]+", visual_type.lower()))
    if tokens & SCIENTIFIC_VECTOR_TERMS:
        return "scripted-scientific-vector"
    return "hand-authored-svg"


def normalize_key_part(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    return normalized
