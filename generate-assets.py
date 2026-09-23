"""Render the profile hero and stack. Run after installing scripts/requirements.txt."""
import sys
import re
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parent / 'scripts'))
from artwork import Canvas, ROOT

ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

def hero(theme, mobile):
    w, h = (520, 670) if mobile else (960, 450)
    c = Canvas(w, h, theme, 'Eden / AI Agent Engineering', 'Building agents from the inside out. An animated, illustrative agent workbench: context, tools, sessions, and evaluation.')
    p = c.p
    c.add('''<style>
      .signal {stroke-dasharray:10 550; animation:signal 8s linear infinite}
      .cursor {animation:blink 1.5s step-end infinite}
      .pulse {animation:pulse 4s ease-in-out infinite}
      @keyframes signal {to {stroke-dashoffset:-560}}
      @keyframes blink {50% {opacity:0}}
      @keyframes pulse {50% {opacity:.4}}
      @media(prefers-reduced-motion:reduce){.signal,.cursor,.pulse{animation:none}}
    </style>''')
    c.rect(0, 0, w, h, p['bg'], 18)
    c.add(f'<defs><radialGradient id="wash"><stop stop-color="{p["blue"]}" stop-opacity=".2"/><stop offset="1" stop-color="{p["bg"]}" stop-opacity="0"/></radialGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="{p["line"]}"/></pattern></defs>')
    c.rect(0, 0, w, h, 'url(#grid)', 18)
    c.add(f'<ellipse cx="{w*.75}" cy="{h*.6}" rx="360" ry="250" fill="url(#wash)"/>')
    c.add(f'<path d="M24 54 H{w-24}" stroke="{p["line"]}"/>')
    c.add(f'<circle cx="32" cy="29" r="4" fill="{p["cyan"]}" class="pulse"/>')
    c.text('eden@workbench', 46, 34, 14, p['muted'])
    c.text('~/agents', w-30, 34, 14, p['muted'], anchor='end')
    c.text('eden', 28, 203 if mobile else 228, 138 if mobile else 158, display='jetbrains-bold')
    cursor_x = 365 if mobile else 420
    c.rect(cursor_x, 192 if mobile else 214, 45, 12, p['cyan'], extra='class="cursor"')
    c.text('AI Agent Engineer', 32, 250 if mobile else 277, 24, p['blue'], display=True)
    for i, line in enumerate(['Building agents', 'from the inside out.']):
        c.text(line, 32, (291 if mobile else 316) + i*25, 18, p['muted'])
    # A schematic rather than a made-up execution log.
    x, y = (30, 351) if mobile else (535, 94)
    c.add(f'<g transform="translate({x} {y})">')
    c.rect(0, 0, 395 if not mobile else 460, 237, p['panel'], 12, f'stroke="{p["line"]}"')
    c.text('inside the loop', 20, 31, 14, p['muted'])
    c.text('() ->', 350 if not mobile else 415, 31, 13, p['cyan'], anchor='end')
    shift = 30 if mobile else 0
    c.add(f'<g transform="translate({shift} 0)">')
    route = 'M90 85 H305 V184 H90 V85'
    c.add(f'<path d="{route}" stroke="{p["line"]}" stroke-width="2" fill="none"/><path d="{route}" stroke="{p["cyan"]}" stroke-width="3" fill="none" class="signal"/>')
    for label, nx, ny, color in [('context',90,85,p['blue']),('tools',305,85,p['cyan']),('session',90,184,p['pink']),('evaluate',305,184,p['blue'])]:
        c.rect(nx-56, ny-17,112,34,p['panel'],7,f'stroke="{color}" stroke-opacity=".65"')
        c.text(label,nx,ny+5,14,color,anchor='middle')
    c.text('plan / act / inspect',197,140,14,p['ink'],anchor='middle')
    c.add('</g></g>')
    if not mobile:
        c.text('harnesses   /   tools   /   evals', 535, 361, 14, p['muted'])
    c.add(f'<path d="M30 {h-50} H{w-30}" stroke="{p["line"]}"/>')
    c.add(f'<circle cx="35" cy="{h-26}" r="4" fill="{p["cyan"]}"/>')
    c.text('Open to Agent Engineering roles', 49, h-21, 13 if mobile else 14, p['muted'])
    if not mobile:
        c.text('DrEden33773', w-32, h-21, 14, p['muted'], anchor='end')
    c.save(ASSETS/f'hero-{"mobile-" if mobile else ""}{theme}.svg')

ICONS = [('typescript','TypeScript'),('python','Python'),('rust','Rust'),('java','Java'),('kotlin','Kotlin'),('react','React'),('nextjs','Next.js'),('fastapi','FastAPI'),('spring','Spring Boot'),('nodejs','Node.js'),('postgresql','PostgreSQL'),('redis','Redis'),('docker','Docker'),('linux','Linux'),('githubactions','Actions')]

def stack(theme, mobile):
    w, cols, tilew, tileh = (520,3,157,105) if mobile else (960,5,180,98)
    h = 70 + ((len(ICONS)+cols-1)//cols)*tileh + 18
    c = Canvas(w,h,theme,'Tools I build with',', '.join(label for _,label in ICONS))
    p=c.p
    c.rect(0,0,w,h,p['bg'],14)
    c.text('tools of the trade',26,36,20,p['ink'],display=True)
    for i,(name,label) in enumerate(ICONS):
        x = 24+(i%cols)*tilew
        y = 60+(i//cols)*tileh
        c.rect(x,y,tilew-12,tileh-12,p['panel'],9,f'stroke="{p["line"]}" stroke-width=".6"')
        icon=ET.parse(ROOT/'vendor'/'devicon'/f'{name}.svg').getroot()
        icon.attrib.update(x=str(x+(tilew-12-34)/2),y=str(y+13),width='34',height='34')
        # Prefix embedded IDs (gradients/clipPaths) so independent icons cannot collide.
        s=ET.tostring(icon,encoding='unicode').replace('ns0:','').replace(':ns0','')
        ids=re.findall(r'\bid="([^"]+)"',s)
        for ident in ids:
            s=s.replace(f'id="{ident}"',f'id="{name}-{ident}"').replace(f'#{ident}',f'#{name}-{ident}')
        if name in ('rust','nextjs') and theme=='dark':
            s=s.replace('fill="#000"','fill="#EDF0FF"').replace('fill="#000000"','fill="#EDF0FF"')
            s=s.replace('<path ', '<path fill="#EDF0FF" ', 1) if 'fill=' not in s else s
        c.add(s)
        c.text(label,x+(tilew-12)/2,y+72,16 if mobile else 14,p['muted'],anchor='middle')
    c.save(ASSETS/f'stack-{"mobile-" if mobile else ""}{theme}.svg')


def button(theme, name, label, width, primary=False, large=False):
    height = 50 if large else 44
    c = Canvas(width, height, theme, label)
    p = c.p
    c.rect(3, 3, width-6, height-6, p['blue'] if primary else p['bg'], 9,
           f'stroke="{p["blue"] if primary else p["line"]}"')
    color = p['bg'] if primary else p['ink']
    c.text(label, width/2, height/2+5, 14, color, anchor='middle')
    c.save(ASSETS/f'button-{name}-{theme}.svg')


def contact(theme, mobile):
    w, h = (520, 150) if mobile else (960, 130)
    c = Canvas(w, h, theme, "Let's build something useful.", 'Coding agents, developer tools, and the people building them.')
    p = c.p
    c.rect(0,0,w,h,p['bg'],14)
    c.add(f'<path d="M24 24 H56 M24 24 V50 M{w-24} {h-24} H{w-56} M{w-24} {h-24} V{h-50}" stroke="{p["cyan"]}" stroke-width="2" fill="none"/>')
    c.text("Let's build", w/2, 63 if mobile else 56, 32, display='jetbrains-bold', anchor='middle')
    c.text('something useful.', w/2, 109 if mobile else 99, 32, display='jetbrains-bold', anchor='middle')
    c.save(ASSETS/f'contact-{"mobile-" if mobile else ""}{theme}.svg')

for theme in ('light','dark'):
    for mobile in (False,True):
        hero(theme,mobile)
        stack(theme,mobile)
        contact(theme,mobile)
    for name,label,width in [('nav-en','English',104),('nav-zh','简体中文',104),('nav-projects','Projects',110),('nav-stack','Stack',88),('nav-github','GitHub',100),('nav-hello','Contact me',132)]:
        button(theme,name,label,width)
    button(theme,'contact-hello','Contact me',142,primary=True,large=True)
    button(theme,'nav-contact-zh','联系我',104)
    button(theme,'contact-zh','联系我',142,primary=True,large=True)
    button(theme,'contact-repos','Repositories',194,large=True)
print('Generated hero, stack, navigation, and contact components.')
