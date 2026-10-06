from __future__ import annotations
import numpy as np
import pandas as pd

BASE_METRICS = ["minutes", "fga", "fg3a", "fta", "ast", "tov"]

def add_rolling_role_features(frame: pd.DataFrame, windows=(3, 5, 10)) -> pd.DataFrame:
    out = frame.sort_values(["player_id", "game_date", "game_id"]).copy()
    grouped = out.groupby("player_id", group_keys=False)
    for window in windows:
        for metric in BASE_METRICS:
            out[f"{metric}_roll_{window}"] = grouped[metric].transform(
                lambda s: s.shift(1).rolling(window, min_periods=1).mean()
            )
    return out

def add_opportunity_components(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["opportunity_raw"] = (
        0.30 * out["fga_roll_5"] +
        0.12 * out["fg3a_roll_5"] +
        0.10 * out["fta_roll_5"] +
        0.20 * out["ast_roll_5"] +
        0.08 * out["tov_roll_5"] +
        0.20 * out["minutes_roll_5"]
    )
    return out

def add_role_shift_index(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    short = (out["minutes_roll_3"] + out["fga_roll_3"] + out["fg3a_roll_3"] + out["fta_roll_3"]) / 4.0
    long = (out["minutes_roll_10"] + out["fga_roll_10"] + out["fg3a_roll_10"] + out["fta_roll_10"]) / 4.0
    out["role_shift_index"] = np.where(long.abs() > 1e-9, 100.0 * (short - long) / long.abs(), 0.0)
    return out
