"""CLI for downloading, validating, and normalizing one NBA/WNBA season.

Examples:
    python -m src.data.ingest_season --league NBA --season 2025-26
    python -m src.data.ingest_season --league WNBA --season 2026
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.data.nba_stats_client import NBA, WNBA, OfficialStatsClient
from src.data.wnba_release_client import WNBAStatsReleaseClient
from src.data.normalize import normalize_player_game_logs
from src.data.quality import assert_valid_player_game_logs, validate_player_game_logs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", choices=["NBA", "WNBA"], required=True)
    parser.add_argument("--season", required=True)
    parser.add_argument("--season-type", default="Regular Season")
    parser.add_argument("--output-dir", default="data/raw/player_game_logs")
    parser.add_argument("--source", choices=["official", "wnba-release"], default="official")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    league = NBA if args.league == "NBA" else WNBA

    if args.source == "wnba-release":
        if args.league != "WNBA":
            raise ValueError("--source wnba-release is only valid with --league WNBA.")
        client = WNBAStatsReleaseClient()
        raw = client.player_game_logs(
            season=args.season,
            season_type=args.season_type,
        )
        source_label = "WNBA Stats official endpoints via SportsDataverse versioned release"
    else:
        client = OfficialStatsClient()
        raw = client.player_game_logs(
            season=args.season,
            season_type=args.season_type,
            league=league,
        )
        source_label = "WNBA/NBA Stats via nba_api"
    normalized = normalize_player_game_logs(raw)

    # Fail closed: never persist a dataset that violates the core contract.
    assert_valid_player_game_logs(normalized)
    quality_report = validate_player_game_logs(normalized)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    season_type_slug = args.season_type.lower().replace(" ", "_")
    output = output_dir / (
        f"{args.league.lower()}_{args.season}_{season_type_slug}.parquet"
    )
    normalized.to_parquet(output, index=False)

    manifest = {
        "league": args.league,
        "season": args.season,
        "season_type": args.season_type,
        "source": source_label,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": len(normalized),
        "players": int(normalized["player_id"].nunique()),
        "games": int(normalized["game_id"].nunique()),
        "date_min": str(normalized["game_date"].min()),
        "date_max": str(normalized["game_date"].max()),
        "quality": quality_report,
        "output": str(output),
    }
    manifest_path = output.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Saved {len(normalized):,} player-game rows")
    print(f"Players: {normalized['player_id'].nunique():,}")
    print(f"Games: {normalized['game_id'].nunique():,}")
    print(f"Date range: {normalized['game_date'].min()} -> {normalized['game_date'].max()}")
    print(f"Output: {output}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
