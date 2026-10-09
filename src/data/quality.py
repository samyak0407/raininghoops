"""Data-quality checks for normalized player-game data."""
from __future__ import annotations

import pandas as pd


REQUIRED = [
    "league", "season", "player_id", "game_id", "game_date",
    "minutes", "pts", "fga", "fg3a", "fta",
]


def validate_player_game_logs(frame: pd.DataFrame) -> dict[str, object]:
    """Return a diagnostic report even when required columns are missing."""
    missing_columns = sorted(set(REQUIRED) - set(frame.columns))
    duplicate_columns = ["league", "game_id", "player_id"]
    if set(duplicate_columns).issubset(frame.columns):
        duplicate_rows = int(frame.duplicated(duplicate_columns).sum())
    else:
        duplicate_rows = 0

    numeric_checks = {}
    for field, label in (
        ("minutes", "negative_minutes"),
        ("fga", "negative_fga"),
        ("fg3a", "negative_fga3"),
        ("fta", "negative_fta"),
        ("pts", "negative_points"),
        ("reb", "negative_rebounds"),
        ("ast", "negative_assists"),
    ):
        if field in frame.columns:
            values = pd.to_numeric(frame[field], errors="coerce")
            numeric_checks[label] = int((values < 0).sum())

    return {
        "rows": len(frame),
        "missing_columns": missing_columns,
        "duplicate_player_games": duplicate_rows,
        "numeric_checks": numeric_checks,
        "null_game_ids": int(frame["game_id"].isna().sum()) if "game_id" in frame else None,
        "null_player_ids": int(frame["player_id"].isna().sum()) if "player_id" in frame else None,
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
    if report["null_game_ids"]:
        raise AssertionError(f"null_game_ids: {report['null_game_ids']} invalid rows.")
    if report["null_player_ids"]:
        raise AssertionError(f"null_player_ids: {report['null_player_ids']} invalid rows.")
