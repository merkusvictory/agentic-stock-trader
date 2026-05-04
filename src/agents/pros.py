from dataclasses import dataclass

from src.services.llm_call import LLMCall
from src.prompts.argument_prompts import PROS_SYSTEM, PROS_ARGUMENTS
from src.agents.scout import NewsBundle


@dataclass(frozen=True)
class ProsList:
    arguments: tuple
    reasoning: str = ""


class ProsAgent:
    def __init__(self, llm: LLMCall):
        self._llm = llm

    async def run(self, news_bundle: NewsBundle) -> ProsList:
        response = await self._llm.get_response(
            PROS_SYSTEM,
            PROS_ARGUMENTS.format(
                symbol=news_bundle.symbol,
                digest=news_bundle.digest,
            ),
        )
        return ProsList(arguments=_parse_bullets(response), reasoning=response.strip())


def _parse_bullets(text: str) -> tuple:
    lines = (line.strip().lstrip("-•* ") for line in text.strip().splitlines())
    return tuple(line for line in lines if line)
