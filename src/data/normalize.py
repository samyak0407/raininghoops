"""Normalize official player-game data into the Raining Hoops contract."""
from __future__ import annotations

import pandas as pd


COLUMN_MAP = {
    "SEASON_YEAR": "season",
    "SEASON_TYPE": "season_type",
    "PLAYER_ID": "player_id",
    "PLAYER_NAME": "player_name",
    "TEAM_ID": "team_id",
    "TEAM_ABBREVIATION": "team_abbreviation",
    "TEAM_NAME": "team_name",
    "GAME_ID": "game_id",
    "GAME_DATE": "game_date",
    "MATCHUP": "matchup",
    "WL": "result",
    "MIN": "minutes",
    "FGM": "fgm",
    "FGA": "fga",
    "FG_PCT": "fg_pct",
    "FG3M": "fg3m",
    "FG3A": "fg3a",
    "FG3_PCT": "fg3_pct",
    "FTM": "ftm",
    "FTA": "fta",
    "FT_PCT": "ft_pct",
    "OREB": "oreb",
    "DREB": "dreb",
    "REB": "reb",
    "AST": "ast",
    "TOV": "tov",
    "STL": "stl",
    "BLK": "blk",
    "BLKA": "blka",
    "PF": "pf",
    "PFD": "pfd",
    "PTS": "pts",
    "PLUS_MINUS": "plus_minus",
}


def _parse_minutes(series: pd.Series) -> pd.Series:
    """Convert NBA-style minutes such as '32:15' or numeric minutes to floats."""
    text = series.astype("string").str.strip()

    colon_mask = text.str.contains(":", na=False)
    result = pd.to_numeric(text, errors="coerce")

    if colon_mask.any():
        parts = text[colon_mask].str.split(":", n=1, expand=True)
        mins = pd.to_numeric(parts[0], errors="coerce")
        secs = pd.to_numeric(parts[1], errors="coerce")
        result.loc[colon_mask] = mins + secs / 60.0

    return result


def normalize_player_game_logs(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize an official player-game-log dataframe.

    The official API client adds LEAGUE metadata before calling this function.
    Tests and other callers may omit it; in that case the contract uses UNKNOWN.
    """
    required_columns = set(COLUMN_MAP) - {"SEASON_TYPE"}
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        raise ValueError(f"Official stats response is missing columns: {missing}")

    out = frame.rename(columns=COLUMN_MAP).copy()

    if "SEASON_TYPE" not in frame.columns:
        out["season_type"] = "UNKNOWN"

    if "LEAGUE" in frame.columns:
        out["league"] = frame["LEAGUE"].astype("string")
    elif "league" not in out.columns:
        out["league"] = "UNKNOWN"

    out["game_date"] = pd.to_datetime(out["game_date"], errors="coerce")
    out["minutes"] = _parse_minutes(out["minutes"])

    # Matchup strings normally look like "LAL vs. BOS" or "LAL @ BOS".
    out["home_away"] = out["matchup"].astype("string").map(
        lambda x: "away" if "@" in x else "home"
    )

    # Keep only the stable normalized contract plus league metadata.
    keep = [
        "league", "season", "season_type", "player_id", "player_name", "team_id",
        "team_abbreviation", "team_name", "game_id", "game_date",
        "matchup", "home_away", "result", "minutes", "fgm", "fga",
        "fg_pct", "fg3m", "fg3a", "fg3_pct", "ftm", "fta", "ft_pct",
        "oreb", "dreb", "reb", "ast", "tov", "stl", "blk", "blka",
        "pf", "pfd", "pts", "plus_minus",
    ]

    return (
        out[keep]
        .sort_values(["game_date", "game_id", "player_id"])
        .reset_index(drop=True)
    )
