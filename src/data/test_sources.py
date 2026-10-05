"""Smoke tests for Raining Hoops public data sources.

This script intentionally performs lightweight requests only. It does not
download a historical dataset yet. The goal is to confirm connectivity and
record the shape of each source before we lock the data architecture.

Run:
    python src/data/test_sources.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class SourceResult:
    name: str
    url: str
    ok: bool
    status_code: int | None
    detail: str


TIMEOUT = 15


def check_url(name: str, url: str) -> SourceResult:
    try:
        response = requests.get(
            url,
            timeout=TIMEOUT,
            headers={"User-Agent": "RainingHoops/0.1 (research project)"},
        )
        content_type = response.headers.get("content-type", "")
        detail = f"{content_type}; {len(response.content):,} bytes"
        return SourceResult(
            name=name,
            url=url,
            ok=response.ok,
            status_code=response.status_code,
            detail=detail,
        )
    except requests.RequestException as exc:
        return SourceResult(
            name=name,
            url=url,
            ok=False,
            status_code=None,
            detail=str(exc),
        )


def main() -> None:
    sources = [
        (
            "StatPick developers API",
            "https://www.statpick.ai/developers",
        ),
        (
            "StatPick API root",
            "https://www.statpick.ai/api",
        ),
        (
            "NBA website",
            "https://www.nba.com/",
        ),
        (
            "WNBA website",
            "https://www.wnba.com/",
        ),
    ]

    results = [check_url(name, url) for name, url in sources]

    print("\nRaining Hoops — Source Smoke Test")
    print("=" * 50)

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(
            f"[{status}] {result.name}: "
            f"{result.status_code or 'NO RESPONSE'} — {result.detail}"
        )

    print("\nRaw result:")
    print(json.dumps([result.__dict__ for result in results], indent=2))


if __name__ == "__main__":
    main()
