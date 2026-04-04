"""Race Orchestrator for IndiaAI Race Alpha."""

import logging
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from config import (
    NUM_RACE_AGENTS,
    RACE_DURATION_HOURS,
    RACE_UPDATE_INTERVAL_SEC,
    EVOLUTION_INTERVAL_MIN,
    INITIAL_PORTFOLIO,
    SUPPORTED_PAIRS,
)
from core import MarketDataManager, RiskEngine, OrderExecutor
from core.exchange_base import ExchangeFactory
from agents.llm_agent import LLMTradingAgent
from logger import AccountantAgent
from monitor import MonitorAgent

logger = logging.getLogger(__name__)


class RaceOrchestrator:
    """Manages the AI race between multiple trading agents."""

    def __init__(self, num_agents: int = NUM_RACE_AGENTS):
        """Initialize the race orchestrator."""
        logger.info("=" * 80)
        logger.info(f"🏁 IndiaAI Race Alpha Orchestrator Starting")
        logger.info(f"Agents: {num_agents} | Duration: {RACE_DURATION_HOURS}h")
        logger.info("=" * 80)

        self.num_agents = num_agents
        self.market_data = MarketDataManager()

        # Create exchange instance if credentials available (for live trading)
        self.exchange = None
        try:
            from config import (
                EXCHANGE_NAME,
                BINANCE_API_KEY,
                BINANCE_SECRET_KEY,
                COINDCX_API_KEY,
                COINDCX_API_SECRET,
            )

            exchange_name = EXCHANGE_NAME.lower()
            if exchange_name == "binance" and BINANCE_API_KEY and BINANCE_SECRET_KEY:
                self.exchange = ExchangeFactory.create_exchange(
                    "binance", BINANCE_API_KEY, BINANCE_SECRET_KEY
                )
                logger.info(f"✅ Live Binance exchange initialized")
            elif exchange_name == "coindcx" and COINDCX_API_KEY and COINDCX_API_SECRET:
                self.exchange = ExchangeFactory.create_exchange(
                    "coindcx", COINDCX_API_KEY, COINDCX_API_SECRET
                )
                logger.info(f"✅ Live CoinDCX exchange initialized")
            else:
                logger.info(
                    "ℹ️ No exchange credentials configured — agents will run in paper trading mode only"
                )
        except Exception as e:
            logger.warning(f"Failed to initialize exchange: {e} — paper mode only")

        self.accountant = AccountantAgent()
        self.monitor = MonitorAgent()

        # Initialize agents with their own risk engines (isolated portfolios)
        self.agents: List[LLMTradingAgent] = []
        self._agent_states: Dict[str, bool] = {}  # Running state per agent
        self._init_agents()

        self.start_time = None
        self.end_time = None
        self.is_running = False

        self.scheduler = BackgroundScheduler()
        self._setup_scheduler()

    def _init_agents(self):
        """Initialize N autonomous agents."""
        for i in range(self.num_agents):
            agent_name = f"Agent-{i + 1:02d}"
            # Each agent gets its own risk engine for isolated virtual capital
            risk_engine = RiskEngine(INITIAL_PORTFOLIO)
            order_executor = OrderExecutor(exchange=self.exchange)

            agent = LLMTradingAgent(
                name=agent_name,
                pairs=SUPPORTED_PAIRS,
                risk_engine=risk_engine,
                order_executor=order_executor,
                market_data=self.market_data,
            )
            self.agents.append(agent)
            self._agent_states[agent_name] = True  # All agents start active
            logger.info(f"✓ {agent_name} joined the race")

    # -------------------------------------------------------------------------
    # AGENT CONTROL
    # -------------------------------------------------------------------------

    def get_agent(self, agent_id: str) -> Optional[LLMTradingAgent]:
        """Get agent by name or numeric ID."""
        for agent in self.agents:
            if (
                agent.name == agent_id
                or str(agent.name).replace("Agent-", "") == agent_id
            ):
                return agent
        return None

    def stop_agent(self, agent_id: str) -> bool:
        """
        Stop a specific agent from trading.
        Returns True if agent was found and stopped, False otherwise.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found")
            return False

        self._agent_states[agent.name] = False
        logger.info(f"Agent {agent.name} stopped")
        return True

    def start_agent(self, agent_id: str) -> bool:
        """
        Start/resume a specific agent.
        Returns True if agent was found and started, False otherwise.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found")
            return False

        self._agent_states[agent.name] = True
        logger.info(f"Agent {agent.name} started")
        return True

    def restart_agent(self, agent_id: str) -> bool:
        """
        Restart an agent with fresh state.
        Returns True if agent was found and restarted, False otherwise.
        """
        agent_idx = None
        for i, agent in enumerate(self.agents):
            if (
                agent.name == agent_id
                or str(agent.name).replace("Agent-", "") == agent_id
            ):
                agent_idx = i
                break

        if agent_idx is None:
            logger.warning(f"Agent {agent_id} not found")
            return False

        # Reinitialize with fresh risk engine and state
        new_agent = LLMTradingAgent(
            name=self.agents[agent_idx].name,
            pairs=SUPPORTED_PAIRS,
            risk_engine=RiskEngine(INITIAL_PORTFOLIO),
            order_executor=OrderExecutor(exchange=self.exchange),
            market_data=self.market_data,
        )
        self.agents[agent_idx] = new_agent
        self._agent_states[new_agent.name] = True
        logger.info(f"Agent {agent_id} restarted with fresh state")
        return True

    def get_active_agents(self) -> List[LLMTradingAgent]:
        """Get list of currently active agents."""
        return [
            agent for agent in self.agents if self._agent_states.get(agent.name, False)
        ]

    def _setup_scheduler(self):
        """Set up race-specific scheduled tasks."""
        # Main race loop: analyze and trade
        self.scheduler.add_job(
            self.run_race_cycle,
            "interval",
            seconds=RACE_UPDATE_INTERVAL_SEC,
            id="race_cycle",
        )

        # Evolution cycle: agents review and update strategies
        self.scheduler.add_job(
            self.run_evolution_cycle,
            "interval",
            minutes=EVOLUTION_INTERVAL_MIN,
            id="evolution_cycle",
        )

        # Snapshot cycle: record equity for dashboard
        self.scheduler.add_job(
            self.take_race_snapshot,
            "interval",
            seconds=RACE_UPDATE_INTERVAL_SEC,
            id="race_snapshot",
        )

    def start_race(self):
        """Start the race."""
        if self.is_running:
            logger.warning("⚠ Race is already running")
            return

        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=RACE_DURATION_HOURS)
        self.is_running = True

        self.scheduler.start()
        logger.info(f"🚀 Race started at {self.start_time}")
        logger.info(f"🏁 Race scheduled to end at {self.end_time}")

    def stop_race(self):
        """Stop the race."""
        if not self.is_running:
            return

        self.is_running = False
        self.scheduler.shutdown()
        logger.info("⏹ Race stopped")

        # Final leaderboard
        self.print_leaderboard()

    def run_race_cycle(self):
        """Execute one trading cycle for active agents only."""
        if not self.is_running:
            return

        # Check if race duration exceeded
        if datetime.now() >= self.end_time:
            logger.info("🏁 Race duration reached. Ending race...")
            self.stop_race()
            return

        for agent in self.agents:
            if not self._agent_states.get(agent.name, False):
                continue  # Skip inactive agents
            try:
                # Analyze top 2 pairs for speed in race mode
                for pair in SUPPORTED_PAIRS[:2]:
                    signal = agent.analyze(pair)
                    if signal:
                        agent.execute_trade(pair, signal)
            except Exception as e:
                logger.error(f"✗ {agent.name} race cycle error: {e}")
            except Exception as e:
                logger.error(f"✗ {agent.name} race cycle error: {e}")

    def run_evolution_cycle(self):
        """Allow agents to evolve their strategies."""
        if not self.is_running:
            return

        logger.info("🧬 Evolution cycle starting for all agents...")
        for agent in self.agents:
            agent.evolve()

    def take_race_snapshot(self):
        """Record current state of all agents for the dashboard."""
        if not self.is_running:
            return

        snapshot_data = []
        for agent in self.agents:
            # Get current portfolio value
            current_prices = {
                pair: self.market_data.get_ticker(pair)["last"]
                for pair in SUPPORTED_PAIRS[:2]
            }
            portfolio_value = agent.risk_engine.get_portfolio_value(current_prices)

            agent_status = agent.get_status()
            agent_status["portfolio_value"] = portfolio_value
            snapshot_data.append(agent_status)

            # Log to database/excel via accountant
            self.accountant.log_agent_performance(
                {
                    "agent_name": agent.name,
                    "portfolio_value": portfolio_value,
                    "total_pnl": agent_status["total_pnl"],
                    "win_rate": agent_status["win_rate"],
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Optionally send to monitor for major changes
        # self.monitor.update_race_status(snapshot_data)

    def print_leaderboard(self):
        """Print current race leaderboard to logs."""
        logger.info("\n" + "=" * 40)
        logger.info("🏆 RACE LEADERBOARD 🏆")
        logger.info("=" * 40)

        # Sort agents by portfolio value (mocking current prices for simplicity)
        sorted_agents = sorted(
            self.agents, key=lambda a: a.risk_engine.current_portfolio, reverse=True
        )

        for i, agent in enumerate(sorted_agents):
            pnl = agent.risk_engine.current_portfolio - INITIAL_PORTFOLIO
            pnl_pct = (pnl / INITIAL_PORTFOLIO) * 100
            logger.info(
                f"{i + 1}. {agent.name:10} | P&L: ₹{pnl:10,.2f} ({pnl_pct:6.2f}%) | Trades: {agent.performance['total_trades']}"
            )

        logger.info("=" * 40 + "\n")

    def get_race_status(self) -> Dict:
        """Get overall race status for the dashboard."""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "time_remaining": str(self.end_time - datetime.now())
            if self.end_time
            else None,
            "num_agents": len(self.agents),
            "active_agents": len(self.get_active_agents()),
            "agents": [agent.get_status() for agent in self.agents],
            "agent_states": self._agent_states,
        }
