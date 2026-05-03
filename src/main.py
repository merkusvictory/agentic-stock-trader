import asyncio
from src.services.alpaca_client import AlpacaClient
from src.agents.scout import Scout
from src.agents.pros import ProAnalyst
from src.agents.cons import ConAnalyst
from src.agents.judge import JudgeAgent

async def trading_cycle():
    scout = Scout()
    pro = ProAnalyst()
    con = ConAnalyst()
    judge = JudgeAgent()
    broker = AlpacaClient()

    while True:
        # 1. Get News
        latest_news = scout.get_latest()
        
        for article in latest_news:
            # 2. Parallel Analysis
            pro_case, con_case = await asyncio.gather(
                pro.analyze(article),
                con.analyze(article)
            )
            
            # 3. Final Decision
            decision = await judge.decide(pro_case, con_case)
            
            # 4. Action
            if "BUY" in decision:
                broker.place_order(article.symbol, "buy")

        await asyncio.sleep(600) # Wait 10 minutes before next check