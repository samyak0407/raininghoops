import pandas as pd
import pytest

from src.data.quality import assert_valid_player_game_logs, validate_player_game_logs


def valid_frame():
    return pd.DataFrame({
        "league": ["NBA", "NBA"],
        "season": ["2025-26", "2025-26"],
        "player_id": ["1", "2"],
        "game_id": ["g1", "g1"],
        "game_date": ["2026-01-01", "2026-01-01"],
        "minutes": [30.0, 22.5],
        "pts": [20, 11],
        "fga": [15, 9],
        "fg3a": [5, 2],
        "fta": [4, 3],
    })


def test_valid_player_game_logs_pass():
    assert_valid_player_game_logs(valid_frame())


def test_missing_columns_return_diagnostic_instead_of_key_error():
    report = validate_player_game_logs(pd.DataFrame({"player_id": ["1"]}))
    assert "league" in report["missing_columns"]
    assert report["duplicate_player_games"] == 0
    with pytest.raises(AssertionError, match="Missing required columns"):
        assert_valid_player_game_logs(pd.DataFrame({"player_id": ["1"]}))


def test_duplicate_player_game_is_detected():
    frame = valid_frame()
    frame.loc[1, ["player_id", "game_id"]] = ["1", "g1"]
    report = validate_player_game_logs(frame)
    assert report["duplicate_player_games"] == 1
    with pytest.raises(AssertionError, match="duplicate player-game"):
        assert_valid_player_game_logs(frame)


def test_negative_count_or_minutes_is_detected():
    frame = valid_frame()
    frame.loc[0, "fga"] = -1
    report = validate_player_game_logs(frame)
    assert report["numeric_checks"]["negative_fga"] == 1
    with pytest.raises(AssertionError, match="negative_fga"):
        assert_valid_player_game_logs(frame)


def test_null_ids_are_rejected():
    frame = valid_frame()
    frame.loc[0, "game_id"] = None
    report = validate_player_game_logs(frame)
    assert report["null_game_ids"] == 1
    with pytest.raises(AssertionError, match="null_game_ids"):
        assert_valid_player_game_logs(frame)
