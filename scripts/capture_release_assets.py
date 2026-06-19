from __future__ import annotations

import argparse
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path


SAMPLES = {
    "mathematics-9260-sample": "sample-math-guide.png",
    "economics-9214-sample": "sample-economics-guide.png",
    "chemistry-9202-sample": "sample-chemistry-guide.png",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture guide screenshots for README/docs assets.")
    parser.add_argument("--outputs-root", default="./outputs")
    parser.add_argument("--docs-assets", default="docs/assets")
    parser.add_argument("--viewport-width", type=int, default=1440)
    parser.add_argument("--viewport-height", type=int, default=720)
    args = parser.parse_args()

    outputs_root = Path(args.outputs_root).resolve()
    docs_assets = Path(args.docs_assets).resolve()
    docs_assets.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return capture_with_chrome_cli(outputs_root, docs_assets, args.viewport_width, args.viewport_height)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.viewport_width, "height": args.viewport_height},
            device_scale_factor=1,
        )
        captured: list[Path] = []
        for sample, asset_name in SAMPLES.items():
            guide = outputs_root / sample / "guide.html"
            if not guide.exists():
                print(f"missing guide: {guide}", file=sys.stderr)
                browser.close()
                return 1
            page.goto(guide.as_uri(), wait_until="networkidle")
            target = first_visible(
                page,
                [
                    ".generated-infographic",
                    ".visual-example",
                    ".guide-grid",
                    ".topic",
                ],
                PlaywrightError,
            )
            if target is None:
                print(f"no screenshot target found in {guide}", file=sys.stderr)
                browser.close()
                return 1
            out = docs_assets / asset_name
            target.screenshot(path=str(out))
            captured.append(out)

        primary = docs_assets / SAMPLES["mathematics-9260-sample"]
        snapshot = docs_assets / "sample-guide-snapshot.png"
        shutil.copyfile(primary, snapshot)
        captured.append(snapshot)
        browser.close()

    for path in captured:
        print(path)
    return 0


def capture_with_chrome_cli(
    outputs_root: Path,
    docs_assets: Path,
    viewport_width: int,
    viewport_height: int,
) -> int:
    browser = find_browser()
    if not browser:
        print(
            "No Playwright package and no Chrome/Edge executable found for screenshot capture.",
            file=sys.stderr,
        )
        return 2

    captured: list[Path] = []
    with tempfile.TemporaryDirectory() as tmp:
        user_data_dir = Path(tmp) / "chrome-profile"
        for sample, asset_name in SAMPLES.items():
            guide = outputs_root / sample / "guide.html"
            if not guide.exists():
                print(f"missing guide: {guide}", file=sys.stderr)
                return 1
            out = docs_assets / asset_name
            capture_html = guide.parent / "_capture_release_asset.html"
            capture_html.write_text(build_capture_html(guide), encoding="utf-8")
            try:
                command = [
                    browser,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-first-run",
                    f"--user-data-dir={user_data_dir}",
                    f"--window-size={viewport_width},{viewport_height}",
                    "--hide-scrollbars",
                    "--virtual-time-budget=2000",
                    f"--screenshot={out.resolve()}",
                    capture_html.resolve().as_uri(),
                ]
                subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
            finally:
                capture_html.unlink(missing_ok=True)
            captured.append(out)

    primary = docs_assets / SAMPLES["mathematics-9260-sample"]
    snapshot = docs_assets / "sample-guide-snapshot.png"
    shutil.copyfile(primary, snapshot)
    captured.append(snapshot)
    for path in captured:
        print(path)
    return 0


def build_capture_html(guide: Path) -> str:
    html = guide.read_text(encoding="utf-8", errors="replace")
    script = """
<script>
window.addEventListener("load", () => {
  const selectors = [".generated-infographic", ".visual-example", ".guide-grid", ".topic"];
  const target = selectors.map(selector => document.querySelector(selector)).find(Boolean);
  if (!target) return;
  const clone = target.cloneNode(true);
  document.body.innerHTML = "";
  document.body.style.margin = "24px";
  document.body.style.background = "#f6f1e8";
  clone.style.maxWidth = "1120px";
  clone.style.margin = "0 auto";
  document.body.appendChild(clone);
});
</script>
"""
    return html.replace("</body>", f"{script}\n</body>")


def first_visible(page, selectors: list[str], playwright_error: type[Exception]):
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() and locator.is_visible(timeout=1000):
                return locator
        except playwright_error:
            continue
    return None


def find_browser() -> str | None:
    candidates = [
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


if __name__ == "__main__":
    raise SystemExit(main())
