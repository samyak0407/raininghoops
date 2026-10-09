"""Fetch ESPN basketball injuries/news and preserve timestamped snapshots.

Examples:
    python -m src.data.ingest_espn --league NBA --resource injuries
    python -m src.data.ingest_espn --league WNBA --resource all
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data.espn_client import ESPNClient
from src.data.player_identity import resolve_player_identity
from src.data.snapshot import save_json_snapshot


def ingest(
    league: str,
    resource: str,
    output_dir: str = "data/processed/espn",
    crosswalk_path: str | None = None,
) -> list[Path]:
    client = ESPNClient()
    league = league.upper()
    resources = ["injuries", "news"] if resource == "all" else [resource]
    written: list[Path] = []
    for item in resources:
        payload, endpoint = getattr(client, item)(league)
        # Use a resource-specific snapshot namespace to avoid same-second filename collisions.
        save_json_snapshot(payload, f"espn_{league.lower()}_{item}", endpoint)
        if item == "injuries":
            frame = client.normalize_injuries(payload, league, endpoint)
            if crosswalk_path:
                crosswalk = pd.read_csv(crosswalk_path, dtype="string")
                frame = resolve_player_identity(frame, crosswalk)
                matched_count = int(frame["match_status"].eq("matched").sum())
                print(f"{league} identity matches: {matched_count}/{len(frame)}")
        else:
            frame = client.normalize_news(payload, league, endpoint)
        retrieved_at = datetime.now(timezone.utc).replace(microsecond=0)
        frame["retrieved_at_utc"] = retrieved_at.isoformat()
        stamp = retrieved_at.strftime("%Y%m%dT%H%M%SZ")
        directory = Path(output_dir) / league.lower()
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{item}_{stamp}.csv"
        frame.to_csv(path, index=False)
        written.append(path)
        print(f"{league} {item}: {len(frame)} rows -> {path}")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ESPN basketball injury and news data.")
    parser.add_argument("--league", choices=["NBA", "WNBA"], default="NBA")
    parser.add_argument("--resource", choices=["injuries", "news", "all"], default="injuries")
    parser.add_argument("--output-dir", default="data/processed/espn")
    parser.add_argument(
        "--crosswalk",
        default=None,
        help="Optional local CSV crosswalk for ESPN-to-league player IDs; no crosswalk is downloaded automatically.",
    )
    args = parser.parse_args()
    ingest(args.league, args.resource, args.output_dir, args.crosswalk)


if __name__ == "__main__":
    main()
