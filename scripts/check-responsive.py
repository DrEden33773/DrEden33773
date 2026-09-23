"""Regress GitHub theme selection, live switches, and mobile art direction.

Requires agent-browser. Tests actual README markup with GitHub's documented
page-level theme visibility, including WebViews without color-scheme inheritance.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import TypedDict, cast

ROOT = Path(__file__).resolve().parents[1]
SESSION = "eden-responsive-regression"


class BrowserResponse(TypedDict):
    success: bool
    data: dict[str, object]
    error: object


class ImageState(TypedDict):
    source: str
    naturalWidth: int
    alt: str


class PageState(TypedDict):
    width: int
    scroll: int
    images: list[ImageState]


def browser(*args: str) -> object:
    result = subprocess.run(
        ["agent-browser", "--session", SESSION, "--json", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    response = cast(BrowserResponse, json.loads(result.stdout))
    assert response["success"], response.get("error")
    return response["data"].get("result")


def apply_theme(site: str) -> None:
    browser(
        "eval",
        f"""(() => {{
        document.documentElement.dataset.colorMode = {json.dumps(site)};
        // Deliberately break SVG color-scheme inheritance, as WebViews can do.
        for (const image of document.images) image.style.colorScheme = 'light';
        for (const s of document.querySelectorAll('source[media]')) {{
            s.dataset.originalMedia ??= s.media;
            const original = s.dataset.originalMedia;
            if (original.includes('prefers-color-scheme')) {{
                s.media = {json.dumps(site)} === 'auto' ? original :
                    original.includes({json.dumps(site)}) ? 'all' : 'not all';
            }}
        }}
    }})()""",
    )


def check_page(width: int, theme: str) -> None:
    browser(
        "wait",
        "--fn",
        "[...document.images].every(i=>!i.checkVisibility() || (i.complete && i.naturalWidth>0))",
    )
    state = cast(
        PageState,
        browser(
            "eval",
            """({
        width:innerWidth,scroll:document.documentElement.scrollWidth,
        images:[...document.querySelectorAll('img[width="100%"]')]
          .filter(i=>i.checkVisibility()).map(i=>({
            source:i.currentSrc.split('/').pop().split('#')[0],
            naturalWidth:i.naturalWidth,alt:i.alt
          }))
    })""",
        ),
    )
    assert state["scroll"] <= width, state
    assert len(state["images"]) == 7, state
    assert len({image["alt"] for image in state["images"]}) == 7, state
    for image in state["images"]:
        assert ("-mobile-" in image["source"]) == (width <= 600), image
        assert image["naturalWidth"] == (520 if width <= 600 else 960), image
        assert image["source"].endswith(f"-{theme}.svg"), image
        svg = (ROOT / "assets" / image["source"]).read_text()
        assert "prefers-color-scheme" not in svg, image


def main() -> None:
    visibility = (ROOT / "preview" / "theme-visibility.css").read_text()
    checks = 0
    try:
        with tempfile.TemporaryDirectory(prefix="eden-responsive-") as tmp:
            for name in ("README.md", "README.zh-CN.md"):
                readme = (ROOT / name).read_text()
                pictures = "\n".join(
                    re.findall(
                        r"<a[^>]+>\s*<picture>.*?</picture>\s*</a>", readme, re.S
                    )
                )
                pictures = pictures.replace(
                    '="assets/', f'="{(ROOT / "assets").as_uri()}/'
                )
                fixture = Path(tmp) / "index.html"
                fixture.write_text(
                    '<!doctype html><html data-color-mode="auto"><meta name="viewport" content="width=device-width,initial-scale=1">'
                    f"<style>{visibility} body{{margin:16px}} article{{max-width:960px}} img{{max-width:100%}}</style><article>{pictures}</article></html>"
                )
                for width in (390, 600, 601, 1600):
                    for system in ("light", "dark"):
                        browser("set", "viewport", str(width), "900")
                        browser("set", "media", system, "reduced-motion")
                        browser("open", fixture.as_uri())
                        # Reuse the same page and cached images across theme switches.
                        for site in ("auto", "dark", "light", "dark", "auto"):
                            apply_theme(site)
                            check_page(width, system if site == "auto" else site)
                            checks += 1
        print(
            f"PASS: {checks} bilingual layout/theme states, including live switches and missing SVG theme inheritance."
        )
    finally:
        browser("close")


if __name__ == "__main__":
    main()
