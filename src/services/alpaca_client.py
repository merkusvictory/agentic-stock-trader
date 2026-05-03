from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from src.utils.config import Config

class AlpacaClient:
    def __init__(self):
        self.client = TradingClient(Config.ALPACA_KEY, Config.ALPACA_SECRET, paper=True)

    def place_order(self, symbol, side, qty=1):
        order_data = MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force='day')
        return self.client.submit_order(order_data)