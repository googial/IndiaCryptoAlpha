"""EMA Crossover + Supertrend Strategy Agent."""

import logging
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from .base_agent import BaseStrategyAgent
from core import MarketDataManager, RiskEngine, OrderExecutor

logger = logging.getLogger(__name__)


class EMASupertrendAgent(BaseStrategyAgent):
    """Strategy combining EMA crossover and Supertrend for trend following."""

    def __init__(self, pairs: List[str], risk_engine: RiskEngine,
                 order_executor: OrderExecutor, market_data: MarketDataManager):
        """Initialize EMA Crossover + Supertrend agent."""
        super().__init__("EMA Crossover + Supertrend", pairs, risk_engine, order_executor, market_data)
        self.ema_fast = 9
        self.ema_slow = 21
        self.supertrend_period = 10
        self.supertrend_multiplier = 3

    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        Args:
            prices: Price series
            period: EMA period
            
        Returns:
            EMA values
        """
        try:
            return prices.ewm(span=period, adjust=False).mean()
        except Exception as e:
            logger.error(f"✗ EMA calculation failed: {e}")
            return pd.Series()

    def calculate_supertrend(self, high: pd.Series, low: pd.Series, close: pd.Series,
                            period: int = 10, multiplier: float = 3) -> tuple:
        """
        Calculate Supertrend indicator.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
            multiplier: ATR multiplier
            
        Returns:
            Tuple of (supertrend, trend)
        """
        try:
            # Calculate ATR (Average True Range)
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()

            # Calculate basic bands
            hl_avg = (high + low) / 2
            basic_ub = hl_avg + multiplier * atr
            basic_lb = hl_avg - multiplier * atr

            # Calculate final bands
            final_ub = basic_ub.copy()
            final_lb = basic_lb.copy()

            for i in range(1, len(final_ub)):
                final_ub.iloc[i] = min(basic_ub.iloc[i], final_ub.iloc[i-1]) if close.iloc[i-1] > final_ub.iloc[i-1] else basic_ub.iloc[i]
                final_lb.iloc[i] = max(basic_lb.iloc[i], final_lb.iloc[i-1]) if close.iloc[i-1] < final_lb.iloc[i-1] else basic_lb.iloc[i]

            # Determine supertrend
            supertrend = pd.Series(index=close.index, dtype=float)
            trend = pd.Series(index=close.index, dtype=int)

            for i in range(len(close)):
                if i == 0:
                    supertrend.iloc[i] = final_ub.iloc[i]
                    trend.iloc[i] = 1
                else:
                    if close.iloc[i] <= final_ub.iloc[i]:
                        supertrend.iloc[i] = final_ub.iloc[i]
                        trend.iloc[i] = 1
                    else:
                        supertrend.iloc[i] = final_lb.iloc[i]
                        trend.iloc[i] = -1

            return supertrend, trend
        except Exception as e:
            logger.error(f"✗ Supertrend calculation failed: {e}")
            return pd.Series(), pd.Series()

    def generate_signal(self, pair: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on EMA crossover and Supertrend.
        
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
            high = data['high']
            low = data['low']

            # Calculate indicators
            ema_fast = self.calculate_ema(close, self.ema_fast)
            ema_slow = self.calculate_ema(close, self.ema_slow)
            supertrend, trend = self.calculate_supertrend(
                high, low, close, self.supertrend_period, self.supertrend_multiplier
            )

            # Get latest values
            current_price = close.iloc[-1]
            current_ema_fast = ema_fast.iloc[-1]
            current_ema_slow = ema_slow.iloc[-1]
            current_trend = trend.iloc[-1]

            prev_ema_fast = ema_fast.iloc[-2]
            prev_ema_slow = ema_slow.iloc[-2]
            prev_trend = trend.iloc[-2]

            signal = None

            # BUY signal: EMA fast crosses above slow + Supertrend uptrend
            if (prev_ema_fast <= prev_ema_slow and current_ema_fast > current_ema_slow and 
                current_trend == -1):
                signal = {
                    'side': 'BUY',
                    'confidence': 0.85,
                    'quantity': 0.1,
                    'reason': 'EMA fast crosses above slow + Supertrend uptrend',
                    'ema_fast': current_ema_fast,
                    'ema_slow': current_ema_slow,
                }

            # SELL signal: EMA fast crosses below slow + Supertrend downtrend
            elif (prev_ema_fast >= prev_ema_slow and current_ema_fast < current_ema_slow and 
                  current_trend == 1):
                signal = {
                    'side': 'SELL',
                    'confidence': 0.85,
                    'quantity': 0.1,
                    'reason': 'EMA fast crosses below slow + Supertrend downtrend',
                    'ema_fast': current_ema_fast,
                    'ema_slow': current_ema_slow,
                }

            return signal
        except Exception as e:
            logger.error(f"✗ Signal generation failed for {pair}: {e}")
            return None
