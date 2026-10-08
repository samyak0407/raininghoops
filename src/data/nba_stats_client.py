"""NBA/WNBA official stats ingestion client.

Uses nba_api to access NBA.com Stats endpoints. Requests are deliberately
chunked by month because large season-wide responses can time out from
cloud-hosted environments.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd
import requests
from nba_api.stats.endpoints import playergamelogs


@dataclass
class LeagueConfig:
    name: str
    league_id: str


NBA = LeagueConfig("NBA", "00")
WNBA = LeagueConfig("WNBA", "10")


DEFAULT_HEADERS = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
}


@dataclass
class OfficialStatsClient:
    request_pause: float = 1.0
    timeout: float = 90.0
    max_retries: int = 3

    def _fetch_month(
        self,
        season: str,
        season_type: str,
        league: LeagueConfig,
        month: int,
    ) -> pd.DataFrame:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                time.sleep(self.request_pause)
                endpoint = playergamelogs.PlayerGameLogs(
                    season_nullable=season,
                    season_type_nullable=season_type,
                    league_id_nullable=league.league_id,
                    month_nullable=str(month),
                    headers=DEFAULT_HEADERS,
                    timeout=self.timeout,
                )
                frames = endpoint.get_data_frames()
                if not frames:
                    return pd.DataFrame()

                frame = frames[0].copy()
                frame["LEAGUE"] = league.name
                return frame

            except requests.exceptions.RequestException as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)

        raise RuntimeError(
            f"NBA.com request failed for {league.name} {season}, month {month} "
            f"after {self.max_retries} attempts."
        ) from last_error

    def player_game_logs(
        self,
        season: str,
        season_type: str = "Regular Season",
        league: LeagueConfig = NBA,
    ) -> pd.DataFrame:
        """Fetch league-wide player game logs in monthly chunks.

        Monthly requests keep payloads smaller and make cloud-hosted ingestion
        substantially more resilient to NBA.com read timeouts.
        """
        frames: list[pd.DataFrame] = []

        for month in range(1, 13):
            frame = self._fetch_month(
                season=season,
                season_type=season_type,
                league=league,
                month=month,
            )
            if not frame.empty:
                frames.append(frame)

        if not frames:
            raise RuntimeError(
                f"No player-game-log response for {league.name} {season}."
            )

        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(
            subset=["GAME_ID", "PLAYER_ID"],
            keep="last",
        )
        return combined
