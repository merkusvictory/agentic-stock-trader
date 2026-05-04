import asyncio
from src.agents.scout import ScoutAgent
from src.agents.pros import ProsAgent
from src.agents.cons import ConsAgent
from src.services.llm_call import LLMCall

SYMBOL = "AAPL"  # change this to any ticker

async def main():
    llm = LLMCall()
    scout = ScoutAgent(llm=llm)
    pros = ProsAgent(llm=llm)
    cons = ConsAgent(llm=llm)

    print(f"\n=== Fetching news for {SYMBOL} ===")
    bundle = await scout.run(SYMBOL)
    print(f"Articles fetched: {len(bundle.articles)}")
    print(f"Digest:\n{bundle.digest}\n")

    print("=== Bull case (Pros) ===")
    pros_list = await pros.run(bundle)
    for arg in pros_list.arguments:
        print(f"  + {arg}")

    print("\n=== Bear case (Cons) ===")
    cons_list = await cons.run(bundle)
    for arg in cons_list.arguments:
        print(f"  - {arg}")

asyncio.run(main())
