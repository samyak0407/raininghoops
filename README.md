# Raining Hoops 🏀

**Basketball Intelligence Engine**

Raining Hoops is an open basketball analytics lab focused on understanding the game behind the numbers.

The project combines player-role intelligence, matchup analysis, prediction, market intelligence, and transparent model evaluation. The goal is not to produce generic picks—it is to build a basketball research platform that can answer meaningful questions about how players and teams actually perform.

## Research pillars

- **Player Intelligence** — role, opportunity, usage, minutes, impact
- **Team Intelligence** — pace, efficiency, lineups, shot profile, matchup tendencies
- **Matchup Intelligence** — player style × opponent tendencies
- **Prediction** — expected minutes, opportunity, production, and probability
- **Market Intelligence** — player props, prices, line movement, and market-vs-model analysis
- **Model Evaluation** — walk-forward validation, calibration, error analysis, and reproducible results

## Core research ideas

Metric formulas, edge cases, and validation requirements are documented in
[docs/metric_specifications.md](docs/metric_specifications.md). The data-to-model
flow and current system boundaries are in [docs/architecture.md](docs/architecture.md).

### RH Opportunity Index
Estimate the opportunity available to a player before translating opportunity into production.

### Role Shift Index
Detect meaningful changes in a player's role using minutes, usage, shot volume, creation, and teammate availability.

### Matchup Intelligence
Measure how a player's offensive profile interacts with an opponent's defensive tendencies.

### RH Player Impact
A transparent framework for decomposing player contribution across scoring, creation, rebounding, defense, and role/context.

These metrics will be versioned and documented rather than presented as unexplained proprietary scores.

## Data philosophy

Raining Hoops will prioritize free/public data sources and clearly distinguish:

- **Official** — directly sourced from a league or team
- **Derived** — calculated from official/public data
- **Proxy** — an approximation for a concept that requires unavailable tracking data
- **Model-generated** — produced by a statistical/ML model

We will not pretend to have proprietary tracking data that we do not have.

## Modeling philosophy

Complex models must earn their place.

Every major model will be compared against simple baselines such as:

1. Season average
2. Weighted recent average
3. Minutes × opportunity model
4. Gradient-boosted model
5. Ensemble

Evaluation will use time-aware / walk-forward validation to reduce look-ahead bias.

Key metrics may include:

- MAE
- RMSE
- Log Loss
- Brier Score
- Calibration
- Error by player/role/context
- Closing Line Value
- ROI where appropriate

Predictions will be timestamped and stored so that the project can evaluate itself honestly.

## Current laboratory

**WNBA Playoff Lab 2026** is the first live research environment, followed by NBA preseason and the 2026–27 NBA regular season.

Example research questions:

- How does a player's role change when a teammate is unavailable?
- Which matchup characteristics change shot volume?
- Can opportunity be identified before production changes?
- What changed between Game 1 and Game 2 of a playoff series?
- Where does the model systematically fail?

## Repository structure

```text
raininghoops/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   └── snapshots/
├── notebooks/
│   ├── 01_data_exploration/
│   ├── 02_wnba_playoffs/
│   └── 03_nba_preseason/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── matchup/
│   └── evaluation/
└── tests/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Status

🚧 **Active development**

The first milestone is validating public data sources and building a reliable historical data layer before modeling begins.

## Principles

**Transparent. Reproducible. Basketball-first.**

Raining Hoops is a research project. Predictions are evaluated against outcomes rather than selected after the fact.
