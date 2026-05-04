import os
import requests
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class NewsItem:
    headline: str
    summary: str
    source: str
    published_at: datetime
    symbols: tuple


_NEWS_URL = "https://data.alpaca.markets/v1beta1/news"


def fetch_news(symbol: str, limit: int = 10) -> tuple:
    """Fetch recent news for *symbol* from the Alpaca News API.

    Returns an immutable tuple of NewsItem objects sorted newest-first.
    Raises ConfigError if credentials are missing, or requests.HTTPError on API errors.
    """
    api_key = os.environ.get("ALPACA_KEY")
    api_secret = os.environ.get("ALPACA_SECRET")
    if not api_key or not api_secret:
        raise ConfigError(
            "ALPACA_KEY and ALPACA_SECRET must be set as environment variables."
        )

    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
    }
    params = {"symbols": symbol, "limit": limit, "sort": "desc"}

    response = requests.get(_NEWS_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    articles = response.json().get("news", [])
    items = []
    for article in articles:
        raw_ts = article.get("created_at", "")
        try:
            published_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            published_at = datetime.now(tz=timezone.utc)

        items.append(
            NewsItem(
                headline=article.get("headline", ""),
                summary=article.get("summary", ""),
                source=article.get("source", ""),
                published_at=published_at,
                symbols=tuple(article.get("symbols", [])),
            )
        )

    return tuple(items)
