"""
SciPy Utilities - Graceful Fallback Module

This module provides scipy-based calculations with automatic fallback
to numpy-based alternatives if scipy is not available.

Useful for Termux environments where scipy cannot be installed due to
missing Fortran compiler.
"""

import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Try to import scipy
try:
    from scipy import signal, stats
    SCIPY_AVAILABLE = True
    logger.info("✓ SciPy available - using optimized calculations")
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("⚠ SciPy not available - using numpy fallback (limited features)")


def calculate_rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
    """
    Calculate Relative Strength Index (RSI).
    
    Works with or without scipy.
    
    Args:
        prices: Array of prices
        period: RSI period (default: 14)
    
    Returns:
        RSI values
    """
    if len(prices) < period + 1:
        return np.full(len(prices), np.nan)
    
    deltas = np.diff(prices)
    seed = deltas[:period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)
    
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    
    return rsi


def calculate_macd(prices: np.ndarray, 
                  fast: int = 12, 
                  slow: int = 26, 
                  signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Works with or without scipy.
    
    Args:
        prices: Array of prices
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)
    
    Returns:
        Tuple of (MACD, Signal, Histogram)
    """
    # Calculate EMAs
    ema_fast = _exponential_moving_average(prices, fast)
    ema_slow = _exponential_moving_average(prices, slow)
    
    # MACD line
    macd = ema_fast - ema_slow
    
    # Signal line
    signal = _exponential_moving_average(macd, signal_period)
    
    # Histogram
    histogram = macd - signal
    
    return macd, signal, histogram


def calculate_bollinger_bands(prices: np.ndarray, 
                             period: int = 20, 
                             num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate Bollinger Bands.
    
    Works with or without scipy.
    
    Args:
        prices: Array of prices
        period: Moving average period (default: 20)
        num_std: Number of standard deviations (default: 2.0)
    
    Returns:
        Tuple of (Upper Band, Middle Band, Lower Band)
    """
    # Middle band (SMA)
    middle = _simple_moving_average(prices, period)
    
    # Standard deviation
    std = np.zeros_like(prices)
    for i in range(period - 1, len(prices)):
        std[i] = np.std(prices[i - period + 1:i + 1])
    
    # Bands
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    
    return upper, middle, lower


def calculate_supertrend(high: np.ndarray, 
                        low: np.ndarray, 
                        close: np.ndarray, 
                        period: int = 10, 
                        multiplier: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate Supertrend indicator.
    
    Works with or without scipy.
    
    Args:
        high: Array of high prices
        low: Array of low prices
        close: Array of close prices
        period: ATR period (default: 10)
        multiplier: ATR multiplier (default: 3.0)
    
    Returns:
        Tuple of (Supertrend, Trend Direction)
    """
    # Calculate ATR
    atr = _calculate_atr(high, low, close, period)
    
    # Calculate HL2
    hl2 = (high + low) / 2
    
    # Calculate basic bands
    basic_ub = hl2 + multiplier * atr
    basic_lb = hl2 - multiplier * atr
    
    # Calculate final bands
    final_ub = np.zeros_like(basic_ub)
    final_lb = np.zeros_like(basic_lb)
    
    final_ub[0] = basic_ub[0]
    final_lb[0] = basic_lb[0]
    
    for i in range(1, len(basic_ub)):
        final_ub[i] = basic_ub[i] if basic_ub[i] < final_ub[i - 1] or close[i - 1] > final_ub[i - 1] else final_ub[i - 1]
        final_lb[i] = basic_lb[i] if basic_lb[i] > final_lb[i - 1] or close[i - 1] < final_lb[i - 1] else final_lb[i - 1]
    
    # Calculate supertrend
    supertrend = np.zeros_like(close)
    trend = np.zeros_like(close)
    
    for i in range(len(close)):
        if i == 0:
            supertrend[i] = final_ub[i]
            trend[i] = -1
        else:
            if supertrend[i - 1] == final_ub[i - 1]:
                supertrend[i] = final_ub[i]
                trend[i] = -1 if close[i] <= final_ub[i] else 1
            else:
                supertrend[i] = final_lb[i]
                trend[i] = 1 if close[i] >= final_lb[i] else -1
    
    return supertrend, trend


# ============================================================================
# Helper Functions
# ============================================================================

def _exponential_moving_average(data: np.ndarray, period: int) -> np.ndarray:
    """Calculate exponential moving average."""
    if len(data) < period:
        return np.full(len(data), np.nan)
    
    ema = np.zeros_like(data)
    ema[:period] = np.mean(data[:period])
    
    multiplier = 2 / (period + 1)
    
    for i in range(period, len(data)):
        ema[i] = (data[i] * multiplier) + (ema[i - 1] * (1 - multiplier))
    
    return ema


def _simple_moving_average(data: np.ndarray, period: int) -> np.ndarray:
    """Calculate simple moving average."""
    if len(data) < period:
        return np.full(len(data), np.nan)
    
    sma = np.zeros_like(data)
    
    for i in range(period - 1, len(data)):
        sma[i] = np.mean(data[i - period + 1:i + 1])
    
    return sma


def _calculate_atr(high: np.ndarray, 
                   low: np.ndarray, 
                   close: np.ndarray, 
                   period: int = 14) -> np.ndarray:
    """Calculate Average True Range."""
    tr = np.zeros_like(close)
    
    for i in range(len(close)):
        if i == 0:
            tr[i] = high[i] - low[i]
        else:
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
    
    atr = _exponential_moving_average(tr, period)
    return atr


# ============================================================================
# Scipy-Specific Functions (Optional)
# ============================================================================

def calculate_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate Pearson correlation coefficient.
    
    Uses scipy if available, otherwise numpy.
    """
    if SCIPY_AVAILABLE:
        return stats.pearsonr(x, y)[0]
    else:
        return np.corrcoef(x, y)[0, 1]


def calculate_zscore(data: np.ndarray, window: int = 20) -> np.ndarray:
    """
    Calculate Z-score (standard score).
    
    Uses scipy if available, otherwise numpy.
    """
    if SCIPY_AVAILABLE:
        return stats.zscore(data)
    else:
        mean = np.mean(data)
        std = np.std(data)
        return (data - mean) / std if std != 0 else np.zeros_like(data)


# ============================================================================
# Module Status
# ============================================================================

def get_status() -> dict:
    """Get module status and available features."""
    return {
        "scipy_available": SCIPY_AVAILABLE,
        "features": {
            "rsi": True,
            "macd": True,
            "bollinger_bands": True,
            "supertrend": True,
            "correlation": SCIPY_AVAILABLE,
            "zscore": SCIPY_AVAILABLE,
        },
        "mode": "Full" if SCIPY_AVAILABLE else "Termux (Limited)"
    }


if __name__ == "__main__":
    # Print status
    status = get_status()
    print("SciPy Utils Status:")
    print(f"  SciPy Available: {status['scipy_available']}")
    print(f"  Mode: {status['mode']}")
    print(f"  Features: {status['features']}")
