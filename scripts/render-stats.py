"""Render GitHub snapshot as themed, responsive SVGs; never fabricate missing data."""

import json
from datetime import date
from typing import cast

from artwork import ROOT, Canvas
from models import Snapshot

DATA = cast(Snapshot, json.loads((ROOT / "data" / "github.json").read_text()))
ASSETS = ROOT / "assets"


def stats(theme: str, mobile: bool) -> None:
    w, h = (520, 460) if mobile else (960, 436)
    c = Canvas(
        w,
        h,
        theme,
        "Eden on GitHub",
        "GitHub API snapshot. Stars and original repository counts cover personally owned public non-fork repositories; contributions and followers come from the same account.",
    )
    p = c.p
    c.rect(0, 0, w, h, p["bg"], 14)
    c.text("building in public", 26, 39, 25, display=True)
    c.text("github / DrEden33773", 26, 64, 13, p["muted"])
    updated = DATA["updated_at"][:10]
    if not mobile:
        c.text(f"updated {updated} UTC", w - 26, 39, 12, p["muted"], anchor="end")
    # Stars and original repositories lead: they are the only numbers here that
    # a third party has to give you. Contribution counts are trivially inflated
    # by forks and daily commits, so they drop to the secondary row.
    headline: list[tuple[int, str, str, str]] = [
        (DATA["owned_repository_stars"], "Stars", "owned, non-fork repos", p["cyan"]),
        (
            DATA["original_public_repositories"],
            "Original repos",
            "public, personally owned",
            p["blue"],
        ),
    ]
    headline_size, headline_step = (44, 244) if mobile else (58, 472)
    headline_y = 124 if mobile else 145
    for i, (value, label, note, color) in enumerate(headline):
        x = 26 + i * headline_step
        c.text(f"{value:,}", x, headline_y, headline_size, color, display=True)
        c.text(label, x, headline_y + 31, 17 if mobile else 20, p["ink"])
        c.text(note, x, headline_y + 50, 12, p["muted"])
    secondary: list[tuple[int, str]] = [
        (
            DATA["contribution_calendar"]["totalContributions"],
            "contributions past year",
        ),
        (DATA["followers"], "followers on GitHub"),
    ]
    secondary_y = 205 if mobile else 234
    for i, (value, label) in enumerate(secondary):
        x = 26 if mobile else 26 + i * 472
        y = secondary_y + i * 34 if mobile else secondary_y
        width = c.text(f"{value:,}", x, y, 24, p["ink"], display=True)
        c.text(label, x + width + 12, y, 13, p["muted"])
    weeks = DATA["contribution_calendar"]["weeks"]
    if mobile:
        weeks = weeks[-26:]
    colors = (
        [p["empty"], "#CAC5F4", "#9F92E5", "#7761CE", "#5540A9"]
        if theme == "light"
        else [p["empty"], "#42416C", "#66609B", "#9786CB", "#C2AEF2"]
    )
    legend_y = 277 if mobile else 272
    c.text(
        "Last 26 weeks" if mobile else "Contribution calendar / past year",
        26,
        legend_y,
        13,
        p["muted"],
    )
    if not mobile:
        c.text("less", w - 160, legend_y, 10, p["muted"])
        c.text("more", w - 26, legend_y, 10, p["muted"], anchor="end")
        for i, color in enumerate(colors):
            c.rect(w - 136 + i * 16, legend_y - 11, 11, 11, color, 2)
    y0 = 295 if mobile else 290
    step = 17
    levels = [
        "NONE",
        "FIRST_QUARTILE",
        "SECOND_QUARTILE",
        "THIRD_QUARTILE",
        "FOURTH_QUARTILE",
    ]
    for col, week in enumerate(weeks):
        for day in week["contributionDays"]:
            row = (date.fromisoformat(day["date"]).weekday() + 1) % 7
            color = colors[levels.index(day["contributionLevel"])]
            x, y = 26 + col * step, y0 + row * step
            c.add(
                f"<g><title>{day['date']}: {day['contributionCount']} contributions</title>"
            )
            c.rect(x, y, 12, 12, color, 3)
            c.add("</g>")
    if mobile:
        c.text(f"updated {updated} UTC", 26, h - 42, 12, p["muted"])
        c.text("Source: GitHub contribution calendar", 26, h - 21, 11, p["muted"])
    else:
        start = weeks[0]["contributionDays"][0]["date"]
        end = weeks[-1]["contributionDays"][-1]["date"]
        c.text(f"{start} - {end}", 26, h - 18, 11, p["muted"])
    c.save(ASSETS / f"github-{'mobile-' if mobile else ''}{theme}.svg")


def project(
    theme: str, index: int, repo: str, stars: int, mobile: bool = False
) -> None:
    name = repo.split("/")[-1]
    roles = ["creator / maintainer", "creator / maintainer", "core contributor"]
    w, h = (520, 110) if mobile else (960, 96)
    c = Canvas(
        w,
        h,
        theme,
        f"{name} / {roles[index]}",
        f"{stars} GitHub stars. Open the repository.",
    )
    p = c.p
    c.rect(0, 0, w, h, p["bg"], 10)
    c.rect(0, 19, 3, 58, [p["blue"], p["cyan"], p["pink"]][index], 1)
    c.text(name, 24, 43, 31, display=True)
    c.text(roles[index], 24, 78 if mobile else 72, 16 if mobile else 14, p["muted"])
    c.text(
        f"{stars} {'star' if stars == 1 else 'stars'}",
        w - 24,
        52,
        19 if mobile else 20,
        p["blue"],
        anchor="end",
    )
    c.save(ASSETS / f"project-{name}-{'mobile-' if mobile else ''}{theme}.svg")


def main() -> None:
    for theme in ("light", "dark"):
        for mobile in (False, True):
            stats(theme, mobile)
        for i, repo in enumerate(DATA["projects"]):
            for mobile in (False, True):
                project(theme, i, repo["repository"], repo["stars"], mobile)
    print("Rendered GitHub panels and project cards from the saved snapshot.")


if __name__ == "__main__":
    main()
