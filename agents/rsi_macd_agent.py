"""RSI + MACD Momentum Strategy Agent."""

import logging
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from .base_agent import BaseStrategyAgent
from core import MarketDataManager, RiskEngine, OrderExecutor

logger = logging.getLogger(__name__)


class RSIMACDAgent(BaseStrategyAgent):
    """Strategy combining RSI and MACD for momentum trading."""

    def __init__(self, pairs: List[str], risk_engine: RiskEngine,
                 order_executor: OrderExecutor, market_data: MarketDataManager):
        """Initialize RSI+MACD agent."""
        super().__init__("RSI+MACD Momentum", pairs, risk_engine, order_executor, market_data)
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Price series
            period: RSI period
            
        Returns:
            RSI values
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"✗ RSI calculation failed: {e}")
            return pd.Series()

    def calculate_macd(self, prices: pd.Series, fast: int = 12, 
                      slow: int = 26, signal: int = 9) -> tuple:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Tuple of (MACD, Signal, Histogram)
        """
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            macd_signal = macd.ewm(span=signal).mean()
            macd_histogram = macd - macd_signal
            return macd, macd_signal, macd_histogram
        except Exception as e:
            logger.error(f"✗ MACD calculation failed: {e}")
            return pd.Series(), pd.Series(), pd.Series()

    def generate_signal(self, pair: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on RSI and MACD.
        
        Args:
            pair: Trading pair
            data: OHLCV data
            
        Returns:
            Signal dictionary or None
        """
        try:
            if len(data) < 50:
                return None

            close = data['close']

            # Calculate indicators
            rsi = self.calculate_rsi(close, self.rsi_period)
            macd, macd_signal, macd_histogram = self.calculate_macd(
                close, self.macd_fast, self.macd_slow, self.macd_signal
            )

            # Get latest values
            current_rsi = rsi.iloc[-1]
            current_macd = macd.iloc[-1]
            current_signal = macd_signal.iloc[-1]
            prev_histogram = macd_histogram.iloc[-2]
            current_histogram = macd_histogram.iloc[-1]

            # Generate signals
            signal = None

            # BUY signal: RSI oversold + MACD bullish crossover
            if (current_rsi < self.rsi_oversold and 
                prev_histogram < 0 and current_histogram > 0):
                signal = {
                    'side': 'BUY',
                    'confidence': 0.8,
                    'quantity': 0.1,
                    'reason': 'RSI oversold + MACD bullish crossover',
                    'rsi': current_rsi,
                    'macd': current_macd,
                }

            # SELL signal: RSI overbought + MACD bearish crossover
            elif (current_rsi > self.rsi_overbought and 
                  prev_histogram > 0 and current_histogram < 0):
                signal = {
                    'side': 'SELL',
                    'confidence': 0.8,
                    'quantity': 0.1,
                    'reason': 'RSI overbought + MACD bearish crossover',
                    'rsi': current_rsi,
                    'macd': current_macd,
                }

            return signal
        except Exception as e:
            logger.error(f"✗ Signal generation failed for {pair}: {e}")
            return None
