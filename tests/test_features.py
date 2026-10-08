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
    assert out["matchup_pressure"].tolist() == [0.05,-0.05]
