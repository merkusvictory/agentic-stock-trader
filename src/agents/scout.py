from dataclasses import dataclass
from datetime import datetime, timezone

from src.services.alpaca_news import AlpacaNewsService, NewsItem
from src.services.llm_call import LLMCall
from src.prompts.argument_prompts import SCOUT_SYSTEM, SCOUT_DIGEST


@dataclass(frozen=True)
class NewsBundle:
    symbol: str
    articles: tuple
    digest: str
    fetched_at: datetime


class ScoutAgent:
    def __init__(self, news_service: AlpacaNewsService, llm: LLMCall):
        self._news = news_service
        self._llm = llm

    async def run(self, symbol: str, limit: int = 10) -> NewsBundle:
        articles = self._news.fetch_news(symbol, limit)
        articles_text = _format_articles(articles)
        digest = await self._llm.get_response(
            SCOUT_SYSTEM,
            SCOUT_DIGEST.format(symbol=symbol, articles=articles_text),
        )
        return NewsBundle(
            symbol=symbol,
            articles=articles,
            digest=digest.strip(),
            fetched_at=datetime.now(timezone.utc),
        )


def _format_articles(articles: tuple) -> str:
    if not articles:
        return "No articles available."
    return "\n\n".join(
        f"[{a.source}] {a.headline}\n{a.summary}" for a in articles
    )
