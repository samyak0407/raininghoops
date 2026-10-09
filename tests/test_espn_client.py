import pandas as pd
import pytest

from src.data.espn_client import ESPNClient


def test_normalize_grouped_injury_payload():
    payload = {
        "injuries": [{
            "team": {"id": "9", "displayName": "Golden State Warriors", "abbreviation": "GSW"},
            "injuries": [{
                "id": "123",
                "athlete": {
                    "id": "313", "displayName": "Test Player",
                    "position": {"abbreviation": "PG"},
                },
                "status": "Out",
                "type": {"name": "ankle"},
                "detail": "Left ankle sprain",
                "date": "2026-10-08T00:00Z",
            }],
        }]
    }
    frame = ESPNClient.normalize_injuries(payload, "NBA", "https://example.test/injuries")
    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["player_name"] == "Test Player"
    assert row["team_abbreviation"] == "GSW"
    assert row["status"] == "Out"
    assert row["injury_detail"] == "Left ankle sprain"
    assert row["source"] == "ESPN"


def test_empty_injuries_returns_stable_schema():
    frame = ESPNClient.normalize_injuries({"injuries": []}, "WNBA", "https://example.test")
    assert frame.empty
    assert "player_id" in frame.columns
    assert "source_url" in frame.columns


def test_normalize_news_payload():
    payload = {
        "articles": [{
            "id": "abc",
            "headline": "Team update",
            "description": "An update about the team.",
            "published": "2026-10-08T12:00Z",
            "links": {"web": {"href": "https://example.test/story"}},
            "byline": "ESPN Staff",
        }]
    }
    frame = ESPNClient.normalize_news(payload, "WNBA", "https://example.test/news")
    assert len(frame) == 1
    assert frame.iloc[0]["headline"] == "Team update"
    assert frame.iloc[0]["link"] == "https://example.test/story"
    assert frame.iloc[0]["league"] == "WNBA"


def test_unsupported_league_is_rejected():
    with pytest.raises(ValueError, match="use NBA or WNBA"):
        ESPNClient._league_slug("NCAA")
