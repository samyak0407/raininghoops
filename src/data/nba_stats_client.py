"""NBA/WNBA official stats ingestion client.

Uses nba_api to access NBA.com Stats endpoints. The package documents
LeagueGameLog/PlayerGameLogs and supports NBA and WNBA static player/team data.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd
from nba_api.stats.endpoints import playergamelogs


@dataclass
class LeagueConfig:
    name: str
    league_id: str


NBA = LeagueConfig("NBA", "00")
WNBA = LeagueConfig("WNBA", "10")


@dataclass
class OfficialStatsClient:
    request_pause: float = 0.7
    timeout: float = 30.0

    def player_game_logs(
        self,
        season: str,
        season_type: str = "Regular Season",
        league: LeagueConfig = NBA,
    ) -> pd.DataFrame:
        """Fetch the league-wide player game-log table for one season.

        This is intentionally the primary ingestion path: it avoids issuing
        one request per player and gives us a consistent player-game grain.
        """
        time.sleep(self.request_pause)

        endpoint = playergamelogs.PlayerGameLogs(
            season_nullable=season,
            season_type_nullable=season_type,
            league_id_nullable=league.league_id,
            timeout=self.timeout,
        )
        frames = endpoint.get_data_frames()
        if not frames:
            raise RuntimeError(
                f"No player-game-log response for {league.name} {season}."
            )

        frame = frames[0].copy()
        frame["LEAGUE"] = league.name
        return frame
