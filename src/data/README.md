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
