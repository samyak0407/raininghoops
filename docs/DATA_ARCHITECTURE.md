# Raining Hoops Data Architecture

## Analytical grain
One row = one player in one game.

## Layers
1. Raw source data
2. Normalized player-game table
3. Lagged/derived features
4. Timestamped predictions
5. Future-outcome evaluation

## Leakage rules
- Current-game production cannot be a pregame predictor.
- Rolling predictors must exclude the current game.
- Market lines require acquisition timestamps.
- Injuries/news require timestamps.
- Train/test splits must respect chronology.
