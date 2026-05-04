import logging
from dataclasses import dataclass

from src.services.llm_call import LLMCall

logger = logging.getLogger(__name__)

_CONS_SYSTEM = (
    "You are a highly skeptical equity analyst who identifies the strongest risks "
    "and sell arguments. Focus on downside risks, valuation concerns, and competitive threats."
)

_CONS_PROMPT = (
    "Analyze the following news digest about {symbol} and produce sell/avoid arguments.\n\n"
    "News digest:\n{digest}\n\n"
    "Example bear arguments:\n"
    "- Rising input costs are compressing margins with no resolution timeline.\n"
    "- Key customer concentration risk: losing top client would cut revenue by 20%.\n"
    "- A competitor launched a superior product at 30% lower cost, threatening market share.\n\n"
    "Using chain-of-thought reasoning:\n"
    "Step 1: Identify the key risk signal in the news.\n"
    "Step 2: Explain why that risk argues against buying or holding {symbol}.\n"
    "Step 3: Consider macroeconomic or sector headwinds.\n\n"
    "Provide 3-5 distinct bullet-point arguments AGAINST buying {symbol}. "
    "Start each bullet with '- '.\n\nArguments:"
)


@dataclass(frozen=True)
class ConsList:
    arguments: tuple


class ConsAgent:
    """Produces bear-case arguments for a stock given a NewsBundle digest."""

    def __init__(self, llm: LLMCall = None):
        self.llm = llm or LLMCall()

    async def run(self, news_bundle) -> ConsList:
        prompt = _CONS_PROMPT.format(symbol=news_bundle.symbol, digest=news_bundle.digest)
        response = await self.llm.get_response(_CONS_SYSTEM, prompt)
        arguments = _parse_bullets(response)
        logger.info("Cons: %d arguments for %s", len(arguments), news_bundle.symbol)
        return ConsList(arguments=tuple(arguments))


def _parse_bullets(text: str) -> list:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    bullets = [l.lstrip("-•*").strip() for l in lines if l.startswith(("-", "•", "*"))]
    return (bullets or lines)[:5] or ["No arguments generated."]
