"""Prediction metrics for Raining Hoops evaluation."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, log_loss, brier_score_loss

def regression_metrics(y_true, y_pred) -> dict[str, float]:
    return {"mae": float(mean_absolute_error(y_true, y_pred)), "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred)))}

def classification_metrics(y_true, probability, threshold: float = 0.5) -> dict[str, float]:
    probability = np.asarray(probability, dtype=float)
    labels = (probability >= threshold).astype(int)
    return {"log_loss": float(log_loss(y_true, probability, labels=[0, 1])), "brier_score": float(brier_score_loss(y_true, probability)), "accuracy_at_threshold": float(np.mean(labels == np.asarray(y_true)))}

def calibration_table(y_true, probability, bins: int = 10) -> pd.DataFrame:
    frame = pd.DataFrame({"y_true": y_true, "probability": probability})
    frame["bin"] = pd.cut(frame["probability"], bins=np.linspace(0, 1, bins + 1), include_lowest=True)
    return frame.groupby("bin", observed=False).agg(predicted_probability=("probability", "mean"), observed_rate=("y_true", "mean"), n=("y_true", "size")).reset_index()


def chronological_split(
    frame: pd.DataFrame,
    date_col: str = "game_date",
    train_end: str | pd.Timestamp = "2025-12-31",
    validation_end: str | pd.Timestamp = "2026-06-30",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split rows by date into train, validation, and test periods.

    The train period includes dates <= train_end; validation includes dates
    after train_end through validation_end; test includes dates after
    validation_end. Rows with invalid/missing dates are rejected rather than
    silently discarded. The caller must choose cutoffs appropriate to the
    season and prediction task.
    """
    if date_col not in frame.columns:
        raise ValueError(f"Missing date column: {date_col}")
    dates = pd.to_datetime(frame[date_col], errors="coerce")
    if dates.isna().any():
        raise ValueError(f"Column {date_col!r} contains missing or invalid dates")
    train_cutoff = pd.Timestamp(train_end)
    validation_cutoff = pd.Timestamp(validation_end)
    if train_cutoff >= validation_cutoff:
        raise ValueError("train_end must be earlier than validation_end")

    train = frame.loc[dates <= train_cutoff].copy()
    validation = frame.loc[(dates > train_cutoff) & (dates <= validation_cutoff)].copy()
    test = frame.loc[dates > validation_cutoff].copy()
    return train, validation, test
