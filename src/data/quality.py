"""Data-quality checks for normalized player-game data."""
from __future__ import annotations

import pandas as pd


REQUIRED = [
    "league", "season", "player_id", "game_id", "game_date",
    "minutes", "pts", "fga", "fg3a", "fta",
]


def validate_player_game_logs(frame: pd.DataFrame) -> dict[str, object]:
    missing_columns = sorted(set(REQUIRED) - set(frame.columns))
    duplicate_rows = int(frame.duplicated(["league", "game_id", "player_id"]).sum())

    numeric_checks = {
        "negative_minutes": int((frame["minutes"] < 0).sum()),
        "negative_fga": int((frame["fga"] < 0).sum()),
        "negative_fga3": int((frame["fg3a"] < 0).sum()),
        "negative_fta": int((frame["fta"] < 0).sum()),
    }

    return {
        "rows": len(frame),
        "missing_columns": missing_columns,
        "duplicate_player_games": duplicate_rows,
        "numeric_checks": numeric_checks,
        "null_game_ids": int(frame["game_id"].isna().sum()),
        "null_player_ids": int(frame["player_id"].isna().sum()),
    }


def assert_valid_player_game_logs(frame: pd.DataFrame) -> None:
    report = validate_player_game_logs(frame)
    if report["missing_columns"]:
        raise AssertionError(f"Missing required columns: {report['missing_columns']}")
    if report["duplicate_player_games"]:
        raise AssertionError(
            f"Found {report['duplicate_player_games']} duplicate player-game rows."
        )
    for field, count in report["numeric_checks"].items():
        if count:
            raise AssertionError(f"{field}: {count} invalid rows.")
