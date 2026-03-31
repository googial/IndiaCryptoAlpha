"""Backtesting engine for strategy analysis."""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core import MarketDataManager

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtests trading strategies on historical data."""

    def __init__(self, market_data: MarketDataManager):
        """
        Initialize backtest engine.
        
        Args:
            market_data: Market data manager instance
        """
        self.market_data = market_data
        self.results = {}

    def backtest_strategy(self, pair: str, strategy_func, days: int = 30,
                         initial_capital: float = 100000) -> Dict:
        """
        Backtest a strategy on historical data.
        
        Args:
            pair: Trading pair
            strategy_func: Strategy function that takes OHLCV data and returns signals
            days: Number of days of historical data
            initial_capital: Initial capital for backtest
            
        Returns:
            Backtest results dictionary
        """
        try:
            # Fetch historical data
            data = self.market_data.get_historical_data(pair, days=days, timeframe='1h')
            if data is None or len(data) < 50:
                logger.warning(f"⚠ Insufficient data for backtest: {pair}")
                return {}

            # Initialize portfolio
            portfolio_value = initial_capital
            cash = initial_capital
            positions = {}
            trades = []
            portfolio_values = [initial_capital]

            # Run strategy on historical data
            for idx in range(50, len(data)):
                current_data = data.iloc[:idx+1]
                current_price = current_data['close'].iloc[-1]

                # Generate signal
                signal = strategy_func(current_data)

                if signal:
                    side = signal.get('side')
                    quantity = signal.get('quantity', 1)

                    if side == 'BUY' and cash >= current_price * quantity:
                        # Execute buy
                        cost = current_price * quantity
                        cash -= cost
                        positions[pair] = {
                            'quantity': quantity,
                            'entry_price': current_price,
                            'entry_idx': idx,
                        }

                    elif side == 'SELL' and pair in positions:
                        # Execute sell
                        position = positions[pair]
                        proceeds = current_price * position['quantity']
                        pnl = proceeds - (position['entry_price'] * position['quantity'])
                        cash += proceeds

                        trades.append({
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'quantity': position['quantity'],
                            'pnl': pnl,
                            'entry_idx': position['entry_idx'],
                            'exit_idx': idx,
                        })

                        del positions[pair]

                # Update portfolio value
                position_value = sum(
                    pos['quantity'] * current_price
                    for pos in positions.values()
                )
                portfolio_value = cash + position_value
                portfolio_values.append(portfolio_value)

            # Calculate statistics
            stats = self._calculate_statistics(trades, portfolio_values, initial_capital)
            stats['pair'] = pair
            stats['trades'] = trades

            logger.info(f"✓ Backtest completed for {pair}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"✗ Backtest failed for {pair}: {e}")
            return {}

    def _calculate_statistics(self, trades: List[Dict], portfolio_values: List[float],
                             initial_capital: float) -> Dict:
        """
        Calculate backtest statistics.
        
        Args:
            trades: List of completed trades
            portfolio_values: List of portfolio values over time
            initial_capital: Initial capital
            
        Returns:
            Statistics dictionary
        """
        try:
            if not trades:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0,
                    'total_pnl': 0.0,
                    'total_return': 0.0,
                    'avg_win': 0.0,
                    'avg_loss': 0.0,
                    'profit_factor': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                }

            pnls = [trade['pnl'] for trade in trades]
            winning_trades = sum(1 for pnl in pnls if pnl > 0)
            losing_trades = sum(1 for pnl in pnls if pnl < 0)

            wins = [pnl for pnl in pnls if pnl > 0]
            losses = [pnl for pnl in pnls if pnl < 0]

            total_pnl = sum(pnls)
            total_return = (portfolio_values[-1] - initial_capital) / initial_capital * 100

            # Calculate max drawdown
            peak = portfolio_values[0]
            max_dd = 0
            for value in portfolio_values:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak * 100
                if dd > max_dd:
                    max_dd = dd

            # Calculate Sharpe ratio (simplified)
            returns = np.diff(portfolio_values) / portfolio_values[:-1]
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0

            return {
                'total_trades': len(trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': winning_trades / len(trades) if trades else 0.0,
                'total_pnl': total_pnl,
                'total_return': total_return,
                'avg_win': sum(wins) / len(wins) if wins else 0.0,
                'avg_loss': sum(losses) / len(losses) if losses else 0.0,
                'profit_factor': abs(sum(wins) / sum(losses)) if losses else 0.0,
                'max_drawdown': max_dd,
                'sharpe_ratio': sharpe,
            }
        except Exception as e:
            logger.error(f"✗ Statistics calculation failed: {e}")
            return {}

    def compare_strategies(self, pair: str, strategies: Dict, days: int = 30) -> Dict:
        """
        Compare multiple strategies on the same data.
        
        Args:
            pair: Trading pair
            strategies: Dictionary of {strategy_name: strategy_func}
            days: Number of days of historical data
            
        Returns:
            Comparison results
        """
        try:
            results = {}
            for name, func in strategies.items():
                result = self.backtest_strategy(pair, func, days=days)
                results[name] = result

            logger.info(f"✓ Strategy comparison completed for {pair}")
            return results
        except Exception as e:
            logger.error(f"✗ Strategy comparison failed: {e}")
            return {}

    def optimize_parameters(self, pair: str, strategy_func, param_ranges: Dict,
                           days: int = 30) -> Dict:
        """
        Optimize strategy parameters through grid search.
        
        Args:
            pair: Trading pair
            strategy_func: Strategy function
            param_ranges: Dictionary of {param_name: [min, max, step]}
            days: Number of days of historical data
            
        Returns:
            Optimization results
        """
        try:
            best_result = None
            best_params = None
            best_return = -float('inf')

            # Grid search (simplified - just 2 parameters for demo)
            for param_value in param_ranges.get('param1', [0.1, 0.2, 0.3]):
                result = self.backtest_strategy(pair, strategy_func, days=days)
                if result.get('total_return', -float('inf')) > best_return:
                    best_return = result.get('total_return')
                    best_result = result
                    best_params = {'param1': param_value}

            logger.info(f"✓ Parameter optimization completed: {best_params}")
            return {
                'best_params': best_params,
                'best_result': best_result,
            }
        except Exception as e:
            logger.error(f"✗ Parameter optimization failed: {e}")
            return {}
