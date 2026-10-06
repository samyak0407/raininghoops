from __future__ import annotations
from pathlib import Path
from typing import Iterable
from src.data.nba_stats_client import NBA, WNBA, LeagueConfig, OfficialStatsClient
from src.data.normalize import normalize_player_game_logs
from src.data.quality import assert_valid_player_game_logs

def league_from_name(name: str) -> LeagueConfig:
    if name.upper() == "NBA": return NBA
    if name.upper() == "WNBA": return WNBA
    raise ValueError("league must be NBA or WNBA")

def ingest(league: LeagueConfig, seasons: Iterable[str],
           season_types: Iterable[str],
           output_dir: str = "data/raw/player_game_logs") -> list[Path]:
    client = OfficialStatsClient()
    outputs = []
    for season in seasons:
        for season_type in season_types:
            raw = client.player_game_logs(season, season_type, league)
            normalized = normalize_player_game_logs(raw)
            assert_valid_player_game_logs(normalized)
            path = Path(output_dir) / f"{league.name.lower()}_{season}_{season_type.lower().replace(' ', '_')}.parquet"
            path.parent.mkdir(parents=True, exist_ok=True)
            normalized.to_parquet(path, index=False)
            outputs.append(path)
    return outputs
