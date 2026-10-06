"""CLI for downloading and normalizing one NBA/WNBA season.

Examples:
    python -m src.data.ingest_season --league NBA --season 2025-26
    python -m src.data.ingest_season --league WNBA --season 2026
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.data.nba_stats_client import NBA, WNBA, OfficialStatsClient
from src.data.normalize import normalize_player_game_logs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", choices=["NBA", "WNBA"], required=True)
    parser.add_argument("--season", required=True)
    parser.add_argument("--season-type", default="Regular Season")
    parser.add_argument("--output-dir", default="data/raw/player_game_logs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    league = NBA if args.league == "NBA" else WNBA

    client = OfficialStatsClient()
    raw = client.player_game_logs(
        season=args.season,
        season_type=args.season_type,
        league=league,
    )
    normalized = normalize_player_game_logs(raw)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{args.league.lower()}_{args.season}_{args.season_type.lower().replace(' ', '_')}.parquet"
    normalized.to_parquet(output, index=False)

    print(f"Saved {len(normalized):,} player-game rows")
    print(f"Players: {normalized['player_id'].nunique():,}")
    print(f"Games: {normalized['game_id'].nunique():,}")
    print(f"Date range: {normalized['game_date'].min()} -> {normalized['game_date'].max()}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
