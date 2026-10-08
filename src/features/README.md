# Feature Engineering

Raining Hoops features are designed to answer a basketball question before they are designed to feed a model.

## Current feature layer

- **Pre-game rolling form:** prior-game-only rolling minutes, points, shots, free throws, rebounds, assists, plus rate features.
- **RH Opportunity Index:** transparent 0–100 relative opportunity score built from pre-game minutes, shot volume, free throws, and creation.
- **Role Shift Index:** recent 5-game role signals versus a 10-game baseline for minutes, shot volume, and creation.
- **Matchup Pressure:** player shot-profile tendency minus opponent allowed tendency.

## Leakage rule

Every rolling statistic is shifted by one game before the rolling window is calculated. The current game's outcome can never enter its own features.

## Promotion rule

Every feature must document its source fields, lookback window, timing, leakage risk, and whether it is official, derived, proxy, or model-generated. A feature does not become production-ready solely because it improves one backtest.
