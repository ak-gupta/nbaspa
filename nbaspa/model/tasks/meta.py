"""Metadata."""

from typing import Dict

META: Dict = {
    "static": [
        "HOME_NET_RATING",
        "VISITOR_NET_RATING",
        "HOME_W_PCT",
        "VISITOR_W_PCT",
        "LAST_GAME_WIN",
        "HOME_GAMES_IN_LAST_3_DAYS",
        "HOME_GAMES_IN_LAST_5_DAYS",
        "HOME_GAMES_IN_LAST_7_DAYS",
        "VISITOR_GAMES_IN_LAST_3_DAYS",
        "VISITOR_GAMES_IN_LAST_5_DAYS",
        "VISITOR_GAMES_IN_LAST_7_DAYS"
    ],
    "dynamic": [
        "SCOREMARGIN",
        "HOME_LINEUP_PLUS_MINUS",
        "VISITOR_LINEUP_PLUS_MINUS"
    ],
    "duration": "TIME",
    "event": "WIN",
    "id": "GAME_ID"
}