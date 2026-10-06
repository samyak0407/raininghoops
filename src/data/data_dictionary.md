# Raining Hoops — Initial Data Dictionary

## Player game

| Field | Description | Classification |
|---|---|---|
| game_id | Unique game identifier | Official |
| game_date | Game date | Official |
| season | League season | Official |
| season_type | Preseason / regular season / playoffs | Official |
| player_id | Stable player identifier | Official |
| player_name | Player identifier/display name | Official |
| team_id | Team identifier | Official |
| opponent_id | Opponent identifier | Official |
| home_away | Home / away | Derived |
| starter | Whether player started | Official |
| minutes | Minutes played | Official |
| points | Points | Official |
| fga | Field-goal attempts | Official |
| fg3a | Three-point attempts | Official |
| fta | Free-throw attempts | Official |
| rebounds | Total rebounds | Official |
| assists | Assists | Official |
| turnovers | Turnovers | Official |
| steals | Steals | Official |
| blocks | Blocks | Official |

## Context / role

rest_days, rolling minutes/usage/FGA/3PA, teammate availability, and
role_shift_index will be derived or model-generated features.

## Market snapshot

Every market record must retain snapshot_timestamp_utc, sport, game/player,
market, line, prices, source, and source endpoint.

**Critical rule:** never evaluate a historical prediction using a market line
that became available after the prediction timestamp.
