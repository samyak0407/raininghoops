# Feature Engineering

Raining Hoops features are designed to answer a basketball question before they are designed to feed a model.

## Current feature layer

- **Pre-game rolling form:** prior-game-only rolling minutes, points, shots, free throws, rebounds, assists, plus rate features.
- **RH Opportunity Index:** transparent 0–100 within-game-date relative opportunity percentile built from pre-game minutes, shot volume, free throws, and creation. It is not a probability or validated production estimate.
- **Role Shift Index:** recent 5-game role signals versus a 10-game baseline for minutes, shot volume, and creation.
- **Matchup Pressure:** player shot-profile tendency minus opponent allowed tendency.

## Leakage rule

When a league column is present, player history is grouped by league and player ID to prevent cross-league ID collisions. Every rolling statistic is shifted by one game before the rolling window is calculated. The current game's outcome can never enter its own features. The opportunity index standardizes and ranks players within the same league and game date (or game date when league is not supplied), rather than using full-dataset means or ranks that would change when future rows are added. For a single-player date, the score is 100 by construction because no cross-sectional comparison is possible; treat that case as low-information.

## Promotion rule

Every feature must document its source fields, lookback window, timing, leakage risk, and whether it is official, derived, proxy, or model-generated. A feature does not become production-ready solely because it improves one backtest.
