import pandas as pd
import pytest

from src.data.normalize import normalize_player_game_logs
from src.data.quality import assert_valid_player_game_logs


def sample_raw() -> pd.DataFrame:
    return pd.DataFrame(
        [{
            "SEASON_YEAR": "2025-26",
            "PLAYER_ID": 1,
            "PLAYER_NAME": "Test Player",
            "TEAM_ID": 2,
            "TEAM_ABBREVIATION": "TST",
            "TEAM_NAME": "Test Team",
            "GAME_ID": "001",
            "GAME_DATE": "2026-01-01",
            "MATCHUP": "TST @ ABC",
            "WL": "W",
            "MIN": "32:00",
            "FGM": 8, "FGA": 15, "FG_PCT": 0.533,
            "FG3M": 2, "FG3A": 6, "FG3_PCT": 0.333,
            "FTM": 4, "FTA": 5, "FT_PCT": 0.8,
            "OREB": 1, "DREB": 5, "REB": 6, "AST": 7,
            "TOV": 2, "STL": 1, "BLK": 0, "BLKA": 1,
            "PF": 2, "PFD": 4, "PTS": 22, "PLUS_MINUS": 5,
        }]
    )


def test_normalize_player_game_logs():
    out = normalize_player_game_logs(sample_raw())
    assert out.loc[0, "home_away"] == "away"
    assert out.loc[0, "pts"] == 22
    assert out.loc[0, "player_id"] == 1


def test_quality_passes():
    out = normalize_player_game_logs(sample_raw())
    assert_valid_player_game_logs(out)


def test_missing_source_column_fails():
    raw = sample_raw().drop(columns=["PTS"])
    with pytest.raises(ValueError):
        normalize_player_game_logs(raw)
