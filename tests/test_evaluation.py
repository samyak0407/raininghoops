import numpy as np
import pandas as pd
from src.evaluation.metrics import regression_metrics, classification_metrics, calibration_table, chronological_split

def test_regression_metrics():
    result=regression_metrics([1,2,3],[1,3,2])
    assert result["mae"] == 2/3
    assert round(result["rmse"],6) == round(np.sqrt(2/3),6)

def test_classification_metrics():
    result=classification_metrics([0,1,1,0],[0.1,0.8,0.7,0.2])
    assert 0 <= result["brier_score"] <= 1 and 0 <= result["accuracy_at_threshold"] <= 1

def test_calibration_table():
    table=calibration_table([0,1,1,0],[0.1,0.8,0.7,0.2],bins=2)
    assert {"predicted_probability","observed_rate","n"} <= set(table.columns)


def test_chronological_split_respects_cutoffs():
    frame = pd.DataFrame({"game_date": pd.to_datetime([
        "2025-01-01", "2025-12-31", "2026-01-01", "2026-06-30", "2026-07-01"
    ]), "value": [1, 2, 3, 4, 5]})
    train, validation, test = chronological_split(
        frame, train_end="2025-12-31", validation_end="2026-06-30"
    )
    assert train["value"].tolist() == [1, 2]
    assert validation["value"].tolist() == [3, 4]
    assert test["value"].tolist() == [5]


def test_chronological_split_rejects_invalid_dates():
    frame = pd.DataFrame({"game_date": ["not-a-date"], "value": [1]})
    try:
        chronological_split(frame, train_end="2025-12-31", validation_end="2026-06-30")
    except ValueError as exc:
        assert "invalid dates" in str(exc)
    else:
        raise AssertionError("Expected invalid dates to raise ValueError")
