#!/usr/bin/env python3
"""
Final verification script for IndiaCryptoAlpha installation.
Tests all components work correctly with mock data.
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/workspace/IndiaCryptoAlpha")

# Ensure test environment
os.environ["PAPER_TRADING_MODE"] = "true"


def test_imports():
    """Verify all imports work."""
    print("Testing imports...")
    modules = [
        "ccxt",
        "pandas",
        "numpy",
        "streamlit",
        "plotly",
        "openai",
        "anthropic",
        "google.generativeai",
        "requests",
        "APScheduler",
        "SQLAlchemy",
        "openpyxl",
        "ta",
    ]
    failed = []
    for mod in modules:
        try:
            __import__(mod)
        except ImportError as e:
            failed.append((mod, str(e)))

    if failed:
        for mod, err in failed:
            print(f"  ✗ {mod}: {err}")
        return False

    print(f"  ✓ All {len(modules)} core modules imported")
    return True


def test_market_data():
    """Verify market data returns mock data."""
    print("Testing MarketDataManager...")
    from core.market_data import MarketDataManager

    md = MarketDataManager()

    ticker = md.get_ticker("BTC-INR")
    assert ticker["last"] > 0, "Should return mock price"

    df = md.get_ohlcv("ETH-INR", "5m", 10)
    assert not df.empty, "Should return mock candles"
    assert len(df) == 10

    print(f"  ✓ Mock data: BTC-INR ₹{ticker['last']:,.2f}, {len(df)} ETH candles")
    return True


def test_risk_engine():
    """Verify risk engine works."""
    print("Testing RiskEngine...")
    from core.risk_engine import RiskEngine

    re = RiskEngine(100000)
    assert re.current_portfolio == 100000

    print(f"  ✓ Portfolio: ₹{re.current_portfolio:,.2f}")
    return True


def test_agents():
    """Verify agents can be created."""
    print("Testing trading agents...")
    from core import MarketDataManager, RiskEngine, OrderExecutor
    from agents.llm_agent import LLMTradingAgent

    agent = LLMTradingAgent(
        name="Test-01",
        pairs=["BTC-INR", "ETH-INR"],
        risk_engine=RiskEngine(100000),
        order_executor=OrderExecutor(),
        market_data=MarketDataManager(),
    )

    assert agent.name == "Test-01"
    assert len(agent.pairs) == 2

    print(f"  ✓ Agent '{agent.name}' created with {len(agent.pairs)} pairs")
    return True


def test_dashboard_import():
    """Verify dashboard script can be imported."""
    print("Testing dashboard import...")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "race_app", "/workspace/IndiaCryptoAlpha/dashboard/race_app.py"
    )
    # We can't actually run the module (it needs streamlit runtime)
    # But we can compile it to verify syntax
    with open("/workspace/IndiaCryptoAlpha/dashboard/race_app.py") as f:
        compile(f.read(), "race_app.py", "exec")
    print("  ✓ Dashboard script syntax valid")
    return True


def test_generate_demo_race_syntax():
    """Verify generate_demo_race.py syntax."""
    print("Testing generate_demo_race.py...")
    with open("/workspace/IndiaCryptoAlpha/generate_demo_race.py") as f:
        compile(f.read(), "generate_demo_race.py", "exec")
    print("  ✓ Demo race script syntax valid")
    return True


def test_env_file():
    """Verify .env exists with required keys."""
    print("Testing .env...")
    env_path = Path("/workspace/IndiaCryptoAlpha/.env")
    if not env_path.exists():
        print("  ✗ .env file missing")
        return False

    content = env_path.read_text()
    required = [
        "COINDCX_API_KEY",
        "COINDCX_API_SECRET",
        "TELEGRAM_BOT_TOKEN",
        "PAPER_TRADING_MODE",
    ]
    missing = [k for k in required if k not in content]

    if missing:
        print(f"  ✗ Missing keys: {missing}")
        return False

    print("  ✓ .env has all required configuration keys")
    return True


def test_logs_dirs():
    """Verify required directories exist."""
    print("Testing directories...")
    for d in ["logs", "data"]:
        path = Path(f"/workspace/IndiaCryptoAlpha/{d}")
        if not path.exists():
            print(f"  ✗ Missing directory: {d}")
            return False

    print("  ✓ Required directories exist (logs, data)")
    return True


def test_short_race_execution():
    """Test actual race execution briefly."""
    print("Testing race execution (10 seconds)...")
    from race.orchestrator import RaceOrchestrator

    orchestrator = RaceOrchestrator(num_agents=2)
    orchestrator.start_race()

    time.sleep(10)

    status = orchestrator.get_race_status()
    # Even with mock data, the race should be running
    assert status["is_running"], "Race should be running"
    assert len(status["agents"]) == 2

    orchestrator.stop_race()

    # Print leaderboard
    sorted_agents = sorted(
        orchestrator.agents, key=lambda a: a.risk_engine.current_portfolio, reverse=True
    )

    print("  ✓ Race ran for 10s with 2 agents")
    for i, agent in enumerate(sorted_agents):
        pnl = agent.risk_engine.current_portfolio - 100000
        print(
            f"    #{i + 1} {agent.name}: ₹{pnl:+,.2f}, {agent.performance['total_trades']} trades"
        )
    return True


def test_dashboard_start():
    """Test that streamlit can start the dashboard."""
    print("Testing dashboard startup...")

    env = os.environ.copy()
    env["PYTHONPATH"] = "/workspace/IndiaCryptoAlpha"
    env["PAPER_TRADING_MODE"] = "true"

    # Start streamlit
    proc = subprocess.Popen(
        [
            "/workspace/IndiaCryptoAlpha/venv/bin/streamlit",
            "run",
            "dashboard/race_app.py",
            "--server.port",
            "8502",
            "--server.headless",
            "true",
        ],
        cwd="/workspace/IndiaCryptoAlpha",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Give it time to start
    import socket

    time.sleep(8)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"  ✗ Streamlit failed (exit {proc.returncode})")
        print(f"  stderr: {stderr.decode()[-500:]}")
        return False

    # Test if port is up
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 8502))
    sock.close()

    proc.terminate()
    proc.wait()

    if result == 0:
        print("  ✓ Dashboard starts and serves on port 8502")
        return True
    else:
        print("  ✗ Dashboard port not accessible")
        return False


def run_all():
    print("=" * 60)
    print("IndiaCryptoAlpha - Final Installation Verification")
    print("=" * 60)

    tests = [
        ("Core Imports", test_imports),
        ("Market Data (Mock)", test_market_data),
        ("Risk Engine", test_risk_engine),
        ("Trading Agents", test_agents),
        ("Dashboard Syntax", test_dashboard_import),
        ("Demo Race Script", test_generate_demo_race_syntax),
        ("Environment File", test_env_file),
        ("Required Directories", test_logs_dirs),
        ("Race Execution", test_short_race_execution),
        ("Dashboard Startup", test_dashboard_start),
    ]

    results = []
    for name, fn in tests:
        try:
            success = fn()
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            import traceback

            traceback.print_exc()
            success = False
        results.append((name, success))
        print()

    print("=" * 60)
    passed = sum(1 for _, s in results if s)
    total = len(results)

    for name, s in results:
        status = "✓ PASS" if s else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\n{passed}/{total} tests passed")
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_all())
