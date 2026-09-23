"""Fetch GitHub profile data via authenticated gh; save only public aggregate data."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

from models import Project, QueryResponse, RepositoryDetails, Snapshot

ROOT = Path(__file__).resolve().parents[1]
LOGIN = "DrEden33773"
QUERY = """query($login:String!, $cursor:String) {
  user(login:$login) {
    followers { totalCount }
    contributionsCollection { contributionCalendar {
      totalContributions weeks { contributionDays { date contributionCount contributionLevel } }
    } }
    repositories(first:100, after:$cursor, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false) {
      totalCount pageInfo { hasNextPage endCursor }
      nodes { stargazerCount }
    }
  }
}"""


def gh(*args: str) -> object:
    return json.loads(
        subprocess.check_output(["gh", "api", *args], text=True, timeout=90)
    )


def fetch() -> None:
    cursor: str | None = None
    stars, count = 0, 0
    while True:
        args = ["graphql", "-f", f"query={QUERY}", "-f", f"login={LOGIN}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        response = cast(QueryResponse, gh(*args))
        if response.get("errors"):
            raise RuntimeError("GitHub GraphQL returned errors")
        user = response["data"]["user"]
        repos = user["repositories"]
        stars += sum(repo["stargazerCount"] for repo in repos["nodes"])
        count += len(repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    assert count == repos["totalCount"], "Incomplete repository pagination"
    projects: list[Project] = []
    for repo in [f"{LOGIN}/adam-agent", "AI-Eden/eden-skills", "KaiOnCode/QuanTable"]:
        data = cast(RepositoryDetails, gh(f"repos/{repo}"))
        projects.append({"repository": repo, "stars": data["stargazers_count"]})
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    assert (
        sum(day["contributionCount"] for day in days) == calendar["totalContributions"]
    )
    snapshot: Snapshot = {
        "login": LOGIN,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "followers": user["followers"]["totalCount"],
        "original_public_repositories": count,
        "owned_repository_stars": stars,
        "contribution_calendar": calendar,
        "projects": projects,
    }
    path = ROOT / "data" / "github.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2) + "\n")
    print(
        f"Fetched {count} original public repositories; {calendar['totalContributions']} contributions."
    )


if __name__ == "__main__":
    fetch()
