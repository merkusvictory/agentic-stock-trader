import logging
from dataclasses import dataclass

from src.services.llm_call import LLMCall

logger = logging.getLogger(__name__)

_PROS_SYSTEM = (
    "You are an optimistic equity analyst who finds the strongest buy arguments. "
    "Focus on growth catalysts, competitive advantages, and positive momentum."
)

_PROS_PROMPT = (
    "Analyze the following news digest about {symbol} and produce buy arguments.\n\n"
    "News digest:\n{digest}\n\n"
    "Example bull arguments:\n"
    "- Earnings beat analyst expectations by 15%, signaling robust demand.\n"
    "- Regulatory approval for a new product line opens a $5B addressable market.\n\n"
    "Using chain-of-thought reasoning:\n"
    "Step 1: Identify the key growth signal in the news.\n"
    "Step 2: Explain why that signal supports buying {symbol}.\n"
    "Step 3: Consider the broader market context.\n\n"
    "Provide 3-5 distinct bullet-point arguments FOR buying {symbol}. "
    "Start each bullet with '- '.\n\nArguments:"
)


@dataclass(frozen=True)
class ProsList:
    arguments: tuple


class ProsAgent:
    """Produces bull-case arguments for a stock given a NewsBundle digest."""

    def __init__(self, llm: LLMCall = None):
        self.llm = llm or LLMCall()

    async def run(self, news_bundle) -> ProsList:
        prompt = _PROS_PROMPT.format(symbol=news_bundle.symbol, digest=news_bundle.digest)
        response = await self.llm.get_response(_PROS_SYSTEM, prompt)
        arguments = _parse_bullets(response)
        logger.info("Pros: %d arguments for %s", len(arguments), news_bundle.symbol)
        return ProsList(arguments=tuple(arguments))


def _parse_bullets(text: str) -> list:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    bullets = [l.lstrip("-•*").strip() for l in lines if l.startswith(("-", "•", "*"))]
    return (bullets or lines)[:5] or ["No arguments generated."]
