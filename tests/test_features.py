import numpy as np
import pandas as pd
from src.features.core import add_matchup_pressure, add_opportunity_index, add_role_shift_features, add_rolling_player_features

def fixture():
    dates = pd.date_range("2026-01-01", periods=12)
    return pd.DataFrame({"player_id":[1]*12,"game_id":range(12),"game_date":dates,"minutes":[30+i for i in range(12)],"pts":[15+i for i in range(12)],"fga":[12+i for i in range(12)],"fg3a":[4]*12,"fta":[3]*12,"reb":[5]*12,"ast":[4+(i//4) for i in range(12)]})

def test_rolling_features_do_not_use_current_game():
    df=add_rolling_player_features(fixture())
    assert pd.isna(df.iloc[0]["pts_roll_5"])
    assert df.iloc[1]["pts_roll_5"] == 15

def test_role_shift_and_opportunity_are_created():
    df=add_opportunity_index(add_role_shift_features(add_rolling_player_features(fixture())))
    assert "role_shift_index" in df and "rh_opportunity_index" in df
    assert df["rh_opportunity_index"].between(0,100).all()

def test_matchup_pressure():
    out=add_matchup_pressure(pd.DataFrame({"three_rate_roll_5":[0.40,0.30],"opp_three_rate_allowed":[0.35,0.35]}))
    assert np.allclose(out["matchup_pressure"].to_numpy(), [0.05,-0.05])


def test_opportunity_index_is_scoped_to_game_date():
    from src.features.core import add_opportunity_index

    base = pd.DataFrame({
        "game_date": ["2026-01-01"] * 3,
        "minutes_roll_5": [20.0, 30.0, 40.0],
        "fga_roll_5": [8.0, 12.0, 16.0],
        "fta_roll_5": [2.0, 4.0, 6.0],
        "ast_roll_5": [2.0, 5.0, 8.0],
    })
    initial = add_opportunity_index(base)
    extended = pd.concat([base, pd.DataFrame({
        "game_date": ["2026-02-01"],
        "minutes_roll_5": [1000.0],
        "fga_roll_5": [1000.0],
        "fta_roll_5": [1000.0],
        "ast_roll_5": [1000.0],
    })], ignore_index=True)
    after_future_row = add_opportunity_index(extended)
    assert initial["rh_opportunity_index"].tolist() == after_future_row.iloc[:3]["rh_opportunity_index"].tolist()


def test_rolling_features_do_not_mix_leagues_when_player_ids_collide():
    from src.features.core import add_rolling_player_features

    df = pd.DataFrame({
        "league": ["NBA", "WNBA", "NBA", "WNBA"],
        "player_id": [1, 1, 1, 1],
        "game_id": [1, 1, 2, 2],
        "game_date": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02"]),
        "minutes": [30, 10, 40, 20],
        "pts": [20, 5, 25, 8],
        "fga": [15, 4, 16, 5],
        "fg3a": [5, 1, 6, 2],
        "fta": [4, 1, 5, 2],
        "reb": [6, 2, 7, 3],
        "ast": [5, 1, 6, 2],
    })
    out = add_rolling_player_features(df)
    nba_second = out[(out["league"] == "NBA") & (out["game_id"] == 2)].iloc[0]
    wnba_second = out[(out["league"] == "WNBA") & (out["game_id"] == 2)].iloc[0]
    assert nba_second["pts_roll_5"] == 20
    assert wnba_second["pts_roll_5"] == 5
