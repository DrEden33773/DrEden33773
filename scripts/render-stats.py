"""Render GitHub snapshot as themed, responsive SVGs; never fabricate missing data."""
import json
from datetime import date
from artwork import Canvas, ROOT

DATA = json.loads((ROOT/'data'/'github.json').read_text())
ASSETS = ROOT/'assets'

def stats(theme, mobile):
    w,h = (520,550) if mobile else (960,365)
    c=Canvas(w,h,theme,'Eden on GitHub', 'GitHub API snapshot. Contributions over the past year; stars and repository counts cover personally owned public non-fork repositories.')
    p=c.p
    c.rect(0,0,w,h,p['bg'],14)
    c.text('building in public',26,39,25,display=True)
    c.text('github / DrEden33773',26,64,13,p['muted'])
    updated=DATA['updated_at'][:10]
    if not mobile: c.text(f'updated {updated} UTC',w-26,39,12,p['muted'],anchor='end')
    values=[(DATA['contribution_calendar']['totalContributions'],'Contributions','past year'),(DATA['owned_repository_stars'],'Stars','owned, non-fork repos'),(DATA['original_public_repositories'],'Original repos','public, personally owned'),(DATA['followers'],'Followers','on GitHub')]
    for i,(value,label,note) in enumerate(values):
        x=26+(i%2)*248 if mobile else 26+i*232
        y=119+(i//2)*104 if mobile else 126
        c.text(f'{value:,}',x,y,45,p['blue'] if i%2==0 else p['cyan'],display=True)
        c.text(label,x,y+27,18 if mobile else 15,p['ink'])
        c.text(note,x,y+47,13 if mobile else 11,p['muted'])
    weeks=DATA['contribution_calendar']['weeks']
    if mobile: weeks=weeks[-26:]
    y0=343 if mobile else 221
    step=17
    c.text('Last 26 weeks' if mobile else 'Contribution calendar / past year',26,y0-22,13,p['muted'])
    colors=[p['empty'],'#CAC5F4','#9F92E5','#7761CE','#5540A9'] if theme=='light' else [p['empty'],'#42416C','#66609B','#9786CB','#C2AEF2']
    levels=['NONE','FIRST_QUARTILE','SECOND_QUARTILE','THIRD_QUARTILE','FOURTH_QUARTILE']
    for col,week in enumerate(weeks):
        for day in week['contributionDays']:
            row=(date.fromisoformat(day['date']).weekday()+1)%7
            color=colors[levels.index(day['contributionLevel'])]
            x,y=26+col*step,y0+row*step
            c.add(f'<g><title>{day["date"]}: {day["contributionCount"]} contributions</title>')
            c.rect(x,y,12,12,color,3)
            c.add('</g>')
    if mobile:
        c.text(f'updated {updated} UTC',26,h-42,12,p['muted'])
        c.text('Source: GitHub contribution calendar',26,h-21,11,p['muted'])
    else:
        start=weeks[0]['contributionDays'][0]['date']
        end=weeks[-1]['contributionDays'][-1]['date']
        c.text(f'{start} - {end}',26,h-18,11,p['muted'])
        c.text('less',w-177,h-18,10,p['muted'])
        for i,color in enumerate(colors): c.rect(w-140+i*16,h-28,11,11,color,2)
        c.text('more',w-24,h-18,10,p['muted'],anchor='end')
    c.save(ASSETS/f'github-{"mobile-" if mobile else ""}{theme}.svg')

def project(theme, index, repo, stars, mobile=False):
    name=repo.split('/')[-1]
    roles=['creator / maintainer','creator / maintainer','core contributor']
    w,h = (520,110) if mobile else (960,96)
    c=Canvas(w,h,theme,f'{name} / {roles[index]}',f'{stars} GitHub stars. Open the repository.')
    p=c.p
    c.rect(0,0,w,h,p['bg'],10)
    c.rect(0,19,3,58,[p['blue'],p['cyan'],p['pink']][index],1)
    c.text(name,24,43,31,display=True)
    c.text(roles[index],24,78 if mobile else 72,16 if mobile else 14,p['muted'])
    c.text(f'{stars} {"star" if stars == 1 else "stars"}',w-24,52,19 if mobile else 20,p['blue'],anchor='end')
    c.save(ASSETS/f'project-{name}-{"mobile-" if mobile else ""}{theme}.svg')

for theme in ('light','dark'):
    for mobile in (False,True): stats(theme,mobile)
    for i,repo in enumerate(DATA['projects']):
        for mobile in (False,True): project(theme,i,repo['repository'],repo['stars'],mobile)
print('Rendered GitHub panels and project cards from the saved snapshot.')
