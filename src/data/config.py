from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "seasons.json"

def load_seasons() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
