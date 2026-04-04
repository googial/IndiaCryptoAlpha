"""
Base exchange interface for supporting multiple cryptocurrency exchanges.
Defines common methods that all exchange implementations must provide.
"""

import abc
import time
import logging
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)


class BaseExchange(abc.ABC):
    """Abstract base class for exchange implementations."""

    def __init__(self, api_key: str = "", api_secret: str = "", **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange_name = self.__class__.__name__.replace("Exchange", "").lower()

    @abc.abstractmethod
    def get_ticker(self, symbol: str) -> Dict:
        """Get latest ticker for a symbol. Returns dict with 'last', 'bid', 'ask', 'volume', 'timestamp'."""
        pass

    @abc.abstractmethod
    def get_candles(
        self, symbol: str, interval: str = "1m", limit: int = 100
    ) -> List[Dict]:
        """Get historical OHLCV candles. Each candle: {'time', 'open', 'high', 'low', 'close', 'volume'}."""
        pass

    def get_ohlcv(
        self, symbol: str, timeframe: str = "1h", limit: int = 100
    ) -> pd.DataFrame:
        """Get OHLCV data as pandas DataFrame. Default implementation uses get_candles."""
        candles = self.get_candles(symbol, interval=timeframe, limit=limit)
        if not candles:
            return pd.DataFrame()
        df = pd.DataFrame(candles)
        # Standardize time column
        if "time" in df.columns:
            df["time"] = pd.to_datetime(
                df["time"], unit="ms" if df["time"].iloc[0] > 1e12 else None
            )
            df.set_index("time", inplace=True)
        # Ensure columns
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df

    @abc.abstractmethod
    def place_order(
        self,
        side: str,
        symbol: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: str = "market",
    ) -> Optional[Dict]:
        """Place an order on the exchange."""
        pass

    @abc.abstractmethod
    def get_balance(self) -> Dict:
        """Get account balance. Returns dict: {asset: {'free': float, 'locked': float, 'total': float}}."""
        pass

    @abc.abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders."""
        pass

    def _generate_timestamp(self) -> int:
        """Generate exchange-specific timestamp."""
        return int(time.time() * 1000)


class ExchangeFactory:
    """Factory for creating exchange instances."""

    @staticmethod
    def create_exchange(
        exchange_name: str, api_key: str = "", api_secret: str = "", **kwargs
    ) -> BaseExchange:
        """Create an exchange instance based on name."""
        exchange_name = exchange_name.lower()

        if exchange_name == "binance":
            from .binance_exchange import BinanceExchange

            return BinanceExchange(api_key, api_secret, **kwargs)
        elif exchange_name == "coindcx":
            from .coindcx_exchange import CoinDCXExchange

            return CoinDCXExchange(api_key, api_secret, **kwargs)
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
