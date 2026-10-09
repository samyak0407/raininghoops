# Raining Hoops system architecture

## Design goal

Build a reproducible basketball intelligence pipeline whose outputs can be
traced to source observations, feature definitions, and model versions. The
system is designed to run historical research locally first; live feeds are
optional inputs, not prerequisites for unit testing.

## Logical flow

```text
Public / league sources
  ├── NBA / WNBA player-game logs
  ├── ESPN injury and news snapshots
  └── StatPick market context (where available)
             |
             v
Raw snapshots + retrieval timestamps + source metadata
             |
             v
Normalization + schema and quality checks
             |
             v
Identity resolution (league-scoped IDs; unresolved cases stay unresolved)
             |
             v
Point-in-time feature tables
  ├── player form / opportunity
  ├── role shift
  └── matchup context
             |
             v
Baselines -> candidate models -> timestamped predictions
             |
             v
Chronological evaluation + calibration + error analysis
```

## Contracts and boundaries

- **Source clients** retrieve data and preserve raw payloads. They do not infer
  player impact or modify predictions.
- **Normalization** converts provider-specific field names and IDs into stable
  contracts. Provider IDs remain separate until an explicit crosswalk is used.
- **Quality checks** detect missing schema fields, duplicate player-game rows,
  null identifiers, and impossible negative count/minute values.
- **Identity resolution** is league-aware and conservative. Exact IDs still
  require team consistency; exact name + team is only a fallback when unique.
  Ambiguous and conflicting matches are retained as unresolved.
- **Features** must use only information available by the target prediction
  timestamp. Feature formulas and versions should be documented.
- **Models** must be compared with simple baselines and must not own source
  acquisition logic.
- **Evaluation** uses chronological splits and never tunes on the final test
  period.
- **Predictions and context** should eventually store prediction_timestamp_utc,
  source snapshot timestamps, feature version, model version, and target game ID.

## Data categories

- **Official:** published by a league/team source.
- **External public context:** e.g., ESPN injury/news snapshots; useful but
  coverage/timing is not guaranteed.
- **Derived:** deterministic calculations from recorded source fields.
- **Proxy:** an approximation where direct tracking/context data is unavailable.
- **Model-generated:** an output from a trained statistical model.

## Current limitations

- Historical league-data acquisition has not yet been validated end-to-end in
  the current environment.
- ESPN identity resolution requires a real, current, league-specific crosswalk;
  the resolver does not download or fabricate one.
- Opportunity, role-shift, and matchup formulas are prototypes, not proven
  predictive signals.
- No live prediction should be treated as production-ready until point-in-time
  snapshots, real-data tests, and chronological evaluation are complete.
