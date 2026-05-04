from dataclasses import dataclass

from src.services.llm_call import LLMCall
from src.services.alpaca_client import AlpacaClient, OrderResult
from src.prompts.decision_prompts import EVALUATOR_SYSTEM, EVALUATOR_PROMPT


@dataclass(frozen=True)
class EvaluationReport:
    symbol: str
    pnl_pct: float
    verdict: str
    suggested_adjustments: tuple
    reasoning: str = ""


class EvaluatorAgent:
    def __init__(self, llm: LLMCall, client: AlpacaClient):
        self._llm = llm
        self._client = client

    async def evaluate(self, order: OrderResult) -> EvaluationReport:
        current_price = self._client.get_current_price(order.symbol)
        pnl_pct = _calc_pnl(order, current_price)

        response = await self._llm.get_response(
            EVALUATOR_SYSTEM,
            EVALUATOR_PROMPT.format(
                symbol=order.symbol,
                action=order.side,
                entry_price=order.filled_price,
                current_price=current_price,
                pnl_pct=pnl_pct,
            ),
        )

        verdict, adjustments = _parse_response(response)
        return EvaluationReport(
            symbol=order.symbol,
            pnl_pct=round(pnl_pct, 4),
            verdict=verdict,
            suggested_adjustments=adjustments,
            reasoning=response.strip(),
        )


def _calc_pnl(order: OrderResult, current_price: float) -> float:
    if order.filled_price == 0:
        return 0.0
    pnl = (current_price - order.filled_price) / order.filled_price * 100
    return pnl if order.side == "buy" else -pnl


def _parse_response(text: str):
    verdict = ""
    adjustments = []
    in_adjustments = False

    for line in text.strip().splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("verdict:"):
            verdict = stripped.split(":", 1)[1].strip()
            in_adjustments = False
        elif stripped.lower().startswith("adjustments:"):
            in_adjustments = True
        elif in_adjustments and stripped.startswith("-"):
            adjustments.append(stripped.lstrip("-• ").strip())

    return verdict, tuple(adjustments)
