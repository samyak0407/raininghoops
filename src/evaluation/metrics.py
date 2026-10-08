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
