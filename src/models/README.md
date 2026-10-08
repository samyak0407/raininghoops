# Models

Models come after feature validation.

## Baseline ladder

1. Season average
2. Weighted recent average
3. Minutes × per-minute production
4. Gradient-boosted model
5. Ensemble

A complex model must beat the appropriate baseline on a held-out future period before promotion.

## Prediction contract

Every prediction should contain prediction timestamp, game ID, player ID, target, predicted value, probability when applicable, model version, feature snapshot/version, and data snapshot timestamp.
