#!/usr/bin/env python3
"""
Test multi-exchange integration: Binance and CoinDCX.
Verifies that the exchange abstraction works correctly with both implementations.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, "/workspace")
from config import PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT))

from core.exchange_base import ExchangeFactory, BaseExchange
from core.binance_exchange import BinanceExchange
from core.coindcx_exchange import CoinDCXExchange

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_exchange_factory():
    """Test that ExchangeFactory creates both exchange types."""
    print("Testing ExchangeFactory...")

    # Test Binance with empty keys (should still create)
    binance: BaseExchange = ExchangeFactory.create_exchange(
        "binance", api_key="", api_secret=""
    )
    assert isinstance(binance, BinanceExchange), (
        "Should create BinanceExchange instance"
    )
    assert binance.exchange_name == "binance"
    print("  ✓ BinanceExchange created via factory")

    # Test CoinDCX with empty keys (should still create with mock data)
    coindcx: BaseExchange = ExchangeFactory.create_exchange(
        "coindcx", api_key="", api_secret=""
    )
    assert isinstance(coindcx, CoinDCXExchange), (
        "Should create CoinDCXExchange instance"
    )
    assert coindcx.exchange_name == "coindcx"
    print("  ✓ CoinDCXExchange created via factory")

    # Test case insensitivity
    binance2 = ExchangeFactory.create_exchange("BINANCE")
    assert isinstance(binance2, BinanceExchange)
    print("  ✓ Factory is case-insensitive")

    # Test invalid exchange raises
    try:
        ExchangeFactory.create_exchange("unknown")
        assert False, "Should raise for unsupported exchange"
    except ValueError as e:
        assert "Unsupported exchange" in str(e)
        print("  ✓ Unknown exchange raises ValueError")

    return True


def test_binance_exchange():
    """Test BinanceExchange basic methods."""
    print("Testing BinanceExchange...")
    from config import BINANCE_API_KEY, BINANCE_SECRET_KEY

    exchange = BinanceExchange(BINANCE_API_KEY, BINANCE_SECRET_KEY)

    # Test ticker (BTC/USDT)
    ticker = exchange.get_ticker("BTC-USDT")
    assert ticker is not None, "Ticker should not be None"
    assert "last" in ticker, "Ticker should have 'last' price"
    assert ticker["last"] > 0, f"Last price should be positive, got {ticker['last']}"
    assert "bid" in ticker and "ask" in ticker
    print(
        f"  ✓ Ticker BTC-USDT: last=${ticker['last']:.2f}, bid={ticker['bid']:.2f}, ask={ticker['ask']:.2f}"
    )

    # Test candles
    candles = exchange.get_candles("BTC-USDT", interval="1h", limit=5)
    assert len(candles) == 5, f"Expected 5 candles, got {len(candles)}"
    assert all("open" in c and "close" in c for c in candles)
    print(f"  ✓ Got {len(candles)} candles")

    # Test get_ohlcv returns DataFrame
    df = exchange.get_ohlcv("BTC-USDT", "1h", 5)
    assert not df.empty, "OHLCV DataFrame should not be empty"
    assert all(col in df.columns for col in ["open", "high", "low", "close", "volume"])
    print(f"  ✓ OHLCV DataFrame shape: {df.shape}")

    # Test get_balance (authenticated, might be empty if no key)
    balance = exchange.get_balance()
    assert isinstance(balance, dict), "Balance should be a dict"
    print(f"  ✓ Balance fetched (assets: {len(balance)})")

    # Test get_open_orders
    orders = exchange.get_open_orders()
    assert isinstance(orders, list), "Open orders should be a list"
    print(f"  ✓ Open orders fetched: {len(orders)}")

    return True


def test_coindcx_exchange():
    """Test CoinDCXExchange (should work with mock data if no API key)."""
    print("Testing CoinDCXExchange...")

    exchange = CoinDCXExchange(api_key="", api_secret="")  # mock mode

    # Test ticker (BTC-INR)
    ticker = exchange.get_ticker("BTC-INR")
    assert ticker is not None
    assert ticker["last"] > 0
    print(f"  ✓ Mock ticker BTC-INR: ₹{ticker['last']:.2f}")

    # Test candles
    candles = exchange.get_candles("BTC-INR", interval="5m", limit=10)
    assert len(candles) == 10
    print(f"  ✓ Mock candles: {len(candles)}")

    # Test get_ohlcv
    df = exchange.get_ohlcv("BTC-INR", "1h", 10)
    assert not df.empty
    print(f"  ✓ OHLCV DataFrame shape: {df.shape}")

    # Test get_balance with no API key (should return empty)
    balance = exchange.get_balance()
    assert isinstance(balance, dict)
    print(f"  ✓ Balance (no auth): empty as expected")

    return True


def test_market_data_manager():
    """Test MarketDataManager uses the correct exchange based on config."""
    print("Testing MarketDataManager with config switching...")

    from core.market_data import MarketDataManager
    import config as config_mod

    # Test with Binance
    original_exchange = config_mod.EXCHANGE_NAME
    config_mod.EXCHANGE_NAME = "binance"
    mdm_binance = MarketDataManager()
    assert mdm_binance.exchange_name == "binance"
    ticker = mdm_binance.get_ticker("BTC-USDT")
    assert ticker["last"] > 0
    print(f"  ✓ MarketDataManager with Binance: last=${ticker['last']:.2f}")

    # Test with CoinDCX
    config_mod.EXCHANGE_NAME = "coindcx"
    mdm_coindcx = MarketDataManager()
    assert mdm_coindcx.exchange_name == "coindcx"
    ticker2 = mdm_coindcx.get_ticker("BTC-INR")
    assert ticker2["last"] > 0
    print(f"  ✓ MarketDataManager with CoinDCX: last=₹{ticker2['last']:.2f}")

    # Restore original
    config_mod.EXCHANGE_NAME = original_exchange

    return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("MULTI-EXCHANGE INTEGRATION TESTS")
    print("=" * 70)

    tests = [
        ("ExchangeFactory", test_exchange_factory),
        ("BinanceExchange", test_binance_exchange),
        ("CoinDCXExchange", test_coindcx_exchange),
        ("MarketDataManager", test_market_data_manager),
    ]

    results = []
    for name, test_fn in tests:
        try:
            success = test_fn()
            results.append((name, success, None))
        except Exception as e:
            print(f"  ✗ {name} FAILED: {e}")
            results.append((name, False, str(e)))
        print()

    print("=" * 70)
    print("RESULTS:")
    all_passed = True
    for name, success, err in results:
        status = "✓ PASS" if success else f"✗ FAIL: {err}"
        print(f"  {name}: {status}")
        if not success:
            all_passed = False
    print("=" * 70)

    if all_passed:
        print("✓ ALL INTEGRATION TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
