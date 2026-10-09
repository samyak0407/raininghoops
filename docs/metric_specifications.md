# Raining Hoops metric specifications

These definitions describe the current research implementation, not validated
basketball truths. Names and formulas should be versioned as the project learns
from out-of-sample evaluation.

## 1. Pre-game rolling features

For player p, target game t, statistic x, and window k, the feature is the mean
of the player's previous k games only. The target game's row is shifted out
before calculating the rolling statistic. Early-season windows may use fewer
than k games.

**Inputs:** normalized player-game logs.
**Timing:** computed before the target game, from prior game logs.
**Limitations:** rolling averages do not themselves account for opponent,
teammate availability, changes in minutes, or coaching decisions.

## 2. RH Opportunity Index (current prototype)

For each game date, calculate cross-sectional z-scores for the pre-game
5-game rolling averages of minutes, field-goal attempts, free-throw attempts,
and assists. Average the four z-scores and convert the composite to a percentile
rank from 0 to 100 within that game-date cross-section.

**Interpretation:** relative opportunity profile among the rows present for the
same date, not a probability, player quality rating, or direct forecast of
production.

**Edge cases:** a one-player date has no meaningful cross-sectional comparison;
the implementation returns 100 by construction. Constant inputs contribute a
zero z-score. Missing rolling inputs contribute zero after standardization, so
early-season scores should be flagged as low-information in downstream work.

**Validation required:** compare the score with future minutes, FGA, FTA, usage
proxies, and production on strictly later games; test whether it adds value
beyond simple minutes and shot-volume baselines.

## 3. Role Shift Index (current prototype)

Calculate relative changes between 5-game and 10-game rolling averages for
minutes, field-goal attempts, and assists:

relative_change = (recent_5 - baseline_10) / baseline_10

The current index is the row-wise mean of available component changes.

**Interpretation:** positive values indicate recent increases in the available
role signals; negative values indicate decreases.

**Edge cases:** zero or missing 10-game baselines produce missing component
values. The row-wise mean skips missing components, so downstream reports
should expose component availability and not treat all scores as equally certain.

**Limitations:** it is a descriptive signal, not proof that a player's role has
changed because of an injury. Teammate availability and lineup context are not
yet included in this calculation.

## 4. Matchup Pressure (current prototype)

player_three_rate - opponent_three_rate_allowed

The player input is the prior-game 5-game ratio of total 3-point attempts to
total field-goal attempts. The opponent input must use a compatible definition
and a timestamp available before the prediction.

**Interpretation:** a positive value means the player's recent shot profile is
more three-point-oriented than the opponent's allowed profile under the chosen
definition. It is not automatically a favorable matchup or a points adjustment.

**Validation required:** define the opponent allowed denominator consistently,
account for league/team context, and test whether the feature improves
out-of-sample predictions over a baseline.

## 5. RH Player Impact (planned, not implemented)

This concept should not become a single unexplained score. The planned design is
a transparent decomposition across scoring efficiency, creation, rebounding,
defense, and role/context. Each component needs an explicit definition,
availability requirements, and a decision about whether it is descriptive,
predictive, or causal. No impact formula is claimed by the current code.

## General release criteria

Before a metric is described as validated, it needs:
- documented inputs, units, timing, and missing-data behavior;
- tests for leakage, edge cases, and duplicate/missing records;
- a simple baseline comparison;
- chronological out-of-sample evaluation;
- subgroup/error analysis by league, role, and season;
- a versioned definition and an explicit statement of limitations.
