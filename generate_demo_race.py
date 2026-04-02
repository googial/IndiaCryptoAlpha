"""Script to run a short simulated AI trading race for demonstration and testing."""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from race.orchestrator import RaceOrchestrator
from config import (
    LOG_LEVEL,
    NUM_RACE_AGENTS,
    RACE_DURATION_HOURS,
    RACE_UPDATE_INTERVAL_SEC,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/demo_race.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the demo race."""
    logger.info("=" * 80)
    logger.info("🚀 Starting IndiaAI Race Alpha Demo")
    logger.info("=" * 80)

    # Override some config for a shorter demo race
    demo_num_agents = min(NUM_RACE_AGENTS, 3)  # Max 3 agents for quick demo
    demo_race_duration_hours = min(RACE_DURATION_HOURS, 0.1)  # 6 minutes for demo

    orchestrator = RaceOrchestrator(num_agents=demo_num_agents)
    orchestrator.start_race()

    logger.info(
        f"Demo Race started with {demo_num_agents} agents for {demo_race_duration_hours * 60:.0f} minutes."
    )
    logger.info("Monitoring race progress...")

    try:
        # Keep the script running until the race ends
        while orchestrator.is_running:
            status = orchestrator.get_race_status()
            if status["time_remaining"]:
                logger.info(f"Time Remaining: {status['time_remaining'].split('.')[0]}")
            else:
                logger.info("Race ending soon...")
            time.sleep(RACE_UPDATE_INTERVAL_SEC)  # Wait for next update cycle

    except KeyboardInterrupt:
        logger.info("Demo race interrupted by user.")
    finally:
        orchestrator.stop_race()
        logger.info("Demo race finished.")
        orchestrator.print_leaderboard()


if __name__ == "__main__":
    main()
