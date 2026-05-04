from dataclasses import dataclass, field

from src.services.llm_call import LLMCall
from src.prompts.decision_prompts import JUDGE_SYSTEM, JUDGE_PROMPT
from src.agents.pros import ProsList
from src.agents.cons import ConsList


CONFIDENCE_THRESHOLD = 0.6
MAX_ITERATIONS = 3


@dataclass(frozen=True)
class JudgeContext:
    iteration: int = 0


@dataclass(frozen=True)
class JudgeDecision:
    action: str  # "buy" | "hold" | "sell"
    confidence: float
    reasoning: str
    needs_more_info: bool


class JudgeAgent:
    def __init__(self, llm: LLMCall):
        self._llm = llm

    async def run(
        self, pros: ProsList, cons: ConsList, symbol: str, context: JudgeContext = JudgeContext()
    ) -> JudgeDecision:
        pros_text = "\n".join(f"- {a}" for a in pros.arguments)
        cons_text = "\n".join(f"- {a}" for a in cons.arguments)

        response = await self._llm.get_response(
            JUDGE_SYSTEM,
            JUDGE_PROMPT.format(symbol=symbol, pros=pros_text, cons=cons_text),
        )

        action, confidence, reasoning = _parse_response(response)
        at_limit = context.iteration >= MAX_ITERATIONS - 1
        needs_more = confidence < CONFIDENCE_THRESHOLD and not at_limit

        return JudgeDecision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            needs_more_info=needs_more,
        )


def _parse_response(text: str):
    action = "hold"
    confidence = 0.5
    reasoning = ""

    for line in text.strip().splitlines():
        lower = line.strip().lower()
        if lower.startswith("action:"):
            raw = line.split(":", 1)[1].strip().lower()
            if raw in ("buy", "sell", "hold"):
                action = raw
        elif lower.startswith("confidence:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        elif lower.startswith("reasoning:"):
            reasoning = line.split(":", 1)[1].strip()

    return action, confidence, reasoning
