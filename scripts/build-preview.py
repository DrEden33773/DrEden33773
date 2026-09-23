"""Render local README previews with Marked and the bundled GitHub Markdown CSS."""

import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "preview" / "github-markdown.css").read_text() + (
    ROOT / "preview" / "theme-visibility.css"
).read_text()
for lang, filename in [("en", "README.md"), ("zh-CN", "README.zh-CN.md")]:
    content = subprocess.check_output(
        ["npx", "--yes", "marked@18.0.14", "-i", str(ROOT / filename)], text=True
    )
    content = (
        content.replace('src="assets/', 'src="../assets/')
        .replace('srcset="assets/', 'srcset="../assets/')
        .replace('href="README.zh-CN.md"', 'href="zh.html"')
        .replace('href="README.md"', 'href="index.html"')
        .replace('href="data/', 'href="../data/')
        .replace('href="assets/', 'href="../assets/')
    )

    def heading(m: re.Match[str]) -> str:
        label = html.unescape(re.sub("<[^>]+>", "", m[2]))
        slug = re.sub(r"[^\w\- ]", "", label.lower()).replace(" ", "-")
        return f'<h{m[1]} id="{slug}">{m[2]}</h{m[1]}>'

    content = re.sub(r"<h([1-6])>(.*?)</h\1>", heading, content)
    extra = """
    :root{color-scheme:light dark} body{margin:0;background:#fff;color:#596579;font-family:system-ui,sans-serif}
    .preview-note{max-width:830px;margin:26px auto 14px;padding:0 24px;font-size:12px}
    article.markdown-body{box-sizing:border-box;max-width:896px;padding:32px;margin:0 auto 40px;border:1px solid #d1d9e0;border-radius:6px}
    .markdown-body picture img[width="100%"]{display:block}
    @media(prefers-color-scheme:dark){body{background:#0d1117;color:#919baa}article.markdown-body{border-color:#3d444d}}
    @media(max-width:600px){article.markdown-body{padding:16px;border:0}.preview-note{padding:0 16px;margin-top:16px}}
    """
    page = f'<!doctype html><html lang="{lang}" data-color-mode="auto"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Eden / Profile preview</title><style>{CSS}{extra}</style></head><body><div class="preview-note">Local GitHub-style preview / follows your system theme</div><article class="markdown-body">{content}</article></body></html>'
    (ROOT / "preview" / ("index.html" if lang == "en" else "zh.html")).write_text(page)
print("Built both local previews.")
