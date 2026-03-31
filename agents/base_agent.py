"""Base strategy agent class for all trading strategies."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd
from core import MarketDataManager, RiskEngine, OrderExecutor

logger = logging.getLogger(__name__)


class BaseStrategyAgent(ABC):
    """Abstract base class for all strategy agents."""

    def __init__(self, name: str, pairs: List[str], risk_engine: RiskEngine,
                 order_executor: OrderExecutor, market_data: MarketDataManager):
        """
        Initialize base strategy agent.
        
        Args:
            name: Agent name
            pairs: List of trading pairs to monitor
            risk_engine: Risk engine instance
            order_executor: Order executor instance
            market_data: Market data manager instance
        """
        self.name = name
        self.pairs = pairs
        self.risk_engine = risk_engine
        self.order_executor = order_executor
        self.market_data = market_data
        
        self.trades = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
        }
        self.last_signals = {}
        
        logger.info(f"✓ {self.name} initialized with pairs: {pairs}")

    @abstractmethod
    def generate_signal(self, pair: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on strategy logic.
        
        Args:
            pair: Trading pair
            data: OHLCV data
            
        Returns:
            Signal dictionary with 'side', 'confidence', etc. or None
        """
        pass

    def analyze(self, pair: str) -> Optional[Dict]:
        """
        Analyze a trading pair and generate signal.
        
        Args:
            pair: Trading pair to analyze
            
        Returns:
            Trading signal or None
        """
        try:
            # Fetch market data
            data = self.market_data.get_ohlcv(pair, timeframe='1h', limit=100)
            if data is None or len(data) < 50:
                logger.warning(f"⚠ Insufficient data for {pair}")
                return None

            # Generate signal
            signal = self.generate_signal(pair, data)
            
            if signal:
                self.last_signals[pair] = signal
                logger.info(f"✓ {self.name} signal for {pair}: {signal}")
            
            return signal
        except Exception as e:
            logger.error(f"✗ {self.name} analysis failed for {pair}: {e}")
            return None

    def execute_trade(self, pair: str, signal: Dict) -> bool:
        """
        Execute a trade based on signal.
        
        Args:
            pair: Trading pair
            signal: Trading signal
            
        Returns:
            True if trade executed, False otherwise
        """
        try:
            ticker = self.market_data.get_ticker(pair)
            if not ticker:
                logger.error(f"✗ Failed to get ticker for {pair}")
                return False

            current_price = ticker['last']
            side = signal.get('side')
            quantity = signal.get('quantity', 1)

            # Validate trade with risk engine
            is_valid, reason = self.risk_engine.validate_trade(
                pair, side, quantity, current_price, current_price
            )

            if not is_valid:
                logger.warning(f"⚠ Trade rejected for {pair}: {reason}")
                return False

            # Execute order
            execution = self.order_executor.simulate_market_execution(
                pair, side, quantity, current_price
            )

            if execution:
                # Update portfolio
                self.risk_engine.update_portfolio(pair, side, quantity, current_price)
                self.trades.append(execution)
                self.performance['total_trades'] += 1
                logger.info(f"✓ {self.name} executed trade: {execution}")
                return True
            else:
                logger.error(f"✗ {self.name} failed to execute trade for {pair}")
                return False

        except Exception as e:
            logger.error(f"✗ {self.name} trade execution failed: {e}")
            return False

    def get_performance(self) -> Dict:
        """
        Get agent performance metrics.
        
        Returns:
            Performance dictionary
        """
        if self.performance['total_trades'] == 0:
            return self.performance

        win_rate = (self.performance['winning_trades'] / 
                   self.performance['total_trades']) if self.performance['total_trades'] > 0 else 0

        return {
            **self.performance,
            'win_rate': win_rate,
            'avg_pnl': self.performance['total_pnl'] / self.performance['total_trades'],
        }

    def reset(self):
        """Reset agent state."""
        self.trades = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
        }
        self.last_signals = {}
        logger.info(f"✓ {self.name} reset")
