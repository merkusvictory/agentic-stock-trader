import asyncio

from src.services.llm_call import LLMCall
from src.services.alpaca_news import AlpacaNewsService
from src.services.alpaca_client import AlpacaClient
from src.agents.scout import ScoutAgent
from src.agents.pros import ProsAgent
from src.agents.cons import ConsAgent
from src.agents.judge import JudgeAgent, JudgeContext, MAX_ITERATIONS
from src.agents.evaluator import EvaluatorAgent
from src.utils.logger import get_logger

log = get_logger("orchestrator")


async def run_trading_cycle(symbol: str):
    llm = LLMCall()
    client = AlpacaClient()

    scout = ScoutAgent(AlpacaNewsService(), llm)
    pros_agent = ProsAgent(llm)
    cons_agent = ConsAgent(llm)
    judge = JudgeAgent(llm)
    evaluator = EvaluatorAgent(llm, client)

    log.info("starting cycle", extra={"agent": "orchestrator", "symbol": symbol})

    bundle = await scout.run(symbol)
    log.info(f"fetched {len(bundle.articles)} articles", extra={"agent": "scout", "symbol": symbol})
    print(f"\n=== Scout Digest ===\n{bundle.digest}\n")

    pros, cons = None, None
    decision = None

    for i in range(MAX_ITERATIONS):
        pros, cons = await asyncio.gather(
            pros_agent.run(bundle),
            cons_agent.run(bundle),
        )

        print(f"\n=== Pros Reasoning (iteration {i + 1}) ===\n{pros.reasoning}\n")
        print(f"=== Cons Reasoning (iteration {i + 1}) ===\n{cons.reasoning}\n")

        context = JudgeContext(iteration=i)
        decision = await judge.run(pros, cons, symbol, context)

        print(
            f"=== Judge Decision (iteration {i + 1}) ===\n"
            f"Action:     {decision.action.upper()}\n"
            f"Confidence: {decision.confidence:.2f}\n"
            f"Reasoning:  {decision.reasoning}\n"
        )
        log.info(
            f"judge iteration {i + 1}: {decision.action} @ {decision.confidence:.2f}",
            extra={"agent": "judge", "symbol": symbol},
        )

        if not decision.needs_more_info:
            break

    if decision.action == "hold":
        log.info("decision: hold, no trade placed", extra={"agent": "orchestrator", "symbol": symbol})
        return

    order = client.place_order(symbol, decision.action)
    log.info(
        f"order placed: {order.side} {order.qty} {order.symbol}",
        extra={"agent": "orchestrator", "symbol": symbol},
    )

    report = await evaluator.evaluate(order)
    print(
        f"\n=== Evaluator Report ===\n"
        f"PnL:     {report.pnl_pct:.2f}%\n"
        f"Verdict: {report.verdict}\n"
        f"\nFull reasoning:\n{report.reasoning}\n"
    )
    log.info(
        f"evaluation: pnl={report.pnl_pct:.2f}% | {report.verdict}",
        extra={"agent": "evaluator", "symbol": symbol},
    )

    return report


if __name__ == "__main__":
    asyncio.run(run_trading_cycle("AAPL"))
