#!/usr/bin/env python3
"""
Comprehensive test for IndiaCryptoAlpha demo race.
Tests all critical components and verifies they work correctly.
"""

import sys
import os
import time
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/workspace/IndiaCryptoAlpha")

# Set test environment variables
os.environ["PAPER_TRADING_MODE"] = "true"
os.environ["OPENAI_API_KEY"] = "sk-test-for-demo"
os.environ["LLM_PROVIDER"] = "openai"


def test_market_data():
    """Test MarketDataManager with mock data."""
    print("Testing MarketDataManager...")
    from core.market_data import MarketDataManager

    md = MarketDataManager()

    # Test ticker
    ticker = md.get_ticker("BTC-INR")
    assert ticker["last"] > 0, f"Mock ticker should return positive price, got {ticker}"
    assert "bid" in ticker and "ask" in ticker
    print(f"  ✓ Ticker for BTC-INR: {ticker['last']:+,.2f}")

    # Test candles
    candles = md.get_candles("BTC-INR", interval="5m", limit=10)
    assert len(candles) == 10, f"Expected 10 candles, got {len(candles)}"
    assert all(
        "open" in c and "high" in c and "low" in c and "close" in c for c in candles
    )
    print(f"  ✓ Got {len(candles)} mock candles, structure valid")

    # Test OHLCV DataFrame
    df = md.get_ohlcv("BTC-INR", "5m", 10)
    assert not df.empty, "OHLCV DataFrame should not be empty"
    assert len(df) == 10, f"Expected 10 OHLCV rows, got {len(df)}"
    assert all(col in df.columns for col in ["open", "high", "low", "close", "volume"])
    print(f"  ✓ OHLCV DataFrame shape: {df.shape}")

    return True


def test_risk_engine():
    """Test RiskEngine functionality."""
    print("Testing RiskEngine...")
    from core.risk_engine import RiskEngine

    re = RiskEngine(initial_portfolio=100000)
    assert re.current_portfolio == 100000
    print(f"  ✓ Initial portfolio: ₹{re.current_portfolio:,.2f}")

    return True


def test_agents():
    """Test agent initialization and basic functionality."""
    print("Testing trading agents...")
    from core import MarketDataManager, RiskEngine, OrderExecutor
    from agents.llm_agent import LLMTradingAgent

    md = MarketDataManager()
    re = RiskEngine(100000)
    oe = OrderExecutor()

    agent = LLMTradingAgent(
        name="Test-Agent",
        pairs=["BTC-INR", "ETH-INR"],
        risk_engine=re,
        order_executor=oe,
        market_data=md,
    )

    print(f"  ✓ Agent '{agent.name}' initialized")
    return True


def test_short_race():
    """Test running a very short race with real components."""
    print("Testing short race simulation...")
    from race.orchestrator import RaceOrchestrator
    from config import RACE_UPDATE_INTERVAL_SEC

    # Create orchestrator with 2 agents
    orchestrator = RaceOrchestrator(num_agents=2)

    # Start race
    orchestrator.start_race()

    print(f"  ✓ Race started")

    # Run for 15 seconds (3 cycles if interval is 5s)
    time.sleep(15)

    # Get status
    status = orchestrator.get_race_status()
    assert status["is_running"], "Race should be running"
    assert len(status["agents"]) == 2, "Should have 2 agents"

    print(f"  ✓ Race status: {status['time_remaining']}")
    for agent in status["agents"]:
        print(
            f"    - {agent['name']}: P&L ₹{agent['total_pnl']:,.2f}, Trades: {agent['total_trades']}"
        )

    # Stop race
    orchestrator.stop_race()
    print("  ✓ Race stopped successfully")

    return True


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("IndiaCryptoAlpha Comprehensive Test Suite")
    print("=" * 60)

    tests = [
        ("MarketDataManager", test_market_data),
        ("RiskEngine", test_risk_engine),
        ("Trading Agents", test_agents),
        ("Short Race", test_short_race),
    ]

    results = []
    for name, test_fn in tests:
        try:
            success = test_fn()
            results.append((name, success, None))
        except Exception as e:
            print(f"  ✗ {name} test failed: {e}")
            results.append((name, False, str(e)))
        print()  # Empty line between tests

    print("=" * 60)
    print("Test Results:")
    all_passed = True
    for name, success, err in results:
        status = "✓ PASS" if success else f"✗ FAIL: {err}"
        print(f"  {name}: {status}")
        if not success:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
