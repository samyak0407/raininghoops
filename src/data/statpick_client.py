"""Client for the public Stat Pick research API."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import requests

@dataclass
class StatPickClient:
    base_url: str = "https://api.statpick.ai"
    timeout: int = 20
    user_agent: str = "RainingHoops/0.1 (basketball research)"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url.rstrip('/')}/{path.lstrip('/')}",
            params=params, timeout=self.timeout,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Stat Pick returned a non-object JSON response.")
        if payload.get("success") is False:
            raise RuntimeError(payload.get("message", "Stat Pick API request failed."))
        return payload

    def app_config(self) -> dict[str, Any]:
        return self._get("/api/app-config")

    def prop_slate(self, sport: str) -> dict[str, Any]:
        return self._get(f"/api/{sport}/prop-pages/slate")

    def player_props(self, sport: str, player_slug: str) -> dict[str, Any]:
        return self._get(f"/api/{sport}/prop-pages/player/{player_slug}")

    def player_stat(self, sport: str, player_slug: str, stat_slug: str) -> dict[str, Any]:
        return self._get(f"/api/{sport}/prop-pages/player/{player_slug}/stat/{stat_slug}")

    def daily_picks_preview(self, sport: str | None = None) -> dict[str, Any]:
        return self._get("/api/public/daily-picks/preview", {"sport": sport} if sport else None)
