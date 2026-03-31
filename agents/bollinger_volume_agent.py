"""Bollinger Band + Volume Breakout Strategy Agent."""

import logging
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from .base_agent import BaseStrategyAgent
from core import MarketDataManager, RiskEngine, OrderExecutor

logger = logging.getLogger(__name__)


class BollingerVolumeAgent(BaseStrategyAgent):
    """Strategy combining Bollinger Bands and volume for breakout trading."""

    def __init__(self, pairs: List[str], risk_engine: RiskEngine,
                 order_executor: OrderExecutor, market_data: MarketDataManager):
        """Initialize Bollinger Band + Volume agent."""
        super().__init__("Bollinger Band + Volume", pairs, risk_engine, order_executor, market_data)
        self.bb_period = 20
        self.bb_std_dev = 2
        self.volume_multiplier = 1.5

    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, 
                                 std_dev: float = 2) -> tuple:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: Price series
            period: MA period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        try:
            middle = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            return upper, middle, lower
        except Exception as e:
            logger.error(f"✗ Bollinger Bands calculation failed: {e}")
            return pd.Series(), pd.Series(), pd.Series()

    def calculate_volume_sma(self, volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate volume simple moving average.
        
        Args:
            volume: Volume series
            period: MA period
            
        Returns:
            Volume SMA
        """
        try:
            return volume.rolling(window=period).mean()
        except Exception as e:
            logger.error(f"✗ Volume SMA calculation failed: {e}")
            return pd.Series()

    def generate_signal(self, pair: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on Bollinger Bands and volume.
        
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
            volume = data['volume']

            # Calculate indicators
            upper, middle, lower = self.calculate_bollinger_bands(
                close, self.bb_period, self.bb_std_dev
            )
            volume_sma = self.calculate_volume_sma(volume, self.bb_period)

            # Get latest values
            current_price = close.iloc[-1]
            current_volume = volume.iloc[-1]
            current_upper = upper.iloc[-1]
            current_lower = lower.iloc[-1]
            avg_volume = volume_sma.iloc[-1]

            prev_price = close.iloc[-2]
            prev_upper = upper.iloc[-2]
            prev_lower = lower.iloc[-2]

            signal = None

            # BUY signal: Price breaks upper band + high volume
            if (prev_price <= prev_upper and current_price > current_upper and 
                current_volume > avg_volume * self.volume_multiplier):
                signal = {
                    'side': 'BUY',
                    'confidence': 0.75,
                    'quantity': 0.1,
                    'reason': 'Breakout above upper Bollinger Band with high volume',
                    'price': current_price,
                    'volume_ratio': current_volume / avg_volume,
                }

            # SELL signal: Price breaks lower band + high volume
            elif (prev_price >= prev_lower and current_price < current_lower and 
                  current_volume > avg_volume * self.volume_multiplier):
                signal = {
                    'side': 'SELL',
                    'confidence': 0.75,
                    'quantity': 0.1,
                    'reason': 'Breakout below lower Bollinger Band with high volume',
                    'price': current_price,
                    'volume_ratio': current_volume / avg_volume,
                }

            return signal
        except Exception as e:
            logger.error(f"✗ Signal generation failed for {pair}: {e}")
            return None
