"""Client for the versioned WNBA Stats release published by SportsDataverse.

The release is built from stats.wnba.com and provides season-level player game logs
without requiring direct access to stats.nba.com from the user's environment.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


BASE_URL = (
    "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
    "wnba_stats_player_game_logs"
)

COLUMN_MAP = {
    "season": "SEASON_YEAR",
    "team_id": "TEAM_ID",
    "team_abbreviation": "TEAM_ABBREVIATION",
    "team_name": "TEAM_NAME",
    "game_id": "GAME_ID",
    "game_date": "GAME_DATE",
    "matchup": "MATCHUP",
    "wl": "WL",
    "player_id": "PLAYER_ID",
    "player_name": "PLAYER_NAME",
    "min": "MIN",
    "fgm": "FGM",
    "fga": "FGA",
    "fg_pct": "FG_PCT",
    "fg3m": "FG3M",
    "fg3a": "FG3A",
    "fg3_pct": "FG3_PCT",
    "ftm": "FTM",
    "fta": "FTA",
    "ft_pct": "FT_PCT",
    "oreb": "OREB",
    "dreb": "DREB",
    "reb": "REB",
    "ast": "AST",
    "tov": "TOV",
    "stl": "STL",
    "blk": "BLK",
    "blka": "BLKA",
    "pf": "PF",
    "pfd": "PFD",
    "pts": "PTS",
    "plus_minus": "PLUS_MINUS",
}


@dataclass
class WNBAStatsReleaseClient:
    """Load a versioned WNBA Stats player-game-log release."""

    base_url: str = BASE_URL
    timeout: int = 120

    def player_game_logs(
        self,
        season: int | str,
        season_type: str | None = None,
    ) -> pd.DataFrame:
        url = f"{self.base_url}/player_game_logs_{season}.csv"
        frame = pd.read_csv(url, low_memory=False)

        if "player_id" not in frame.columns:
            raise ValueError("WNBA Stats release is missing player_id.")
        frame = frame[frame["player_id"].notna()].copy()

        if season_type:
            wanted = season_type.lower().replace(" ", "-")
            if "season_type" not in frame.columns:
                raise ValueError("WNBA Stats release is missing season_type.")
            frame = frame[
                frame["season_type"].astype(str).str.lower().eq(wanted)
            ].copy()

        missing = [column for column in COLUMN_MAP if column not in frame.columns]
        if missing:
            raise ValueError(
                "WNBA Stats release is missing expected columns: "
                + ", ".join(missing)
            )

        raw = frame[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)
        raw["SEASON_TYPE"] = frame["season_type"].astype("string")
        raw["LEAGUE"] = "WNBA"
        return raw.reset_index(drop=True)
