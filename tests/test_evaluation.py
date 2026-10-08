import numpy as np
from src.evaluation.metrics import regression_metrics, classification_metrics, calibration_table

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
