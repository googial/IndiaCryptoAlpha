import time
import json
import hmac
import hashlib
import requests
import pandas as pd
from typing import Dict, Optional, List
import logging
import config as config_mod  # Import module, not values, to allow hot-reload
from .exchange_base import ExchangeFactory

logger = logging.getLogger(__name__)


"""
Market Data Manager - Exchange-agnostic facade for IndiaCryptoAlpha.
Provides high-level market data methods and delegates to the configured exchange.
"""


class MarketDataManager:
    """
    Facade that provides unified market data access across supported exchanges.
    Current supported: 'binance', 'coindcx'
    """

    def __init__(self):
        """Initialize the exchange based on configuration."""
        exchange_name = (
            config_mod.EXCHANGE_NAME.lower() if config_mod.EXCHANGE_NAME else "coindcx"
        )

        # Select credentials based on exchange
        if exchange_name == "binance":
            api_key = config_mod.BINANCE_API_KEY
            api_secret = config_mod.BINANCE_SECRET_KEY
        elif exchange_name == "coindcx":
            api_key = config_mod.COINDCX_API_KEY
            api_secret = config_mod.COINDCX_API_SECRET
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")

        self.exchange = ExchangeFactory.create_exchange(
            exchange_name, api_key=api_key, api_secret=api_secret
        )
        self.exchange_name = exchange_name
        logger.info(f"✅ MarketDataManager initialized with {exchange_name} exchange")

    # Delegate low-level methods to exchange
    def get_ticker(self, symbol: str) -> Dict:
        """Get latest ticker for a symbol."""
        return self.exchange.get_ticker(symbol)

    def get_candles(
        self, symbol: str, interval: str = "1m", limit: int = 100
    ) -> List[Dict]:
        """Get historical OHLCV candles."""
        return self.exchange.get_candles(symbol, interval, limit)

    def get_ohlcv(
        self, symbol: str, timeframe: str = "1h", limit: int = 100
    ) -> pd.DataFrame:
        """Get OHLCV data as pandas DataFrame."""
        return self.exchange.get_ohlcv(symbol, timeframe, limit)

    def place_order(
        self,
        side: str,
        symbol: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: str = "market",
    ) -> Optional[Dict]:
        """Place an order on the exchange."""
        return self.exchange.place_order(side, symbol, quantity, price, order_type)

    def get_balance(self) -> Dict:
        """Get account balance."""
        return self.exchange.get_balance()

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders."""
        return self.exchange.get_open_orders(symbol)

    # High-level methods
    def get_historical_data(
        self, symbol: str, timeframe: str = "1h", days: int = 30
    ) -> pd.DataFrame:
        """
        Get historical data for backtesting/analysis.
        Estimates limit from timeframe and days.
        """
        interval_map = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "1h": 60,
            "4h": 240,
            "1d": 1440,
        }
        minutes_per_candle = interval_map.get(timeframe, 60)
        total_minutes = days * 24 * 60
        limit = min(1000, total_minutes // minutes_per_candle)

        candles = self.exchange.get_candles(symbol, interval=timeframe, limit=limit)
        if not candles:
            return pd.DataFrame()
        df = pd.DataFrame(candles)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], unit="ms")
            df.set_index("time", inplace=True)
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol."""
        ticker = self.exchange.get_ticker(symbol)
        return ticker.get("last") if ticker else None

    def get_market_regime(
        self, symbol: str, timeframe: str = "1d", days: int = 30
    ) -> str:
        """
        Detect market regime for a symbol.
        Fetches historical data and uses regime detector.
        """
        try:
            from intelligence.regime_detector import detect_regime

            # Use 1h for daily regime detection if timeframe is daily
            df = self.get_historical_data(
                symbol, timeframe="1h" if timeframe == "1d" else timeframe, days=days
            )
            if df is None or len(df) < 50:
                return "choppy"
            return detect_regime(df)
        except Exception as e:
            logger.error(f"Failed to detect regime for {symbol}: {e}")
            return "choppy"
