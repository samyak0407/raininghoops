"""NBA/WNBA official stats ingestion client.

Primary source: NBA.com Stats via nba_api.

For WNBA ingestion, a versioned SportsDataverse release is used as a
fallback when stats.nba.com is unreachable from the execution environment.
This preserves reproducibility without requiring paid data.
"""
from __future__ import annotations

import io
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


WNBA_FALLBACK_URL = (
    "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
    "wnba_stats_player_game_logs/player_game_logs_{season}.parquet"
)


@dataclass
class OfficialStatsClient:
    request_pause: float = 1.0
    timeout: float = 90.0
    max_retries: int = 3
    last_source: str = "NBA.com Stats via nba_api"

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

    @staticmethod
    def _fallback_months(league: LeagueConfig) -> range:
        # Restrict requests to months in which regular-season games can exist.
        if league.name == "WNBA":
            return range(5, 10)
        return range(10, 13)

    def _fetch_wnba_fallback(self, season: str, season_type: str) -> pd.DataFrame:
        if season_type != "Regular Season":
            raise RuntimeError(
                "The WNBA fallback currently supports Regular Season only."
            )

        url = WNBA_FALLBACK_URL.format(season=season)
        response = requests.get(
            url,
            timeout=self.timeout,
            headers={"User-Agent": DEFAULT_HEADERS["User-Agent"]},
        )
        response.raise_for_status()

        frame = pd.read_parquet(io.BytesIO(response.content))

        # The published release contains both player and team rows and both
        # regular-season and playoff records. Keep only player regular-season
        # rows so the output matches our player-game-log contract.
        if "player_id" in frame.columns:
            frame = frame[frame["player_id"].notna()].copy()
        if "season_type" in frame.columns:
            frame = frame[
                frame["season_type"].astype(str).str.lower().eq("regular-season")
            ].copy()

        rename_map = {
            "player_id": "PLAYER_ID",
            "player_name": "PLAYER_NAME",
            "team_id": "TEAM_ID",
            "team_abbreviation": "TEAM_ABBREVIATION",
            "game_id": "GAME_ID",
            "game_date": "GAME_DATE",
            "min": "MIN",
            "fgm": "FGM",
            "fga": "FGA",
            "fg3m": "FG3M",
            "fg3a": "FG3A",
            "ftm": "FTM",
            "fta": "FTA",
            "oreb": "OREB",
            "dreb": "DREB",
            "reb": "REB",
            "ast": "AST",
            "stl": "STL",
            "blk": "BLK",
            "tov": "TOV",
            "pf": "PF",
            "pts": "PTS",
            "plus_minus": "PLUS_MINUS",
            "wl": "WL",
            "matchup": "MATCHUP",
        }
        frame = frame.rename(columns=rename_map)
        frame["LEAGUE"] = "WNBA"

        self.last_source = "SportsDataverse WNBA Stats release (NBA.com Stats source)"
        return frame

    def player_game_logs(
        self,
        season: str,
        season_type: str = "Regular Season",
        league: LeagueConfig = NBA,
    ) -> pd.DataFrame:
        """Fetch league-wide player game logs.

        NBA.com Stats is attempted first. If WNBA requests fail because
        stats.nba.com is unreachable, the published SportsDataverse WNBA
        Stats release is used as a reproducible fallback.
        """
        frames: list[pd.DataFrame] = []

        months = (
            self._fallback_months(league)
            if league.name == "WNBA"
            else range(10, 13)
        )

        try:
            for month in months:
                frame = self._fetch_month(
                    season=season,
                    season_type=season_type,
                    league=league,
                    month=month,
                )
                if not frame.empty:
                    frames.append(frame)
        except RuntimeError:
            if league.name != "WNBA":
                raise
            return self._fetch_wnba_fallback(
                season=season,
                season_type=season_type,
            )

        if not frames:
            if league.name == "WNBA":
                return self._fetch_wnba_fallback(
                    season=season,
                    season_type=season_type,
                )
            raise RuntimeError(
                f"No player-game-log response for {league.name} {season}."
            )

        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(
            subset=["GAME_ID", "PLAYER_ID"],
            keep="last",
        )
        self.last_source = "NBA.com Stats via nba_api"
        return combined
