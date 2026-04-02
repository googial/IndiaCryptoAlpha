#!/usr/bin/env python3
"""Test that the race orchestrator can be imported and initialized."""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/workspace/IndiaCryptoAlpha")

# Set minimal env vars for testing
os.environ["PAPER_TRADING_MODE"] = "true"
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-demo"
os.environ["LLM_PROVIDER"] = "openai"

try:
    print("Importing RaceOrchestrator...")
    from race.orchestrator import RaceOrchestrator

    print("Creating orchestrator with 2 agents...")
    orchestrator = RaceOrchestrator(num_agents=2)

    print("Orchestrator created successfully")
    print(f"  - Number of agents: {len(orchestrator.agents)}")
    print(f"  - Agent names: {[a.name for a in orchestrator.agents]}")

    # Test start/stop quickly
    print("Starting race...")
    orchestrator.start_race()

    print("Getting race status...")
    status = orchestrator.get_race_status()
    print(f"  - Running: {status['is_running']}")
    print(f"  - Agents: {len(status['agents'])}")

    print("Stopping race...")
    orchestrator.stop_race()

    print("\n✓ ORCHESTRATOR TEST PASSED")
    sys.exit(0)

except Exception as e:
    print(f"\n✗ ORCHESTRATOR TEST FAILED: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
