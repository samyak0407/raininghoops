"""Conservative player identity resolution for ESPN injury records.

The resolver never invents IDs. It prefers explicit ESPN-ID crosswalks, falls
back only to unique exact name + team matches, and leaves conflicts unresolved.
All identifiers are treated as strings because providers use separate namespaces.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

import pandas as pd

OUTPUT_COLUMNS = [
    "resolved_player_id",
    "resolved_player_name",
    "resolved_team_abbreviation",
    "match_method",
    "match_confidence",
    "match_status",
    "match_reason",
]


def normalize_player_name(value: Any) -> str:
    """Normalize cosmetic name differences without attempting fuzzy matching."""
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.casefold().replace(".", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_team(value: Any) -> str:
    """Normalize team abbreviations for exact comparison."""
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper().strip())


def _safe_string(value: Any) -> str:
    """Convert scalar identifiers safely, including pandas missing values."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _first_column(frame: pd.DataFrame, candidates: tuple[str, ...], required: bool = True) -> str | None:
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    if required:
        raise ValueError(f"Crosswalk is missing one of these required columns: {candidates}")
    return None


def _canonical_crosswalk(crosswalk: pd.DataFrame) -> pd.DataFrame:
    """Accept the project's canonical schema and common crosswalk field names."""
    league_col = _first_column(crosswalk, ("league",))
    espn_id_col = _first_column(crosswalk, ("espn_player_id", "espn_athlete_id"))
    player_id_col = _first_column(
        crosswalk, ("league_player_id", "nba_player_id", "wnba_player_id", "player_id")
    )
    player_name_col = _first_column(
        crosswalk, ("league_player_name", "nba_player_name", "wnba_player_name", "player_name")
    )
    team_col = _first_column(crosswalk, ("team_abbreviation", "team_abbr", "team"))
    confidence_col = _first_column(crosswalk, ("match_confidence", "confidence"), required=False)

    out = pd.DataFrame({
        "league": crosswalk[league_col].astype("string").str.upper().str.strip(),
        "espn_player_id": crosswalk[espn_id_col].astype("string").str.strip(),
        "league_player_id": crosswalk[player_id_col].astype("string").str.strip(),
        "league_player_name": crosswalk[player_name_col].astype("string").str.strip(),
        "team_abbreviation": crosswalk[team_col].astype("string").str.upper().str.strip(),
    })
    out["espn_player_name"] = (
        crosswalk[_first_column(crosswalk, ("espn_player_name", "espn_full_name"), required=False)]
        .astype("string").str.strip()
        if _first_column(crosswalk, ("espn_player_name", "espn_full_name"), required=False)
        else out["league_player_name"]
    )
    out["match_confidence"] = (
        pd.to_numeric(crosswalk[confidence_col], errors="coerce")
        if confidence_col
        else 1.0
    )
    out["name_key"] = out["league_player_name"].map(normalize_player_name)
    out["espn_name_key"] = out["espn_player_name"].map(normalize_player_name)
    out["team_key"] = out["team_abbreviation"].map(normalize_team)
    out = out.replace({"<NA>": ""})
    return out


def resolve_player_identity(
    injuries: pd.DataFrame,
    crosswalk: pd.DataFrame,
    min_confidence: float = 0.92,
) -> pd.DataFrame:
    """Add conservative identity-resolution fields to normalized ESPN injury rows.

    Required injury columns: league, player_id, player_name, team_abbreviation.
    Required crosswalk concepts: league, ESPN athlete ID, league player ID/name,
    and team abbreviation. Common NBA/WNBA crosswalk aliases are accepted.

    Match order:
      1. ESPN athlete ID + league, requiring team consistency.
      2. Unique exact normalized player name + team + league.
      3. Otherwise unresolved; fuzzy matches are intentionally not auto-accepted.
    """
    if not 0 <= min_confidence <= 1:
        raise ValueError("min_confidence must be between 0 and 1")
    required = {"league", "player_id", "player_name", "team_abbreviation"}
    missing = required - set(injuries.columns)
    if missing:
        raise ValueError(f"Injury rows are missing required columns: {sorted(missing)}")
    if crosswalk.empty:
        out = injuries.copy()
        for column in OUTPUT_COLUMNS:
            out[column] = pd.Series(index=out.index, dtype="object")
        out["match_status"] = "unresolved"
        out["match_reason"] = "empty_crosswalk"
        return out

    cw = _canonical_crosswalk(crosswalk)
    cw = cw[
        cw["league_player_id"].fillna("").ne("")
        & cw["league_player_name"].fillna("").ne("")
        & cw["league"].fillna("").ne("")
    ].copy()

    results: list[dict[str, Any]] = []
    for _, injury in injuries.iterrows():
        league = _safe_string(injury.get("league", "")).upper()
        espn_id = _safe_string(injury.get("player_id", ""))
        name_key = normalize_player_name(injury.get("player_name"))
        team_key = normalize_team(injury.get("team_abbreviation"))
        league_cw = cw[cw["league"] == league]
        result: dict[str, Any] = {
            "resolved_player_id": None,
            "resolved_player_name": None,
            "resolved_team_abbreviation": None,
            "match_method": None,
            "match_confidence": 0.0,
            "match_status": "unresolved",
            "match_reason": "no_unique_exact_match",
        }

        id_matches = league_cw[
            league_cw["espn_player_id"].fillna("").ne("")
            & (league_cw["espn_player_id"] == espn_id)
        ] if espn_id and espn_id.lower() != "nan" else league_cw.iloc[0:0]

        if not id_matches.empty:
            team_matches = id_matches[id_matches["team_key"] == team_key] if team_key else id_matches.iloc[0:0]
            candidates = team_matches if not team_matches.empty else id_matches
            player_ids = candidates["league_player_id"].dropna().unique().tolist()
            if len(player_ids) == 1 and team_matches.shape[0] > 0:
                candidate = team_matches.iloc[0]
                confidence = float(candidate["match_confidence"]) if pd.notna(candidate["match_confidence"]) else 0.0
                if confidence >= min_confidence:
                    result.update({
                        "resolved_player_id": str(candidate["league_player_id"]),
                        "resolved_player_name": str(candidate["league_player_name"]),
                        "resolved_team_abbreviation": str(candidate["team_abbreviation"]),
                        "match_method": "espn_id_crosswalk",
                        "match_confidence": confidence,
                        "match_status": "matched",
                        "match_reason": "espn_id_and_team_agree",
                    })
                else:
                    result["match_reason"] = "crosswalk_confidence_below_threshold"
            elif not team_matches.empty and len(player_ids) > 1:
                result["match_reason"] = "ambiguous_espn_id_crosswalk"
            else:
                result["match_reason"] = "espn_id_team_conflict"
        elif name_key and team_key:
            exact = league_cw[
                (league_cw["name_key"] == name_key)
                & (league_cw["team_key"] == team_key)
            ]
            ids = exact["league_player_id"].dropna().unique().tolist()
            if len(ids) == 1 and not exact.empty:
                candidate = exact.iloc[0]
                result.update({
                    "resolved_player_id": str(candidate["league_player_id"]),
                    "resolved_player_name": str(candidate["league_player_name"]),
                    "resolved_team_abbreviation": str(candidate["team_abbreviation"]),
                    "match_method": "exact_name_team",
                    "match_confidence": float(candidate["match_confidence"]) if pd.notna(candidate["match_confidence"]) else 0.99,
                    "match_status": "matched",
                    "match_reason": "unique_exact_name_and_team",
                })
                if result["match_confidence"] < min_confidence:
                    result.update({
                        "resolved_player_id": None,
                        "resolved_player_name": None,
                        "resolved_team_abbreviation": None,
                        "match_method": None,
                        "match_status": "unresolved",
                        "match_reason": "crosswalk_confidence_below_threshold",
                    })
            elif len(ids) > 1:
                result["match_reason"] = "ambiguous_exact_name_and_team"
            else:
                result["match_reason"] = "no_exact_name_and_team_match"

        results.append(result)

    matched = pd.DataFrame(results, index=injuries.index, columns=OUTPUT_COLUMNS)
    return pd.concat([injuries.copy(), matched], axis=1)
