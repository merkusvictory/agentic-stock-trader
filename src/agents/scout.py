import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from src.services.alpaca_news import fetch_news
from src.services.llm_call import LLMCall

logger = logging.getLogger(__name__)

_DIGEST_PROMPT = (
    "Summarize the following news headlines about {symbol} into a concise "
    "3-5 sentence digest. Focus on market-relevant themes, catalysts, and risks.\n\n"
    "Headlines:\n{headlines}\n\nDigest:"
)

_DIGEST_SYSTEM = "You are a concise financial news summarizer. Return only the digest, no preamble."


@dataclass(frozen=True)
class NewsBundle:
    symbol: str
    articles: tuple
    fetched_at: datetime
    digest: str


class ScoutAgent:
    """Fetches news for a symbol and summarises headlines into a digest."""

    def __init__(self, llm: LLMCall = None):
        self.llm = llm or LLMCall()

    async def run(self, symbol: str, limit: int = 10) -> NewsBundle:
        articles = fetch_news(symbol, limit)
        fetched_at = datetime.now(tz=timezone.utc)

        logger.info("Scout fetched %d articles for %s at %s", len(articles), symbol, fetched_at.isoformat())

        if not articles:
            return NewsBundle(symbol=symbol, articles=articles, fetched_at=fetched_at,
                              digest="No recent news found for this symbol.")

        headlines = "\n".join(f"- {a.headline}" for a in articles)
        prompt = _DIGEST_PROMPT.format(symbol=symbol, headlines=headlines)
        digest = await self.llm.get_response(_DIGEST_SYSTEM, prompt)

        sentences = [s.strip() for s in digest.replace("\n", " ").split(".") if s.strip()]
        digest = ". ".join(sentences[:5]) + ("." if sentences else "")

        logger.info("Scout digest generated (%d chars) for %s", len(digest), symbol)
        return NewsBundle(symbol=symbol, articles=articles, fetched_at=fetched_at, digest=digest)
