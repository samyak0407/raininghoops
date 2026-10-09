# Player identity resolution

The ESPN injury feed's athlete ID is not assumed to be the same as an NBA or WNBA
player ID. Use an explicit crosswalk with a league column and current team context.

## Crosswalk schema

The resolver accepts these canonical concepts (some common source aliases are
also accepted):

- `league`: `NBA` or `WNBA`
- `espn_player_id` / `espn_athlete_id`
- `league_player_id` / `nba_player_id` / `wnba_player_id`
- `league_player_name` / `nba_player_name` / `wnba_player_name`
- `team_abbreviation`
- optional `match_confidence` (or `confidence`)

Do not fabricate a crosswalk. Keep the source, season/as-of date, and version of
the crosswalk with the downloaded reference file. For multi-season crosswalks,
retain the season or effective dates and prepare a current-season slice before
resolving current injuries.

## Match policy

1. Match by ESPN athlete ID within the same league, and require team consistency.
2. If the ESPN ID is absent from the crosswalk, allow only a unique exact
   normalized name + team + league match.
3. Leave team conflicts, duplicate candidates, low-confidence mappings, and
   missing matches unresolved. Fuzzy name similarity may suggest candidates for
   manual review but must not automatically attach an injury to a player.
4. Keep ESPN's ID and the resolved league ID in separate columns.
5. Store the retrieval timestamp separately from the injury report date.

## Example

```python
from src.data.player_identity import resolve_player_identity

resolved = resolve_player_identity(injury_frame, crosswalk_frame)
matched = resolved[resolved["match_status"] == "matched"]
review = resolved[resolved["match_status"] == "unresolved"]
```

The function uses no network access. Unit tests use synthetic records only and
do not establish that any external crosswalk is complete or accurate.
