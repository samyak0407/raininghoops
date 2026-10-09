import pandas as pd
import pytest

from src.data.player_identity import normalize_player_name, resolve_player_identity


def injury(player_id="espn-1", player_name="Jordan Example", team="ABC", league="NBA"):
    return pd.DataFrame([{
        "league": league, "player_id": player_id, "player_name": player_name,
        "team_abbreviation": team, "status": "Out",
    }])


def crosswalk(rows=None):
    if rows is None:
        rows = [{
            "league": "NBA", "espn_athlete_id": "espn-1", "nba_player_id": 1001,
            "nba_player_name": "Jordan Example", "team_abbreviation": "ABC",
            "match_confidence": 0.99,
        }]
    return pd.DataFrame(rows)


def test_name_normalization_handles_accents_and_punctuation():
    assert normalize_player_name("José A. Example") == "jose a example"


def test_exact_espn_id_and_team_match():
    result = resolve_player_identity(injury(), crosswalk())
    row = result.iloc[0]
    assert row["resolved_player_id"] == "1001"
    assert row["match_status"] == "matched"
    assert row["match_method"] == "espn_id_crosswalk"
    assert row["match_confidence"] == 0.99


def test_name_team_fallback_when_espn_id_is_not_in_crosswalk():
    result = resolve_player_identity(injury(player_id="new-espn-id"), crosswalk())
    row = result.iloc[0]
    assert row["resolved_player_id"] == "1001"
    assert row["match_method"] == "exact_name_team"
    assert row["match_status"] == "matched"


def test_team_conflict_is_not_silently_matched():
    result = resolve_player_identity(injury(team="XYZ"), crosswalk())
    row = result.iloc[0]
    assert row["match_status"] == "unresolved"
    assert row["resolved_player_id"] is None
    assert row["match_reason"] == "espn_id_team_conflict"


def test_same_name_on_different_teams_does_not_match_wrong_team():
    rows = [
        {"league": "NBA", "espn_athlete_id": "other", "nba_player_id": 1001,
         "nba_player_name": "Jordan Example", "team_abbreviation": "XYZ", "match_confidence": 0.99},
        {"league": "NBA", "espn_athlete_id": "third", "nba_player_id": 1002,
         "nba_player_name": "Jordan Example", "team_abbreviation": "ABC", "match_confidence": 0.99},
    ]
    result = resolve_player_identity(injury(player_id="unknown"), crosswalk(rows))
    assert result.iloc[0]["resolved_player_id"] == "1002"


def test_ambiguous_name_team_match_is_unresolved():
    rows = [
        {"league": "NBA", "espn_athlete_id": "a", "nba_player_id": 1001,
         "nba_player_name": "Jordan Example", "team_abbreviation": "ABC", "match_confidence": 0.99},
        {"league": "NBA", "espn_athlete_id": "b", "nba_player_id": 1002,
         "nba_player_name": "Jordan Example", "team_abbreviation": "ABC", "match_confidence": 0.99},
    ]
    result = resolve_player_identity(injury(player_id="unknown"), crosswalk(rows))
    assert result.iloc[0]["match_status"] == "unresolved"
    assert result.iloc[0]["match_reason"] == "ambiguous_exact_name_and_team"


def test_leagues_are_separate_id_namespaces():
    rows = [{
        "league": "WNBA", "espn_athlete_id": "espn-1", "wnba_player_id": 2001,
        "wnba_player_name": "Jordan Example", "team_abbreviation": "ABC", "match_confidence": 0.99,
    }]
    result = resolve_player_identity(injury(league="NBA"), crosswalk(rows))
    assert result.iloc[0]["match_status"] == "unresolved"


def test_low_confidence_crosswalk_is_unresolved():
    rows = [{
        "league": "NBA", "espn_athlete_id": "espn-1", "nba_player_id": 1001,
        "nba_player_name": "Jordan Example", "team_abbreviation": "ABC", "match_confidence": 0.5,
    }]
    result = resolve_player_identity(injury(), crosswalk(rows))
    assert result.iloc[0]["match_status"] == "unresolved"
    assert result.iloc[0]["match_reason"] == "crosswalk_confidence_below_threshold"


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError, match="min_confidence"):
        resolve_player_identity(injury(), crosswalk(), min_confidence=2)
