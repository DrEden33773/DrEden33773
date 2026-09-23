"""Typed shapes for the GitHub API responses and saved profile snapshot."""

from typing import NotRequired, TypedDict


class ContributionDay(TypedDict):
    date: str
    contributionCount: int
    contributionLevel: str


class ContributionWeek(TypedDict):
    contributionDays: list[ContributionDay]


class ContributionCalendar(TypedDict):
    totalContributions: int
    weeks: list[ContributionWeek]


class Project(TypedDict):
    repository: str
    stars: int


class Snapshot(TypedDict):
    login: str
    updated_at: str
    followers: int
    original_public_repositories: int
    owned_repository_stars: int
    contribution_calendar: ContributionCalendar
    projects: list[Project]


class PageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class RepositoryNode(TypedDict):
    stargazerCount: int


class Repositories(TypedDict):
    totalCount: int
    pageInfo: PageInfo
    nodes: list[RepositoryNode]


class Count(TypedDict):
    totalCount: int


class Collection(TypedDict):
    contributionCalendar: ContributionCalendar


class User(TypedDict):
    followers: Count
    contributionsCollection: Collection
    repositories: Repositories


class QueryData(TypedDict):
    user: User


class QueryResponse(TypedDict):
    data: QueryData
    errors: NotRequired[list[object]]


class RepositoryDetails(TypedDict):
    stargazers_count: int
