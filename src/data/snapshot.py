"""Utilities for preserving raw API responses with provenance."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def save_json_snapshot(payload: dict[str, Any], source: str, endpoint: str,
                       output_dir: str = "data/snapshots") -> Path:
    timestamp = datetime.now(timezone.utc)
    directory = Path(output_dir) / source
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
    envelope = {"source": source, "endpoint": endpoint,
                "retrieved_at_utc": timestamp.isoformat(), "payload": payload}
    path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    return path
