from dataclasses import dataclass

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

from src.utils.config import Config, ConfigError


@dataclass(frozen=True)
class OrderResult:
    order_id: str
    symbol: str
    side: str
    qty: float
    filled_price: float
    status: str


class AlpacaClient:
    def __init__(self):
        if not Config.ALPACA_KEY or not Config.ALPACA_SECRET:
            raise ConfigError("ALPACA_KEY and ALPACA_SECRET must be set in environment")
        self._trading = TradingClient(
            Config.ALPACA_KEY, Config.ALPACA_SECRET, paper=Config.PAPER_TRADING
        )
        self._data = StockHistoricalDataClient(Config.ALPACA_KEY, Config.ALPACA_SECRET)

    def place_order(self, symbol: str, side: str, qty: int = 1) -> OrderResult:
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY,
        )
        order = self._trading.submit_order(request)
        filled_price = float(order.filled_avg_price or 0)
        return OrderResult(
            order_id=str(order.id),
            symbol=symbol,
            side=side.lower(),
            qty=float(qty),
            filled_price=filled_price,
            status=str(order.status),
        )

    def get_current_price(self, symbol: str) -> float:
        request = StockLatestTradeRequest(symbol_or_symbols=symbol)
        trade = self._data.get_stock_latest_trade(request)
        return float(trade[symbol].price)
