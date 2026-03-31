"""Market data module for fetching real-time and historical data from CoinDCX."""

import logging
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import COINDCX_API_KEY, COINDCX_API_SECRET, SUPPORTED_PAIRS, DEFAULT_TIMEFRAME

logger = logging.getLogger(__name__)


class MarketDataManager:
    """Manages market data fetching and caching from CoinDCX."""

    def __init__(self):
        """Initialize the market data manager with CoinDCX exchange."""
        try:
            self.exchange = ccxt.coindcx({
                'apiKey': COINDCX_API_KEY,
                'secret': COINDCX_API_SECRET,
                'enableRateLimit': True,
            })
            self.exchange.load_markets()
            logger.info("✓ CoinDCX market data manager initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize CoinDCX: {e}")
            raise

        self.data_cache = {}
        self.last_update = {}

    def get_ticker(self, pair: str) -> Optional[Dict]:
        """
        Fetch current ticker data for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'BTC/INR')
            
        Returns:
            Ticker data dictionary or None if failed
        """
        try:
            ticker = self.exchange.fetch_ticker(pair)
            logger.debug(f"✓ Fetched ticker for {pair}: {ticker['last']}")
            return ticker
        except Exception as e:
            logger.error(f"✗ Failed to fetch ticker for {pair}: {e}")
            return None

    def get_orderbook(self, pair: str, limit: int = 20) -> Optional[Dict]:
        """
        Fetch order book for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'BTC/INR')
            limit: Number of bids/asks to return
            
        Returns:
            Order book dictionary or None if failed
        """
        try:
            orderbook = self.exchange.fetch_order_book(pair, limit=limit)
            logger.debug(f"✓ Fetched orderbook for {pair}")
            return orderbook
        except Exception as e:
            logger.error(f"✗ Failed to fetch orderbook for {pair}: {e}")
            return None

    def get_ohlcv(self, pair: str, timeframe: str = DEFAULT_TIMEFRAME, 
                  limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV (candlestick) data for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'BTC/INR')
            timeframe: Timeframe (e.g., '1h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['pair'] = pair
            logger.debug(f"✓ Fetched {len(df)} candles for {pair} ({timeframe})")
            return df
        except Exception as e:
            logger.error(f"✗ Failed to fetch OHLCV for {pair}: {e}")
            return None

    def get_historical_data(self, pair: str, days: int = 30, 
                           timeframe: str = '1d') -> Optional[pd.DataFrame]:
        """
        Fetch historical data for backtesting.
        
        Args:
            pair: Trading pair (e.g., 'BTC/INR')
            days: Number of days of historical data
            timeframe: Timeframe for candles
            
        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            all_candles = []
            since = self.exchange.parse8601(
                (datetime.now() - timedelta(days=days)).isoformat()
            )
            
            while since < self.exchange.milliseconds():
                ohlcv = self.exchange.fetch_ohlcv(
                    pair, timeframe=timeframe, since=since, limit=1000
                )
                if not ohlcv:
                    break
                all_candles.extend(ohlcv)
                since = ohlcv[-1][0] + 1
            
            df = pd.DataFrame(
                all_candles,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['pair'] = pair
            logger.info(f"✓ Fetched {len(df)} historical candles for {pair}")
            return df
        except Exception as e:
            logger.error(f"✗ Failed to fetch historical data for {pair}: {e}")
            return None

    def get_multiple_tickers(self, pairs: List[str]) -> Dict[str, Dict]:
        """
        Fetch tickers for multiple pairs.
        
        Args:
            pairs: List of trading pairs
            
        Returns:
            Dictionary with ticker data for each pair
        """
        tickers = {}
        for pair in pairs:
            ticker = self.get_ticker(pair)
            if ticker:
                tickers[pair] = ticker
        return tickers

    def validate_pair(self, pair: str) -> bool:
        """
        Check if a trading pair is valid on CoinDCX.
        
        Args:
            pair: Trading pair to validate
            
        Returns:
            True if pair is valid, False otherwise
        """
        try:
            return pair in self.exchange.symbols
        except Exception as e:
            logger.error(f"✗ Failed to validate pair {pair}: {e}")
            return False

    def get_supported_pairs(self) -> List[str]:
        """
        Get list of supported trading pairs on CoinDCX.
        
        Returns:
            List of supported pairs
        """
        try:
            return self.exchange.symbols
        except Exception as e:
            logger.error(f"✗ Failed to get supported pairs: {e}")
            return []

    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Series with VWAP values
        """
        try:
            df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
            return df['vwap']
        except Exception as e:
            logger.error(f"✗ Failed to calculate VWAP: {e}")
            return pd.Series()

    def get_market_regime(self, pair: str, timeframe: str = '1d', 
                         days: int = 30) -> Optional[str]:
        """
        Analyze market regime (bullish, bearish, sideways).
        
        Args:
            pair: Trading pair
            timeframe: Timeframe for analysis
            days: Number of days for analysis
            
        Returns:
            Market regime ('bullish', 'bearish', 'sideways') or None
        """
        try:
            df = self.get_historical_data(pair, days=days, timeframe=timeframe)
            if df is None or len(df) < 2:
                return None
            
            close_prices = df['close'].values
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            current_price = close_prices[-1]
            
            if current_price > sma_20 * 1.02:
                regime = 'bullish'
            elif current_price < sma_20 * 0.98:
                regime = 'bearish'
            else:
                regime = 'sideways'
            
            logger.info(f"✓ Market regime for {pair}: {regime}")
            return regime
        except Exception as e:
            logger.error(f"✗ Failed to analyze market regime for {pair}: {e}")
            return None
