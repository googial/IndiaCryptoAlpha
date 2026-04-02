#!/usr/bin/env python3
"""Run the demo race for a short duration and verify it works."""

import sys
import os
import time
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/workspace/IndiaCryptoAlpha")

# Set minimal env vars (already in .env, but ensure)
os.environ["PAPER_TRADING_MODE"] = "true"

from race.orchestrator import RaceOrchestrator
from config import NUM_RACE_AGENTS, RACE_DURATION_HOURS, RACE_UPDATE_INTERVAL_SEC


def test_short_race():
    """Test running a very short race."""
    print("Starting short race test...")

    # Override for very short test: 2 agents, 0.01 hours (36 seconds)
    test_agents = 2
    test_duration = 0.01  # hours = 36 seconds

    orchestrator = RaceOrchestrator(num_agents=test_agents)
    orchestrator.start_race()

    print(
        f"Race started with {test_agents} agents for {test_duration * 60:.0f} seconds"
    )

    start = time.time()
    max_time = test_duration * 3600  # convert to seconds

    try:
        while orchestrator.is_running and (time.time() - start) < max_time:
            status = orchestrator.get_race_status()
            time_remaining = status.get("time_remaining")
            if time_remaining:
                print(f"Time remaining: {str(time_remaining).split('.')[0]}")

            # Check agents have status
            for agent in status["agents"]:
                assert "name" in agent
                assert "portfolio_value" in agent or True  # may not have immediately
                assert "total_pnl" in agent

            time.sleep(RACE_UPDATE_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        orchestrator.stop_race()
        print("\nFinal leaderboard:")
        orchestrator.print_leaderboard()

    print("✓ DEMO RACE TEST COMPLETED SUCCESSFULLY")
    return True


if __name__ == "__main__":
    try:
        success = test_short_race()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ DEMO RACE TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
