import pandas as pd
from src.features.role import add_rolling_role_features, add_opportunity_components, add_role_shift_index

def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = add_rolling_role_features(frame)
    out = add_opportunity_components(out)
    return add_role_shift_index(out)
