"""Main orchestrator for IndiaCryptoAlpha trading system."""

import logging
import sys
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from config import (
    LOG_LEVEL, SUPPORTED_PAIRS, RESEARCHER_INTERVAL_HOURS, MONITOR_INTERVAL_HOURS,
    INITIAL_PORTFOLIO, PAPER_TRADING_MODE
)
from core import MarketDataManager, RiskEngine, OrderExecutor
from agents import RSIMACDAgent, BollingerVolumeAgent, EMASupertrendAgent
from logger import AccountantAgent
from monitor import MonitorAgent
from researcher import ResearcherAgent

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_system.log'),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class TradingOrchestrator:
    """Orchestrates all trading agents and system components."""

    def __init__(self):
        """Initialize the trading orchestrator."""
        logger.info("=" * 80)
        logger.info("🚀 IndiaCryptoAlpha Trading System Starting")
        logger.info("=" * 80)
        logger.info(f"Mode: {'PAPER TRADING' if PAPER_TRADING_MODE else 'LIVE TRADING'}")
        logger.info(f"Initial Portfolio: ₹{INITIAL_PORTFOLIO:,.2f}")

        # Initialize core components
        self.market_data = MarketDataManager()
        self.risk_engine = RiskEngine(INITIAL_PORTFOLIO)
        self.order_executor = OrderExecutor()

        # Initialize agents
        self.strategy_agents = [
            RSIMACDAgent(SUPPORTED_PAIRS, self.risk_engine, self.order_executor, self.market_data),
            BollingerVolumeAgent(SUPPORTED_PAIRS, self.risk_engine, self.order_executor, self.market_data),
            EMASupertrendAgent(SUPPORTED_PAIRS, self.risk_engine, self.order_executor, self.market_data),
        ]

        self.accountant = AccountantAgent()
        self.monitor = MonitorAgent()
        self.researcher = ResearcherAgent(self.market_data)

        # Initialize scheduler
        self.scheduler = BackgroundScheduler()
        self._setup_scheduler()

        logger.info("✓ Trading Orchestrator initialized successfully")

    def _setup_scheduler(self):
        """Set up scheduled tasks."""
        # Strategy analysis every hour
        self.scheduler.add_job(
            self.analyze_strategies,
            'interval',
            hours=1,
            id='strategy_analysis'
        )

        # Researcher analysis every 6 hours
        self.scheduler.add_job(
            self.run_researcher,
            'interval',
            hours=RESEARCHER_INTERVAL_HOURS,
            id='researcher_analysis'
        )

        # Monitor check every 2-3 hours
        self.scheduler.add_job(
            self.monitor_system,
            'interval',
            hours=MONITOR_INTERVAL_HOURS,
            id='system_monitor'
        )

        # Daily summary at 8 PM
        self.scheduler.add_job(
            self.send_daily_summary,
            'cron',
            hour=20,
            minute=0,
            id='daily_summary'
        )

        logger.info("✓ Scheduler configured")

    def start(self):
        """Start the trading system."""
        try:
            self.scheduler.start()
            logger.info("✓ Trading system started")
            logger.info("Press Ctrl+C to stop the system")

            # Keep the system running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("⏹ Shutting down trading system...")
                self.stop()

        except Exception as e:
            logger.error(f"✗ Failed to start trading system: {e}")
            self.stop()
            raise

    def stop(self):
        """Stop the trading system."""
        try:
            self.scheduler.shutdown()
            self.accountant.close()
            logger.info("✓ Trading system stopped")
        except Exception as e:
            logger.error(f"✗ Error stopping system: {e}")

    def analyze_strategies(self):
        """Run strategy analysis on all agents."""
        try:
            logger.info("=" * 80)
            logger.info("📊 Strategy Analysis Cycle")
            logger.info("=" * 80)

            for agent in self.strategy_agents:
                logger.info(f"\n🤖 Analyzing {agent.name}...")

                for pair in SUPPORTED_PAIRS[:3]:  # Analyze top 3 pairs
                    signal = agent.analyze(pair)

                    if signal:
                        # Execute trade
                        success = agent.execute_trade(pair, signal)

                        if success:
                            # Log trade
                            trade_data = {
                                'strategy_name': agent.name,
                                'pair': pair,
                                'side': signal['side'],
                                'entry_price': signal.get('price', 0),
                                'quantity': signal.get('quantity', 1),
                                'entry_time': datetime.now().isoformat(),
                                'notes': signal.get('reason', ''),
                            }

                            # Send alert
                            self.monitor.send_trade_alert(trade_data)

            logger.info("✓ Strategy analysis cycle completed")

        except Exception as e:
            logger.error(f"✗ Strategy analysis failed: {e}")
            self.monitor.check_system_error('StrategyAnalysis', str(e))

    def run_researcher(self):
        """Run researcher analysis."""
        try:
            logger.info("=" * 80)
            logger.info("🔬 Researcher Analysis")
            logger.info("=" * 80)

            report = self.researcher.generate_market_report()

            if report:
                logger.info(f"Market Analysis Report:\n{report}")

                # Send to monitor
                for pair, analysis in report.get('market_analysis', {}).items():
                    logger.info(f"  {pair}: {analysis.get('regime', 'N/A')}")

            logger.info("✓ Researcher analysis completed")

        except Exception as e:
            logger.error(f"✗ Researcher analysis failed: {e}")
            self.monitor.check_system_error('ResearcherAgent', str(e))

    def monitor_system(self):
        """Monitor system health and performance."""
        try:
            logger.info("=" * 80)
            logger.info("🔍 System Monitoring")
            logger.info("=" * 80)

            # Get portfolio metrics
            current_prices = {pair: self.market_data.get_ticker(pair)['last']
                            for pair in SUPPORTED_PAIRS[:3]}
            portfolio_value = self.risk_engine.get_portfolio_value(current_prices)
            metrics = self.risk_engine.get_risk_metrics(portfolio_value)

            logger.info(f"Portfolio Value: ₹{portfolio_value:,.2f}")
            logger.info(f"Daily P&L: ₹{metrics['daily_pnl']:,.2f}")
            logger.info(f"Drawdown: {metrics['drawdown']:.2f}%")

            # Check for alerts
            self.monitor.check_drawdown(portfolio_value, self.risk_engine.initial_portfolio)

            # Log portfolio snapshot
            self.accountant.log_portfolio_snapshot({
                'portfolio_value': portfolio_value,
                'cash': self.risk_engine.current_portfolio,
                'positions_count': len(self.risk_engine.positions),
                'daily_pnl': metrics['daily_pnl'],
                'cumulative_pnl': metrics['cumulative_pnl'],
                'drawdown': metrics['drawdown'],
            })

            logger.info("✓ System monitoring completed")

        except Exception as e:
            logger.error(f"✗ System monitoring failed: {e}")
            self.monitor.check_system_error('SystemMonitor', str(e))

    def send_daily_summary(self):
        """Send daily trading summary."""
        try:
            logger.info("=" * 80)
            logger.info("📈 Daily Summary")
            logger.info("=" * 80)

            stats = self.accountant.get_statistics()
            summary = {
                'total_trades': stats.get('total_trades', 0),
                'winning_trades': stats.get('winning_trades', 0),
                'losing_trades': stats.get('losing_trades', 0),
                'win_rate': stats.get('win_rate', 0),
                'daily_pnl': self.risk_engine.daily_pnl,
                'cumulative_pnl': self.accountant.cumulative_pnl,
                'avg_win': stats.get('avg_win', 0),
                'avg_loss': stats.get('avg_loss', 0),
                'portfolio_value': self.risk_engine.current_portfolio,
            }

            logger.info(f"Daily Summary: {summary}")
            self.monitor.send_daily_summary(summary)

            # Log agent performance
            for agent in self.strategy_agents:
                perf = agent.get_performance()
                self.accountant.log_agent_performance({
                    'agent_name': agent.name,
                    **perf,
                })

            logger.info("✓ Daily summary sent")

        except Exception as e:
            logger.error(f"✗ Failed to send daily summary: {e}")

    def get_status(self) -> dict:
        """Get system status."""
        return {
            'status': 'running' if self.scheduler.running else 'stopped',
            'portfolio_value': self.risk_engine.current_portfolio,
            'daily_pnl': self.risk_engine.daily_pnl,
            'cumulative_pnl': self.accountant.cumulative_pnl,
            'agents': len(self.strategy_agents),
            'trades': len(self.order_executor.filled_orders),
            'timestamp': datetime.now().isoformat(),
        }


def main():
    """Main entry point."""
    try:
        orchestrator = TradingOrchestrator()
        orchestrator.start()
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
