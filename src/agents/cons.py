from dataclasses import dataclass

from src.services.llm_call import LLMCall
from src.prompts.argument_prompts import CONS_SYSTEM, CONS_ARGUMENTS
from src.agents.scout import NewsBundle


@dataclass(frozen=True)
class ConsList:
    arguments: tuple


class ConsAgent:
    def __init__(self, llm: LLMCall):
        self._llm = llm

    async def run(self, news_bundle: NewsBundle) -> ConsList:
        response = await self._llm.get_response(
            CONS_SYSTEM,
            CONS_ARGUMENTS.format(
                symbol=news_bundle.symbol,
                digest=news_bundle.digest,
            ),
        )
        return ConsList(arguments=_parse_bullets(response))


def _parse_bullets(text: str) -> tuple:
    lines = (line.strip().lstrip("-•* ") for line in text.strip().splitlines())
    return tuple(line for line in lines if line)
