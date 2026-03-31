"""Researcher Agent for backtesting and market analysis."""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from .backtest_engine import BacktestEngine
from core import MarketDataManager
from config import SUPPORTED_PAIRS, BACKTEST_DAYS

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """Analyzes market conditions and backtests strategies."""

    def __init__(self, market_data: MarketDataManager):
        """
        Initialize researcher agent.
        
        Args:
            market_data: Market data manager instance
        """
        self.market_data = market_data
        self.backtest_engine = BacktestEngine(market_data)
        self.reports = []
        logger.info("✓ Researcher Agent initialized")

    def analyze_market_regime(self, pair: str = 'BTC-INR') -> Dict:
        """
        Analyze current market regime.
        
        Args:
            pair: Trading pair to analyze
            
        Returns:
            Market analysis dictionary
        """
        try:
            regime = self.market_data.get_market_regime(pair, timeframe='1d', days=30)
            
            # Get additional metrics
            data = self.market_data.get_historical_data(pair, days=30, timeframe='1d')
            if data is not None and len(data) > 0:
                current_price = data['close'].iloc[-1]
                sma_20 = data['close'].rolling(window=20).mean().iloc[-1]
                sma_50 = data['close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else sma_20
                
                volatility = data['close'].pct_change().std() * 100
                
                analysis = {
                    'pair': pair,
                    'regime': regime,
                    'current_price': current_price,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'volatility': volatility,
                    'timestamp': datetime.now().isoformat(),
                }
                
                logger.info(f"✓ Market analysis for {pair}: {analysis}")
                return analysis
            
            return {}
        except Exception as e:
            logger.error(f"✗ Market analysis failed: {e}")
            return {}

    def backtest_strategy(self, pair: str, strategy_func, days: int = BACKTEST_DAYS) -> Dict:
        """
        Backtest a strategy.
        
        Args:
            pair: Trading pair
            strategy_func: Strategy function
            days: Number of days for backtest
            
        Returns:
            Backtest results
        """
        try:
            return self.backtest_engine.backtest_strategy(pair, strategy_func, days=days)
        except Exception as e:
            logger.error(f"✗ Strategy backtest failed: {e}")
            return {}

    def compare_strategies(self, pair: str, strategies: Dict, days: int = BACKTEST_DAYS) -> Dict:
        """
        Compare multiple strategies.
        
        Args:
            pair: Trading pair
            strategies: Dictionary of {strategy_name: strategy_func}
            days: Number of days for backtest
            
        Returns:
            Comparison results
        """
        try:
            results = self.backtest_engine.compare_strategies(pair, strategies, days=days)
            
            # Rank strategies by return
            ranked = sorted(
                results.items(),
                key=lambda x: x[1].get('total_return', -float('inf')),
                reverse=True
            )
            
            report = {
                'pair': pair,
                'timestamp': datetime.now().isoformat(),
                'strategies': results,
                'ranking': [name for name, _ in ranked],
                'best_strategy': ranked[0][0] if ranked else None,
            }
            
            self.reports.append(report)
            logger.info(f"✓ Strategy comparison completed: {report}")
            return report
        except Exception as e:
            logger.error(f"✗ Strategy comparison failed: {e}")
            return {}

    def generate_market_report(self) -> Dict:
        """
        Generate comprehensive market report.
        
        Returns:
            Market report dictionary
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'market_analysis': {},
                'recommendations': [],
            }

            # Analyze all supported pairs
            for pair in SUPPORTED_PAIRS[:3]:  # Analyze top 3 pairs
                analysis = self.analyze_market_regime(pair)
                if analysis:
                    report['market_analysis'][pair] = analysis

            # Generate recommendations
            report['recommendations'] = self._generate_recommendations(report['market_analysis'])

            logger.info(f"✓ Market report generated")
            return report
        except Exception as e:
            logger.error(f"✗ Market report generation failed: {e}")
            return {}

    def _generate_recommendations(self, market_analysis: Dict) -> List[str]:
        """
        Generate trading recommendations based on market analysis.
        
        Args:
            market_analysis: Market analysis data
            
        Returns:
            List of recommendations
        """
        recommendations = []

        for pair, analysis in market_analysis.items():
            regime = analysis.get('regime', 'sideways')
            volatility = analysis.get('volatility', 0)

            if regime == 'bullish':
                recommendations.append(f"✓ {pair}: Bullish trend detected. Consider momentum strategies.")
            elif regime == 'bearish':
                recommendations.append(f"⚠ {pair}: Bearish trend detected. Use caution or short strategies.")
            else:
                recommendations.append(f"→ {pair}: Sideways market. Range-bound strategies recommended.")

            if volatility > 5:
                recommendations.append(f"⚠ {pair}: High volatility ({volatility:.2f}%). Reduce position size.")

        return recommendations

    def get_latest_report(self) -> Optional[Dict]:
        """
        Get the latest researcher report.
        
        Returns:
            Latest report or None
        """
        return self.reports[-1] if self.reports else None

    def get_report_history(self, limit: int = 10) -> List[Dict]:
        """
        Get report history.
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of reports
        """
        return self.reports[-limit:]

    def get_status(self) -> Dict:
        """
        Get researcher agent status.
        
        Returns:
            Status dictionary
        """
        return {
            'status': 'active',
            'total_reports': len(self.reports),
            'last_report': self.reports[-1] if self.reports else None,
            'timestamp': datetime.now().isoformat(),
        }
