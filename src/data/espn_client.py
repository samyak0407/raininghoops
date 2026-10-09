"""Public ESPN basketball injury and news client.

ESPN's public site API is undocumented and may change. Preserve raw responses,
record retrieval timestamps, and treat this source as supplemental context rather
than an authoritative league injury report.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball"
SUPPORTED_LEAGUES = {"NBA": "nba", "WNBA": "wnba"}

INJURY_COLUMNS = [
    "league", "team_id", "team_name", "team_abbreviation", "player_id",
    "player_name", "position", "status", "injury_type", "injury_detail",
    "injury_side", "injury_date", "short_comment", "long_comment",
    "source", "source_url",
]
NEWS_COLUMNS = [
    "league", "article_id", "headline", "description", "published",
    "updated", "link", "byline", "source", "source_url",
]


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get("displayName") or value.get("name") or value.get("abbreviation") or value.get("href")
    return str(value)


def _first(*values: Any) -> Any:
    return next((value for value in values if value not in (None, "")), None)


@dataclass
class ESPNClient:
    timeout: float = 20.0
    base_url: str = BASE_URL
    session: requests.Session | None = None

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "RainingHoops/0.1 (basketball research)",
            "Accept": "application/json",
        })

    @staticmethod
    def _league_slug(league: str) -> str:
        key = league.strip().upper()
        if key not in SUPPORTED_LEAGUES:
            raise ValueError(f"Unsupported league {league!r}; use NBA or WNBA.")
        return SUPPORTED_LEAGUES[key]

    def _get(self, league: str, resource: str) -> tuple[dict[str, Any], str]:
        slug = self._league_slug(league)
        if resource not in {"injuries", "news"}:
            raise ValueError("resource must be 'injuries' or 'news'")
        url = f"{self.base_url.rstrip('/')}/{slug}/{resource}"
        assert self.session is not None
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"ESPN {resource} response was not a JSON object.")
        return payload, url

    def injuries(self, league: str = "NBA") -> tuple[dict[str, Any], str]:
        """Return the raw league-wide injury payload and requested URL."""
        return self._get(league, "injuries")

    def news(self, league: str = "NBA") -> tuple[dict[str, Any], str]:
        """Return the raw league news payload and requested URL."""
        return self._get(league, "news")

    @staticmethod
    def normalize_injuries(payload: dict[str, Any], league: str, source_url: str) -> pd.DataFrame:
        """Flatten ESPN's team-grouped injury payload into a stable row schema."""
        rows: list[dict[str, Any]] = []
        groups = payload.get("injuries", [])
        if not isinstance(groups, list):
            groups = []

        for group in groups:
            if not isinstance(group, dict):
                continue
            # League endpoint commonly groups injury records under each team.
            group_team = group.get("team") or {}
            nested = group.get("injuries")
            if isinstance(nested, list):
                records = nested
            else:
                records = [group]

            for injury in records:
                if not isinstance(injury, dict):
                    continue
                team = injury.get("team") or group_team or {}
                athlete = injury.get("athlete") or {}
                position = athlete.get("position") or {}
                injury_type = injury.get("type") or {}
                fantasy = injury.get("fantasy") or {}
                rows.append({
                    "league": league.upper(),
                    "team_id": _first(team.get("id"), injury.get("teamId")),
                    "team_name": _first(team.get("displayName"), team.get("name")),
                    "team_abbreviation": _first(team.get("abbreviation"), team.get("shortDisplayName")),
                    "player_id": _first(athlete.get("id"), injury.get("athleteId")),
                    "player_name": _first(athlete.get("displayName"), athlete.get("fullName"), injury.get("athleteName")),
                    "position": _first(position.get("abbreviation"), _text(position)),
                    "status": _first(injury.get("status"), fantasy.get("status")),
                    "injury_type": _first(injury_type.get("name"), injury_type.get("description"), fantasy.get("injuryType")),
                    "injury_detail": _first(injury.get("detail"), injury.get("description"), injury.get("location")),
                    "injury_side": injury.get("side"),
                    "injury_date": _first(injury.get("date"), injury.get("updated")),
                    "short_comment": _first(injury.get("shortComment"), injury.get("short_comment")),
                    "long_comment": _first(injury.get("longComment"), injury.get("long_comment"), injury.get("comment")),
                    "source": "ESPN",
                    "source_url": source_url,
                })

        return pd.DataFrame(rows, columns=INJURY_COLUMNS)

    @staticmethod
    def normalize_news(payload: dict[str, Any], league: str, source_url: str) -> pd.DataFrame:
        """Flatten ESPN article records into a stable news schema."""
        articles = payload.get("articles", [])
        if not isinstance(articles, list):
            articles = []
        rows: list[dict[str, Any]] = []
        for article in articles:
            if not isinstance(article, dict):
                continue
            links = article.get("links") or {}
            web_link = links.get("web") or {}
            authors = article.get("byline") or article.get("author")
            if isinstance(authors, list):
                authors = ", ".join(filter(None, (_text(author) for author in authors)))
            rows.append({
                "league": league.upper(),
                "article_id": _first(article.get("id"), article.get("dataSourceIdentifier")),
                "headline": _first(article.get("headline"), article.get("title")),
                "description": _first(article.get("description"), article.get("summary")),
                "published": _first(article.get("published"), article.get("date")),
                "updated": article.get("lastModified"),
                "link": _first(web_link.get("href"), article.get("link")),
                "byline": _text(authors),
                "source": "ESPN",
                "source_url": source_url,
            })
        return pd.DataFrame(rows, columns=NEWS_COLUMNS)
