"""Canonical source registry for Raining Hoops."""
SOURCES = {
    "statpick": {
        "name": "Stat Pick", "kind": "market_research",
        "classification": "external_public_api", "base_url": "https://api.statpick.ai",
        "supports": ["NBA", "WNBA"],
        "notes": "Current prop research; not a general box-score or historical odds API.",
    },
    "nba_stats": {
        "name": "NBA Stats", "kind": "official_league_stats",
        "classification": "official", "base_url": "https://www.nba.com/stats/",
        "supports": ["NBA"],
    },
    "wnba_stats": {
        "name": "WNBA Stats", "kind": "official_league_stats",
        "classification": "official", "base_url": "https://stats.wnba.com/",
        "supports": ["WNBA"],
    },
    "espn": {
        "name": "ESPN", "kind": "injury_and_news_context",
        "classification": "external_public_api",
        "base_url": "https://site.api.espn.com/apis/site/v2/sports/basketball",
        "supports": ["NBA", "WNBA"],
        "endpoints": ["/{league}/injuries", "/{league}/news"],
        "notes": (
            "Supplemental current injury/news context. Public endpoints are undocumented "
            "and may change; coverage and update timing are not guaranteed. Preserve "
            "retrieval timestamps and do not treat ESPN as the sole authoritative injury source."
        ),
    },
}

def get_source(name: str) -> dict:
    try:
        return SOURCES[name]
    except KeyError as exc:
        raise KeyError(f"Unknown Raining Hoops source: {name}") from exc
