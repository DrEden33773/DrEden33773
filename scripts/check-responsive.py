"""Browser regression for GitHub's theme rewriting and README art direction.

Requires agent-browser. Uses temporary HTML made from the actual README picture
markup. Fixed-theme rewriting follows github/markup#1681; it intentionally drops
other clauses, so the former compound mobile/dark source fails on desktop.
"""
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SESSION = 'eden-responsive-regression'

def browser(*args):
    result = subprocess.run(['agent-browser', '--session', SESSION, '--json', *args], capture_output=True, text=True, check=True)
    response = json.loads(result.stdout)
    assert response['success'], response.get('error')
    return response['data'].get('result')

try:
    with tempfile.TemporaryDirectory(prefix='eden-responsive-') as tmp:
        checks = 0
        for name in ('README.md', 'README.zh-CN.md'):
            readme = (ROOT/name).read_text()
            pictures = '\n'.join(re.findall(r'<picture>.*?</picture>',readme,re.S))
            pictures = pictures.replace('="assets/', f'="{(ROOT/"assets").as_uri()}/')
            fixture = Path(tmp)/'index.html'
            fixture.write_text('<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>:root{color-scheme:light dark}body{margin:16px}article{max-width:960px}img{max-width:100%}</style><article>'+pictures+'</article>')
            for width in (390, 600, 601, 1600):
                for system, site in (('light','auto'),('dark','auto'),('light','dark'),('dark','light')):
                    browser('set','viewport',str(width),'900')
                    browser('set','media',system,'reduced-motion')
                    browser('open',fixture.as_uri())
                    if site != 'auto':
                        browser('eval', f'''(() => {{
                          document.documentElement.style.colorScheme = {json.dumps(site)};
                          for (const s of document.querySelectorAll('source[media]')) {{
                            if (s.media.includes('prefers-color-scheme')) {{
                              s.media = s.media.includes({json.dumps(site)}) ? '(prefers-color-scheme: light),(prefers-color-scheme: dark)' : 'not all';
                            }}
                          }}
                        }})()''')
                    browser('wait','--fn','[...document.images].every(i=>i.complete && i.naturalWidth>0)')
                    state = browser('eval', '''({width:innerWidth,scroll:document.documentElement.scrollWidth,images:[...document.querySelectorAll('img[width="100%"]')].map(i=>({source:i.currentSrc.split('/').pop(),naturalWidth:i.naturalWidth}))})''')
                    assert state['scroll'] <= width, state
                    assert len(state['images']) == 7, state
                    for image in state['images']:
                        assert ('-mobile' in image['source']) == (width <= 600), (name,width,system,site,image)
                        assert image['naturalWidth'] == (520 if width <= 600 else 960), (name,width,system,site,image)
                        if width > 600:
                            theme = system if site == 'auto' else site
                            assert image['source'].endswith(f'-{theme}.svg'),image
                    checks += 1
        print(f'PASS: {checks} combinations across both READMEs, 390/600/601/1600px, automatic and fixed themes.')
finally:
    browser('close')
