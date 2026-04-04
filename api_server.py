"""API Control Server for IndiaCryptoAlpha.

Provides RESTful endpoints to control the trading system and agents.
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    LOG_LEVEL,
    NUM_RACE_AGENTS,
    RACE_DURATION_HOURS,
    INITIAL_PORTFOLIO,
    SUPPORTED_PAIRS,
    DATA_DIR,
)
from race.orchestrator import RaceOrchestrator
from logger import AccountantAgent, TradeDatabase
from core import MarketDataManager, RiskEngine, OrderExecutor
from agents.llm_agent import LLMTradingAgent

logger = logging.getLogger(__name__)

# Global state (in production, use Redis or a database)
_orchestrator: Optional[RaceOrchestrator] = None
_orchestrator_lock = threading.Lock()
_api_key_file = DATA_DIR / "api_keys.json"
_config_file = project_root / ".env"
_allow_api_control = os.getenv("ALLOW_API_CONTROL", "false").lower() == "true"


def _load_api_keys() -> Dict:
    """Load stored API keys."""
    if _api_key_file.exists():
        try:
            with open(_api_key_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
    return {}


def _save_api_keys(keys: Dict):
    """Save API keys."""
    try:
        with open(_api_key_file, "w") as f:
            json.dump(keys, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save API keys: {e}")


def _load_config() -> Dict:
    """Load configuration from .env."""
    config = {}
    if _config_file.exists():
        with open(_config_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip().strip("\"'")
    return config


def _save_config(config: Dict):
    """Save configuration to .env."""
    try:
        # Read existing lines to preserve structure
        existing_lines = []
        if _config_file.exists():
            with open(_config_file, "r") as f:
                existing_lines = f.readlines()

        # Build new config
        new_lines = []
        for line in existing_lines:
            line = line.rstrip("\n")
            if line.strip() and not line.strip().startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                if key in config:
                    new_lines.append(f"{key}={config[key]}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Append new keys if not present
        for key, value in config.items():
            if not any(
                line.split("=", 1)[0].strip() == key
                for line in new_lines
                if "=" in line
            ):
                new_lines.append(f"{key}={value}")

        with open(_config_file, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        logger.info("Configuration saved")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")


def create_app() -> Flask:
    """Create and configure the Flask API app."""
    app = Flask(__name__)
    CORS(app)  # Allow cross-origin requests from dashboard

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify(
            {
                "status": "healthy",
                "orchestrator_running": _orchestrator is not None
                and _orchestrator.is_running,
                "timestamp": datetime.now().isoformat(),
            }
        )

    # -------------------------------------------------------------------------
    # Race Control
    # -------------------------------------------------------------------------
    @app.route("/api/race/start", methods=["POST"])
    def start_race():
        """Start the trading race."""
        global _orchestrator
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        with _orchestrator_lock:
            if _orchestrator and _orchestrator.is_running:
                return jsonify({"error": "Race already running"}), 400

            try:
                # Reload config from .env if updated via API
                from config import load_dotenv

                load_dotenv()
                import importlib
                import config as config_mod

                importlib.reload(config_mod)

                _orchestrator = RaceOrchestrator(num_agents=NUM_RACE_AGENTS)
                _orchestrator.start_race()
                logger.info("Race started via API")
                return jsonify({"status": "started", "num_agents": NUM_RACE_AGENTS})
            except Exception as e:
                logger.error(f"Failed to start race: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route("/api/race/stop", methods=["POST"])
    def stop_race():
        """Stop the trading race."""
        global _orchestrator
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        with _orchestrator_lock:
            if not _orchestrator:
                return jsonify({"error": "Race not initialized"}), 400

            try:
                _orchestrator.stop_race()
                logger.info("Race stopped via API")
                return jsonify({"status": "stopped"})
            except Exception as e:
                logger.error(f"Failed to stop race: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route("/api/race/status", methods=["GET"])
    def get_race_status():
        """Get current race status."""
        with _orchestrator_lock:
            if not _orchestrator:
                return jsonify(
                    {"is_running": False, "num_agents": NUM_RACE_AGENTS, "agents": []}
                )

            try:
                status = _orchestrator.get_race_status()
                return jsonify(status)
            except Exception as e:
                logger.error(f"Failed to get race status: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route("/api/race/leaderboard", methods=["GET"])
    def get_leaderboard():
        """Get current leaderboard."""
        with _orchestrator_lock:
            if not _orchestrator:
                return jsonify({"agents": []})

            try:
                agents_data = []
                for agent in _orchestrator.agents:
                    agent_status = agent.get_status()
                    portfolio_value = (
                        agent.risk_engine.current_portfolio
                        if hasattr(agent, "risk_engine")
                        else INITIAL_PORTFOLIO
                    )
                    pnl = portfolio_value - INITIAL_PORTFOLIO
                    agents_data.append(
                        {
                            **agent_status,
                            "portfolio_value": portfolio_value,
                            "pnl": pnl,
                            "pnl_percent": (pnl / INITIAL_PORTFOLIO) * 100
                            if INITIAL_PORTFOLIO > 0
                            else 0,
                        }
                    )

                # Sort by portfolio value
                agents_data.sort(key=lambda x: x["portfolio_value"], reverse=True)
                return jsonify({"agents": agents_data})
            except Exception as e:
                logger.error(f"Failed to get leaderboard: {e}")
                return jsonify({"error": str(e)}), 500

    # -------------------------------------------------------------------------
    # Agent Control
    # -------------------------------------------------------------------------
    @app.route("/api/agents/<agent_id>/stop", methods=["POST"])
    def stop_agent(agent_id: str):
        """Stop a specific agent."""
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        with _orchestrator_lock:
            if not _orchestrator:
                return jsonify({"error": "Race not running"}), 400

            try:
                for agent in _orchestrator.agents:
                    if (
                        agent.name == agent_id
                        or str(agent.name).replace("Agent-", "") == agent_id
                    ):
                        # Remove agent from active trading
                        if agent in _orchestrator.agents:
                            _orchestrator.agents.remove(agent)
                        logger.info(f"Agent {agent_id} stopped via API")
                        return jsonify({"status": "stopped", "agent": agent_id})
                return jsonify({"error": "Agent not found"}), 404
            except Exception as e:
                logger.error(f"Failed to stop agent {agent_id}: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route("/api/agents/<agent_id>/restart", methods=["POST"])
    def restart_agent(agent_id: str):
        """Restart a specific agent."""
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        with _orchestrator_lock:
            if not _orchestrator or not _orchestrator.is_running:
                return jsonify({"error": "Race not running"}), 400

            try:
                # Find agent index
                agent_index = None
                for i, agent in enumerate(_orchestrator.agents):
                    if (
                        agent.name == agent_id
                        or str(agent.name).replace("Agent-", "") == agent_id
                    ):
                        agent_index = i
                        break

                if agent_index is None:
                    return jsonify({"error": "Agent not found"}), 404

                # Reinitialize agent with fresh risk engine
                risk_engine = RiskEngine(INITIAL_PORTFOLIO)
                order_executor = OrderExecutor(exchange=_orchestrator.exchange)
                new_agent = LLMTradingAgent(
                    name=_orchestrator.agents[agent_index].name,
                    pairs=SUPPORTED_PAIRS,
                    risk_engine=risk_engine,
                    order_executor=order_executor,
                    market_data=_orchestrator.market_data,
                )
                _orchestrator.agents[agent_index] = new_agent
                logger.info(f"Agent {agent_id} restarted via API")
                return jsonify({"status": "restarted", "agent": agent_id})
            except Exception as e:
                logger.error(f"Failed to restart agent {agent_id}: {e}")
                return jsonify({"error": str(e)}), 500

    # -------------------------------------------------------------------------
    # Configuration Management
    # -------------------------------------------------------------------------
    @app.route("/api/config", methods=["GET"])
    def get_config():
        """Get current configuration."""
        config = _load_config()
        # Remove sensitive keys
        sensitive_keys = [
            "COINDCX_API_KEY",
            "COINDCX_API_SECRET",
            "TELEGRAM_BOT_TOKEN",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "XAI_API_KEY",
            "MSTOCK_USER_ID",
            "MSTOCK_PASSWORD",
            "MSTOCK_PIN",
            "MSTOCK_API_KEY",
            "MSTOCK_API_SECRET",
        ]
        display_config = {k: v for k, v in config.items() if k not in sensitive_keys}
        return jsonify(display_config)

    @app.route("/api/config", methods=["POST"])
    def update_config():
        """Update configuration."""
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        new_config = request.get_json()
        if not new_config:
            return jsonify({"error": "No data provided"}), 400

        # Validate numeric fields
        numeric_fields = {
            "INITIAL_PORTFOLIO": float,
            "RISK_PER_TRADE": float,
            "MAX_PORTFOLIO_EXPOSURE": float,
            "STOP_LOSS_PERCENT": float,
            "DAILY_MAX_LOSS_PERCENT": float,
            "RACE_DURATION_HOURS": int,
            "NUM_RACE_AGENTS": int,
            "RACE_UPDATE_INTERVAL_SEC": int,
            "EVOLUTION_INTERVAL_MIN": int,
            "LOG_LEVEL": str,
            "PAPER_TRADING_MODE": str,
        }

        current_config = _load_config()
        for key, value in new_config.items():
            if key in numeric_fields:
                try:
                    numeric_fields[key](value)
                except ValueError:
                    return jsonify({"error": f"Invalid value for {key}"}), 400

        # Merge and save
        current_config.update(new_config)
        _save_config(current_config)
        logger.info("Configuration updated via API")
        return jsonify({"status": "updated"})

    # -------------------------------------------------------------------------
    # API Key Management
    # -------------------------------------------------------------------------
    @app.route("/api/apikeys", methods=["GET"])
    def get_api_keys():
        """Get list of stored API keys (names only, not values)."""
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        keys = _load_api_keys()
        return jsonify({"keys": list(keys.keys())})

    @app.route("/api/apikeys/<key_name>", methods=["GET", "POST", "DELETE"])
    def manage_api_key(key_name: str):
        """Get, set, or delete an API key."""
        if not _allow_api_control:
            return jsonify({"error": "API control disabled"}), 403

        keys = _load_api_keys()

        if request.method == "GET":
            if key_name not in keys:
                return jsonify({"error": "Key not found"}), 404
            return jsonify({"name": key_name, "value": keys[key_name]})

        elif request.method == "POST":
            data = request.get_json()
            if not data or "value" not in data:
                return jsonify({"error": "Value required"}), 400
            keys[key_name] = data["value"]
            _save_api_keys(keys)
            # Also set as environment variable
            os.environ[key_name] = data["value"]
            logger.info(f"API key {key_name} updated")
            return jsonify({"status": "saved"})

        elif request.method == "DELETE":
            if key_name in keys:
                del keys[key_name]
                _save_api_keys(keys)
                if key_name in os.environ:
                    del os.environ[key_name]
                logger.info(f"API key {key_name} deleted")
                return jsonify({"status": "deleted"})
            return jsonify({"error": "Key not found"}), 404

    # -------------------------------------------------------------------------
    # Logs
    # -------------------------------------------------------------------------
    @app.route("/api/logs", methods=["GET"])
    def get_logs():
        """Get recent log entries."""
        log_file = project_root / "logs" / "trading_system.log"
        if not log_file.exists():
            return jsonify({"logs": []})

        lines = []
        try:
            with open(log_file, "r") as f:
                lines = f.readlines()[-100:]  # Last 100 lines
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")

        return jsonify({"logs": lines})

    # -------------------------------------------------------------------------
    # Trades & Analytics
    # -------------------------------------------------------------------------
    @app.route("/api/trades", methods=["GET"])
    def get_trades():
        """Get recent trades."""
        try:
            db = TradeDatabase()
            limit = int(request.args.get("limit", 100))
            trades = db.get_trades(limit=limit)
            db.close()
            return jsonify({"trades": trades})
        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/analytics/performance", methods=["GET"])
    def get_performance():
        """Get performance metrics."""
        try:
            db = TradeDatabase()
            stats = db.get_statistics()
            db.close()
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Failed to get performance: {e}")
            return jsonify({"error": str(e)}), 500

    return app


# Standalone runner
if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
    )

    # Check if API control is explicitly enabled
    if not _allow_api_control:
        logger.warning(
            "ALLOW_API_CONTROL is not set to 'true'. API endpoints will be disabled."
        )
        logger.warning("Set ALLOW_API_CONTROL=true in .env to enable remote control.")

    app = create_app()
    port = int(os.getenv("API_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
