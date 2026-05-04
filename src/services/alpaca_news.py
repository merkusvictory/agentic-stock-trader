from dataclasses import dataclass
from datetime import datetime
import requests
from src.utils.config import Config, ConfigError


@dataclass(frozen=True)
class NewsItem:
    headline: str
    summary: str
    source: str
    published_at: datetime
    symbols: tuple


BASE_URL = "https://data.alpaca.markets/v1beta1/news"


class AlpacaNewsService:
    def __init__(self):
        if not Config.ALPACA_KEY or not Config.ALPACA_SECRET:
            raise ConfigError("ALPACA_KEY and ALPACA_SECRET must be set in environment")
        self._headers = {
            "APCA-API-KEY-ID": Config.ALPACA_KEY,
            "APCA-API-SECRET-KEY": Config.ALPACA_SECRET,
        }

    def fetch_news(self, symbol: str, limit: int = 10) -> tuple:
        if not symbol:
            raise ValueError("symbol must be a non-empty string")

        response = requests.get(
            BASE_URL,
            headers=self._headers,
            params={"symbols": symbol, "limit": limit},
            timeout=10,
        )
        response.raise_for_status()

        raw_articles = response.json().get("news", [])
        return tuple(_parse_article(a) for a in raw_articles)


def _parse_article(raw: dict) -> NewsItem:
    published_raw = raw.get("updated_at") or raw.get("created_at", "")
    published_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
    return NewsItem(
        headline=raw.get("headline", ""),
        summary=raw.get("summary", ""),
        source=raw.get("source", ""),
        published_at=published_at,
        symbols=tuple(raw.get("symbols", [])),
    )
