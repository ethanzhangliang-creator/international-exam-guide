from __future__ import annotations


ICON_PATHS = {
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
    "bridge": '<path d="M4 15c3-7 13-7 16 0"/><path d="M4 15h16"/><path d="M8 15v-3"/><path d="M16 15v-3"/>',
    "steps": '<path d="M5 18h4v-4h4v-4h4V6h2"/><path d="M5 18h14"/>',
    "alert": '<path d="M12 4 3 20h18L12 4z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "practice": '<path d="M6 4h9l3 3v13H6z"/><path d="M14 4v4h4"/><path d="M9 13h6"/><path d="M9 17h4"/>',
    "command": '<path d="M7 8h10"/><path d="M7 12h7"/><path d="M7 16h4"/>',
    "level": '<path d="M5 17h3v-5H5z"/><path d="M11 17h3V7h-3z"/><path d="M17 17h3V4h-3z"/>',
    "focus": '<circle cx="12" cy="12" r="7"/><path d="M12 9v3l2 2"/>',
    "frame": '<rect x="5" y="6" width="14" height="12" rx="2"/><path d="M8 10h8"/><path d="M8 14h6"/>',
    "check": '<path d="m5 12 4 4 10-10"/>',
    "visual": '<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m7 17 4-4 3 3 2-2 2 3"/>',
    "life": '<path d="M4 12 12 5l8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-5h4v5"/>',
    "detective": '<circle cx="11" cy="11" r="5"/><path d="m15 15 5 5"/><path d="M8 11h6"/>',
    "quest": '<path d="M12 3 4 7v6c0 5 3.5 7.5 8 8 4.5-.5 8-3 8-8V7z"/><path d="M9 12l2 2 4-5"/>',
}


def render_icon(name: str) -> str:
    path = ICON_PATHS.get(name, ICON_PATHS["target"])
    return (
        '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{path}</svg>'
    )
