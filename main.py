"""Main orchestrator for IndiaAI Race Alpha trading system."""

import logging
import sys
import time
import os
import threading
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from config import LOG_LEVEL, NUM_RACE_AGENTS, RACE_DURATION_HOURS, INITIAL_PORTFOLIO
from race.orchestrator import RaceOrchestrator

# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(logs_dir / "trading_system.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def _run_api_server():
    """Run Flask API server for dashboard integration."""
    try:
        import importlib

        api_server = importlib.import_module("api_server")
        app = api_server.create_app()
        port = int(os.getenv("API_PORT", "5000"))
        logger.info(f"API server started on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"API server failed to start: {e}", exc_info=True)


def main():
    """Main entry point for the IndiaAI Race Alpha system."""
    logger.info("=" * 80)
    logger.info("IndiaAI Race Alpha Trading System Starting")
    logger.info("=" * 80)
    logger.info(
        f"Configured for {NUM_RACE_AGENTS} agents over {RACE_DURATION_HOURS} hours."
    )

    # Start the backend API server in a daemon thread
    api_thread = threading.Thread(target=_run_api_server, daemon=True)
    api_thread.start()
    logger.info("API server thread started (background)")

    orchestrator = None
    try:
        orchestrator = RaceOrchestrator(num_agents=NUM_RACE_AGENTS)
        orchestrator.start_race()

        # Keep the main thread alive while scheduler runs in background
        while orchestrator.is_running:
            time.sleep(1)  # Sleep to prevent busy-waiting
    except KeyboardInterrupt:
        logger.info("Race interrupted by user. Stopping race...")
    except Exception as e:
        logger.error(f"Fatal error in main orchestrator: {e}", exc_info=True)
    finally:
        if orchestrator:
            orchestrator.stop_race()
        logger.info("IndiaAI Race Alpha Trading System Stopped.")
        if orchestrator:
            orchestrator.print_leaderboard()


if __name__ == "__main__":
    main()
