"""Shared SVG renderer. Lettering is outlined from the two bundled fonts."""
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
PALETTES = {
    'dark': dict(bg='#101424', panel='#191F35', ink='#EDF0FF', muted='#A3AFCD', line='#313C5D', blue='#A49AFF', cyan='#66DAD4', pink='#EDADD1', empty='#242C45'),
    'light': dict(bg='#F3F3FC', panel='#FFFFFF', ink='#242342', muted='#626582', line='#D9DAEC', blue='#6951CA', cyan='#117F80', pink='#A5427D', empty='#E3E4F2'),
}

@lru_cache
def font(display=False):
    filename = 'Buttons-CJK.ttf' if display == 'cjk' else 'JetBrainsMono-Bold.ttf' if display == 'jetbrains-bold' else ('Iosevka-Bold.woff2' if display else 'JetBrainsMono-Regular.ttf')
    return TTFont(ROOT / 'fonts' / filename)

class Canvas:
    def __init__(self, width, height, theme, title, desc=''):
        self.width, self.height = width, height
        self.p = PALETTES[theme]
        self.title, self.desc = title, desc
        self.parts, self.glyphs = [], {}

    def add(self, markup):
        self.parts.append(markup)

    def rect(self, x, y, w, h, fill, rx=0, extra=''):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>')

    def text(self, value, x, y, size=16, color=None, display=False, anchor='start', extra=''):
        value = str(value)
        f = font(display)
        if any(ord(ch) not in f.getBestCmap() for ch in value):
            display = 'cjk'
            f = font(display)
        glyphset, cmap = f.getGlyphSet(), f.getBestCmap()
        scale = size / f['head'].unitsPerEm
        advances = [f['hmtx'][cmap[ord(ch)]][0] for ch in value]
        width = sum(advances) * scale
        if anchor == 'end': x -= width
        if anchor == 'middle': x -= width / 2
        uses, pos = [], 0
        for ch, advance in zip(value, advances):
            key = ('c' if display == 'cjk' else 'b' if display == 'jetbrains-bold' else ('i' if display else 'j')) + str(ord(ch))
            if key not in self.glyphs:
                pen = SVGPathPen(glyphset)
                glyphset[cmap[ord(ch)]].draw(pen)
                self.glyphs[key] = pen.getCommands()
            uses.append(f'<use href="#{key}" x="{pos}"/>')
            pos += advance
        self.add(f'<g fill="{color or self.p["ink"]}" aria-label="{escape(value)}" {extra}><title>{escape(value)}</title><g transform="translate({x:.2f} {y}) scale({scale:.6f} {-scale:.6f})">' + ''.join(uses) + '</g></g>')
        return width

    def save(self, path):
        defs = ''.join(f'<path id="{k}" d="{v}"/>' for k,v in self.glyphs.items())
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc"><title id="title">{escape(self.title)}</title><desc id="desc">{escape(self.desc)}</desc><defs>{defs}</defs>' + ''.join(self.parts) + '</svg>\n'
        Path(path).write_text(svg, encoding='utf-8')


def combine_mobile_variants(stem):
    """Keep viewport selection outside GitHub's color-scheme source rewriting.

    The mobile SVG inherits the embedding page's color-scheme. Its two groups
    contain the existing mobile artwork unchanged, with IDs namespaced.
    """
    import re
    import xml.etree.ElementTree as ET
    paths = [ROOT / 'assets' / f'{stem}-mobile-{theme}.svg' for theme in ('light', 'dark')]
    roots = [ET.parse(path).getroot() for path in paths]
    assert roots[0].attrib['viewBox'] == roots[1].attrib['viewBox']
    groups = []
    for theme, path in zip(('light', 'dark'), paths):
        svg = path.read_text()
        body = svg[svg.index('>') + 1:svg.rindex('</svg>')]
        for ident in set(re.findall(r'\bid="([^"]+)"', body)):
            replacement = f'{theme}-{ident}'
            body = body.replace(f'id="{ident}"', f'id="{replacement}"')
            body = body.replace(f'href="#{ident}"', f'href="#{replacement}"')
            body = body.replace(f'url(#{ident})', f'url(#{replacement})')
        groups.append(f'<g class="variant-{theme}">{body}</g>')
    attrs = roots[0].attrib
    title = escape(roots[0].find('{http://www.w3.org/2000/svg}title').text or stem)
    result = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{attrs["width"]}" height="{attrs["height"]}" '
        f'viewBox="{attrs["viewBox"]}" role="img" aria-labelledby="responsive-title">'
        f'<title id="responsive-title">{title}</title>'
        '<style>.variant-dark{display:none}@media(prefers-color-scheme:dark){'
        '.variant-light{display:none}.variant-dark{display:inline}}</style>'
        + ''.join(groups) + '</svg>\n'
    )
    (ROOT / 'assets' / f'{stem}-mobile.svg').write_text(result)
