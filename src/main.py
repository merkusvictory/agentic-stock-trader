import os
import requests
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

load_dotenv()

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
LLM_API_KEY = os.getenv("LLM_API_KEY")
PAPER_TRADING = os.getenv("ALPACA_PAPER", "true").lower() == "true"
MODEL = "gemini-2.5-flash"
CONFIDENCE_THRESHOLD = 0.6
MAX_ITERATIONS = 3
NEWS_URL = "https://data.alpaca.markets/v1beta1/news"

llm = ChatGoogleGenerativeAI(model=MODEL, google_api_key=LLM_API_KEY)
trading = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=PAPER_TRADING)
market_data = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)

# LLM call function to for role + prompt
def ask_llm(system, prompt):
    return llm.invoke(f"{system}\n\n{prompt}").content

# Fetching 10 most recent articles using Alpaca News API
def fetch_news(symbol, limit=10):
    headers = {"APCA-API-KEY-ID": ALPACA_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET}
    response = requests.get(NEWS_URL, headers=headers, params={"symbols": symbol, "limit": limit}, timeout=10)
    response.raise_for_status()
    articles = response.json().get("news", [])
    return [f"[{a['source']}] {a['headline']}\n{a['summary']}" for a in articles]

# Summarizing important info from articles
def scout(symbol):
    articles = fetch_news(symbol)
    if articles:
        articles_text = "\n\n".join(articles)
    else:
        "No articles available."
    system = "You are a financial news analyst. Synthesize the provided news articles into a clear, factual digest. Focus on earnings, product launches, regulatory news, partnerships, and market impact. Do not speculate."
    prompt = f"Summarize the following news articles about {symbol} in 3-5 sentences.\n\nArticles:\n{articles_text}"
    digest = ask_llm(system, prompt)
    return articles, digest.strip()

# Getting list of pros 
def get_pros(symbol, digest):
    system = "You are an optimistic equity analyst. Your job is to find the strongest buy arguments in any given news story. Do not use markdown formatting in your response."
    prompt = (
        f"Analyze the following news about {symbol} step by step:\n\n"
        "Step 1: Identify the key positive signals in the news.\n"
        "Step 2: Explain how each signal could drive the stock price higher.\n"
        "Step 3: List 3-5 distinct bullish arguments as bullet points.\n\n"
        f"News digest:\n{digest}\n\nBullish arguments:"
    )
    return ask_llm(system, prompt)

# Getting list of cons
def get_cons(symbol, digest):
    system = "You are a skeptical risk analyst. Your job is to identify the strongest arguments against buying a stock, including hidden risks. Do not use markdown formatting in your response."
    prompt = (
        f"Analyze the following news about {symbol} step by step:\n\n"
        "Step 1: Identify the key risks or negative signals hidden in the news.\n"
        "Step 2: Explain how each risk could push the stock price lower.\n"
        "Step 3: List 3-5 distinct bearish arguments as bullet points.\n\n"
        f"News digest:\n{digest}\n\nBearish arguments:"
    )
    return ask_llm(system, prompt)

# Weighing pros and cons, deciding buy, hold, or sell
def judge(symbol, pros, cons, iteration=0):
    system = "You are an impartial senior portfolio manager. Your job is to weigh bullish and bearish arguments objectively and make a clear trading decision."
    prompt = (
        f"You are reviewing arguments about {symbol}. Think step by step:\n\n"
        "Step 1: Summarize the bull case in one sentence.\n"
        "Step 2: Summarize the bear case in one sentence.\n"
        "Step 3: Weigh the strength of each side.\n"
        "Step 4: State your decision and how confident you are (0.0 to 1.0).\n\n"
        f"Bull case:\n{pros}\n\nBear case:\n{cons}\n\n"
        "Respond in exactly this format:\n"
        "ACTION: BUY or HOLD or SELL\n"
        "CONFIDENCE: 0.XX\n"
        "REASONING: one or two sentences"
    )
    response = ask_llm(system, prompt)

    parsed = {k.strip().lower(): v.strip() for line in response.strip().splitlines() if ":" in line for k, _, v in [line.partition(":")]}

    action = parsed.get("action", "hold").lower()
    if action not in ("buy", "sell", "hold"):
        action = "hold"
    try:
        confidence = max(0.0, min(1.0, float(parsed.get("confidence", "0.5"))))
    except ValueError:
        confidence = 0.5
    reasoning = parsed.get("reasoning", "")

    needs_more = confidence < CONFIDENCE_THRESHOLD and iteration < MAX_ITERATIONS - 1
    return action, confidence, reasoning, needs_more

# Getting current holding of specific stock
def get_position_qty(symbol):
    try:
        position = trading.get_open_position(symbol)
        return float(position.qty)
    except Exception:
        return 0.0

# Buying stock through Alpaca API
def place_order(symbol, side, qty=1):
    order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL
    request = MarketOrderRequest(symbol=symbol, qty=qty, side=order_side, time_in_force=TimeInForce.DAY)
    order = trading.submit_order(request)
    time.sleep(2)
    order = trading.get_order_by_id(order.id)
    filled_price = float(order.filled_avg_price or 0) or get_current_price(symbol)
    return {
        "symbol": symbol,
        "side": side,
        "qty": float(qty),
        "filled_price": filled_price,
    }

# Getting current price
def get_current_price(symbol):
    trade = market_data.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol))
    return float(trade[symbol].price)

# Evaluating order after set amount of time
def evaluate(order):
    current_price = get_current_price(order["symbol"])
    entry_price = order["filled_price"]
    pnl_pct = 0.0
    if entry_price != 0:
        pnl_pct = (current_price - entry_price) / entry_price * 100
        if order["side"] == "sell":
            pnl_pct = -pnl_pct

    system = "You are a trading performance analyst. Review a completed trade and give honest, actionable feedback on what drove the outcome."
    prompt = (
        f"Trade summary for {order['symbol']}:\n"
        f"- Action taken: {order['side']}\n"
        f"- Entry price: ${entry_price}\n"
        f"- Current price: ${current_price}\n"
        f"- PnL: {pnl_pct}%\n\n"
        "Respond in exactly this format:\n"
        "VERDICT: one sentence assessment"
    )
    return round(pnl_pct, 4), ask_llm(system, prompt).strip()

# Cycle flow for each run
def run(symbol):
    print(f"Starting cycle for {symbol}")

    articles, digest = scout(symbol)
    print(f"Fetched {len(articles)} articles")
    print(f"\nScout Digest:\n{digest}\n")

    action, confidence, reasoning = "hold", 0.5, ""

    for i in range(MAX_ITERATIONS):
        pros = get_pros(symbol, digest)
        cons = get_cons(symbol, digest)

        print(f"Pros (iteration {i + 1}):\n{pros}\n")
        print(f"Cons (iteration {i + 1}):\n{cons}\n")

        action, confidence, reasoning, needs_more = judge(symbol, pros, cons, i)

        print(f"Judge Decision (iteration {i + 1}):")
        print(f"  Action:     {action.upper()}")
        print(f"  Confidence: {confidence}")
        print(f"  Reasoning:  {reasoning}\n")

        if not needs_more:
            break

    if action == "hold":
        print("Decision: hold, no trade placed.")
        return

    if action == "sell" and get_position_qty(symbol) == 0:
        print(f"Decision: sell but no position in {symbol}, skipping order.")
        return

    order = place_order(symbol, action)
    print(f"Order placed: {order['side']} {order['qty']} {order['symbol']}")

    pnl_pct, evaluation = evaluate(order)
    print(f"\nEvaluator Report:\nPnL: {pnl_pct}%\n\n{evaluation}")

# Specifying which company to review
if __name__ == "__main__":
    run("GOOGL")
