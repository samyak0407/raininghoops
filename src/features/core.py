"""Leakage-safe basketball feature engineering primitives."""
from __future__ import annotations
import numpy as np
import pandas as pd

def add_rolling_player_features(df: pd.DataFrame, windows: tuple[int, ...] = (3, 5, 10)) -> pd.DataFrame:
    required = {"player_id", "game_date", "minutes", "pts", "fga", "fg3a", "fta", "reb", "ast"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    out = df.copy()
    out["game_date"] = pd.to_datetime(out["game_date"])
    out = out.sort_values(["player_id", "game_date", "game_id"], kind="stable").copy()
    grouped = out.groupby("player_id", group_keys=False)
    for window in windows:
        for column in ("minutes", "pts", "fga", "fg3a", "fta", "reb", "ast"):
            out[f"{column}_roll_{window}"] = grouped[column].transform(
                lambda s: s.shift(1).rolling(window, min_periods=1).mean()
            )
    prior_minutes_5 = grouped["minutes"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).sum())
    out["pts_per_min_roll_5"] = grouped["pts"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).sum()) / prior_minutes_5.replace(0, np.nan)
    out["fga_per_min_roll_5"] = grouped["fga"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).sum()) / prior_minutes_5.replace(0, np.nan)
    out["three_rate_roll_5"] = grouped["fg3a"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).sum()) / grouped["fga"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).sum()).replace(0, np.nan)
    return out

def add_role_shift_features(df: pd.DataFrame) -> pd.DataFrame:
    required = {"minutes_roll_5", "minutes_roll_10", "fga_roll_5", "fga_roll_10"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required rolling columns: {sorted(missing)}")
    out = df.copy()
    out["role_shift_minutes"] = (out["minutes_roll_5"] - out["minutes_roll_10"]) / out["minutes_roll_10"].replace(0, np.nan)
    out["role_shift_shot_volume"] = (out["fga_roll_5"] - out["fga_roll_10"]) / out["fga_roll_10"].replace(0, np.nan)
    if {"ast_roll_5", "ast_roll_10"}.issubset(out.columns):
        out["role_shift_creation"] = (out["ast_roll_5"] - out["ast_roll_10"]) / out["ast_roll_10"].replace(0, np.nan)
    else:
        out["role_shift_creation"] = np.nan
    out["role_shift_index"] = out[["role_shift_minutes", "role_shift_shot_volume", "role_shift_creation"]].mean(axis=1, skipna=True)
    return out

def add_opportunity_index(df: pd.DataFrame) -> pd.DataFrame:
    """Create a leakage-safe, within-game-date opportunity percentile.

    Rolling inputs must already exclude the target game. Standardization and
    ranking are performed only against players on the same game date, never
    across the full historical dataset. This is a relative score, not a
    calibrated probability or validated estimate of future production.
    """
    required = {"game_date", "minutes_roll_5", "fga_roll_5", "fta_roll_5", "ast_roll_5"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required opportunity columns: {sorted(missing)}")
    out = df.copy()
    out["game_date"] = pd.to_datetime(out["game_date"], errors="coerce")
    metrics = ["minutes_roll_5", "fga_roll_5", "fta_roll_5", "ast_roll_5"]
    standardized = pd.DataFrame(index=out.index)

    for column in metrics:
        grouped = out.groupby("game_date", dropna=False)[column]
        means = grouped.transform("mean")
        stds = grouped.transform(lambda values: values.std(ddof=0))
        safe_stds = stds.where(stds.ne(0), np.nan)
        standardized[column] = ((out[column] - means) / safe_stds).fillna(0.0)

    out["rh_opportunity_raw"] = standardized.mean(axis=1)
    out["rh_opportunity_index"] = (
        out.groupby("game_date", dropna=False)["rh_opportunity_raw"]
        .rank(method="average", pct=True) * 100
    )
    return out

def add_matchup_pressure(df: pd.DataFrame, player_rate_col: str = "three_rate_roll_5", opponent_allowed_col: str = "opp_three_rate_allowed") -> pd.DataFrame:
    if player_rate_col not in df.columns or opponent_allowed_col not in df.columns:
        raise ValueError(f"Need {player_rate_col!r} and {opponent_allowed_col!r}")
    out = df.copy()
    out["matchup_pressure"] = out[player_rate_col] - out[opponent_allowed_col]
    return out
