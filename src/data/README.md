# Data Layer

The data layer is responsible for acquiring, validating, normalizing, and snapshotting public basketball data.

## Current connectors

- **NBA/WNBA Stats:** historical and official league statistics.
- **ESPN:** supplemental current injury reports and basketball news for NBA and WNBA.
- **Stat Pick:** current prop/market research, not a historical box-score or odds archive.

## ESPN injury and news ingestion

The ESPN connector uses the public site API endpoints:

- `https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries`
- `https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/injuries`
- The same league paths ending in `/news` for news articles.

Run from the repository root:

```bash
python -m src.data.ingest_espn --league NBA --resource injuries
python -m src.data.ingest_espn --league WNBA --resource all
```

Each request stores the raw JSON response under `data/snapshots/espn_<league>_<resource>/` with a UTC retrieval timestamp. A normalized CSV is written under `data/processed/espn/<league>/`. The normalized rows retain the source URL; the raw snapshots preserve fields not yet mapped into the stable schema.

## Reliability and temporal rules

- ESPN's public endpoints are undocumented and may change without notice.
- Injury coverage and update timing are not guaranteed; an empty response means only that the endpoint returned no records at retrieval time.
- Treat ESPN as a supplemental context source, not the sole authoritative injury source.
- Keep the retrieval timestamp separate from the injury's reported date. Never backdate an observation to the reported injury date.
- Join injury/news observations to a prediction only when the observation was available by that prediction's timestamp.
- Injury-related role adjustments should be derived features with documented rules, not assumed causal effects.

## Data engineering principles

1. Stable source connectors
2. Raw-data preservation
3. Normalized schemas
4. Timestamped snapshots
5. Data-quality checks
6. Provenance metadata

Live access is not required for unit tests; tests should use representative mocked responses.


## Player identity resolution

The ESPN injury `player_id` is an ESPN athlete ID, not automatically the NBA
or WNBA stats provider's player ID. The resolver in
`src/data/player_identity.py` maps IDs only through a supplied crosswalk and
requires league and team consistency. It falls back to a unique exact normalized
name + team match only when the ESPN ID is absent from the crosswalk. Ambiguous,
conflicting, or low-confidence records remain unresolved.

Prepare and review a crosswalk CSV with a `league` column, ESPN athlete ID,
league player ID/name, team abbreviation, and preferably `match_confidence`.
Common field aliases such as `espn_athlete_id` and `nba_player_id` are
supported. Keep a source/version/as-of date for the crosswalk; do not mix
stale rosters into current injury matching.

Optionally enrich ESPN injury rows during ingestion:

```bash
python -m src.data.ingest_espn --league NBA --resource injuries --crosswalk data/reference/player_id_crosswalk.csv
```

Without `--crosswalk`, ingestion continues to save the normalized ESPN data
without league-ID enrichment. Both injury and news CSVs include
`retrieved_at_utc`; this is the observation timestamp and must not be replaced
with the injury's reported date.
