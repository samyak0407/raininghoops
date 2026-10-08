# Evaluation

Raining Hoops evaluates predictions chronologically, not randomly.

## Metrics

- Regression: MAE, RMSE
- Probability: Log Loss, Brier Score, calibration
- Diagnostics: error by player, role, opponent, rest context, and minutes bucket

## Rules

1. Train only on information available before the prediction timestamp.
2. Store prediction timestamp and data snapshot timestamp.
3. Never tune on the final evaluation period.
4. Compare against simple baselines before complex models.
5. Publish failures as well as wins.
