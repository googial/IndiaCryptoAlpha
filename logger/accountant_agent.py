"""Logger/Accountant Agent for trade logging and financial calculations."""

import logging
from typing import Dict, Optional
from datetime import datetime
from uuid import uuid4
from .database import TradeDatabase
from .excel_logger import ExcelLogger
from config import GST_RATE, INCOME_TAX_RATE, COINDCX_MAKER_FEE, COINDCX_TAKER_FEE

logger = logging.getLogger(__name__)


class AccountantAgent:
    """Handles all trade logging, financial calculations, and reporting."""

    def __init__(self):
        """Initialize the accountant agent."""
        self.db = TradeDatabase()
        self.excel = ExcelLogger()
        self.cumulative_pnl = 0.0
        logger.info("✓ Accountant Agent initialized")

    def calculate_trade_financials(self, entry_price: float, exit_price: float,
                                  quantity: float, side: str = 'BUY') -> Dict:
        """
        Calculate complete financial metrics for a trade including fees and taxes.
        
        Args:
            entry_price: Entry price per unit
            exit_price: Exit price per unit
            quantity: Quantity traded
            side: 'BUY' or 'SELL'
            
        Returns:
            Dictionary with financial calculations
        """
        # Calculate gross P&L
        if side == 'BUY':
            gross_pnl = (exit_price - entry_price) * quantity
        else:  # SELL
            gross_pnl = (entry_price - exit_price) * quantity

        # Calculate fees (0.1% maker + 0.2% taker = 0.3% total)
        entry_fee = entry_price * quantity * COINDCX_TAKER_FEE
        exit_fee = exit_price * quantity * COINDCX_TAKER_FEE
        total_fees = entry_fee + exit_fee

        # Calculate GST on fees (18%)
        gst = total_fees * GST_RATE

        # Calculate income tax (30% on profits only)
        tax = max(0, gross_pnl * INCOME_TAX_RATE)

        # Calculate net P&L
        net_pnl = gross_pnl - total_fees - gst - tax

        return {
            'gross_pnl': gross_pnl,
            'entry_fee': entry_fee,
            'exit_fee': exit_fee,
            'total_fees': total_fees,
            'gst': gst,
            'tax': tax,
            'net_pnl': net_pnl,
        }

    def log_completed_trade(self, trade_details: Dict) -> bool:
        """
        Log a completed trade to both SQLite and Excel.
        
        Args:
            trade_details: Dictionary with trade information
                - strategy_name: Name of the strategy
                - pair: Trading pair (e.g., 'BTC-INR')
                - side: 'BUY' or 'SELL'
                - entry_price: Entry price
                - exit_price: Exit price
                - quantity: Quantity traded
                - entry_time: Entry timestamp
                - exit_time: Exit timestamp
                - leverage: Leverage (default 1.0)
                - notes: Optional notes
                
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate trade ID
            trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid4())[:8]}"

            # Calculate financials
            financials = self.calculate_trade_financials(
                trade_details['entry_price'],
                trade_details['exit_price'],
                trade_details['quantity'],
                trade_details.get('side', 'BUY')
            )

            # Update cumulative P&L
            self.cumulative_pnl += financials['net_pnl']

            # Prepare complete trade record
            trade_record = {
                'trade_id': trade_id,
                'strategy_name': trade_details.get('strategy_name'),
                'pair': trade_details.get('pair'),
                'side': trade_details.get('side', 'BUY'),
                'entry_price': trade_details.get('entry_price'),
                'exit_price': trade_details.get('exit_price'),
                'quantity': trade_details.get('quantity'),
                'leverage': trade_details.get('leverage', 1.0),
                'entry_time': trade_details.get('entry_time'),
                'exit_time': trade_details.get('exit_time'),
                'fees_inr': financials['total_fees'],
                'gst': financials['gst'],
                'realized_pnl_inr': financials['net_pnl'],
                'tax_estimate_30pct': financials['tax'],
                'cumulative_pnl': self.cumulative_pnl,
                'status': 'closed',
                'notes': trade_details.get('notes', ''),
            }

            # Log to database
            db_success = self.db.log_trade(trade_record)

            # Log to Excel
            excel_success = self.excel.log_trade(trade_record)

            if db_success and excel_success:
                logger.info(f"✓ Trade logged successfully: {trade_id} | P&L: ₹{financials['net_pnl']:.2f}")
                return True
            else:
                logger.error(f"✗ Failed to log trade {trade_id}")
                return False

        except Exception as e:
            logger.error(f"✗ Error logging trade: {e}")
            return False

    def get_trade_history(self, pair: Optional[str] = None, 
                         strategy: Optional[str] = None, limit: int = 100) -> list:
        """
        Retrieve trade history from database.
        
        Args:
            pair: Optional pair filter
            strategy: Optional strategy filter
            limit: Maximum trades to return
            
        Returns:
            List of trade records
        """
        return self.db.get_trades(pair=pair, strategy=strategy, limit=limit)

    def get_statistics(self, strategy: Optional[str] = None) -> Dict:
        """
        Get comprehensive trading statistics.
        
        Args:
            strategy: Optional strategy filter
            
        Returns:
            Dictionary with statistics
        """
        stats = self.db.get_statistics(strategy=strategy)
        stats['cumulative_pnl'] = self.cumulative_pnl
        return stats

    def log_portfolio_snapshot(self, portfolio_data: Dict) -> bool:
        """
        Log a portfolio snapshot for tracking over time.
        
        Args:
            portfolio_data: Dictionary with portfolio metrics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.db.log_portfolio_snapshot(portfolio_data)
        except Exception as e:
            logger.error(f"✗ Failed to log portfolio snapshot: {e}")
            return False

    def log_agent_performance(self, agent_data: Dict) -> bool:
        """
        Log agent performance metrics.
        
        Args:
            agent_data: Dictionary with agent performance data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.db.log_agent_performance(agent_data)
        except Exception as e:
            logger.error(f"✗ Failed to log agent performance: {e}")
            return False

    def log_alert(self, alert_data: Dict) -> bool:
        """
        Log an alert or significant event.
        
        Args:
            alert_data: Dictionary with alert details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.db.log_alert(alert_data)
        except Exception as e:
            logger.error(f"✗ Failed to log alert: {e}")
            return False

    def generate_daily_report(self) -> Dict:
        """
        Generate a daily trading report.
        
        Returns:
            Dictionary with daily statistics
        """
        try:
            stats = self.get_statistics()
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_trades': stats.get('total_trades', 0),
                'winning_trades': stats.get('winning_trades', 0),
                'losing_trades': stats.get('losing_trades', 0),
                'win_rate': f"{stats.get('win_rate', 0) * 100:.2f}%",
                'total_pnl': f"₹{stats.get('total_pnl', 0):.2f}",
                'cumulative_pnl': f"₹{self.cumulative_pnl:.2f}",
                'avg_win': f"₹{stats.get('avg_win', 0):.2f}",
                'avg_loss': f"₹{stats.get('avg_loss', 0):.2f}",
                'profit_factor': f"{stats.get('profit_factor', 0):.2f}",
            }
            logger.info(f"✓ Daily report generated: {report}")
            return report
        except Exception as e:
            logger.error(f"✗ Failed to generate daily report: {e}")
            return {}

    def close(self):
        """Close all resources."""
        try:
            self.db.close()
            self.excel.close()
            logger.info("✓ Accountant Agent closed")
        except Exception as e:
            logger.error(f"✗ Failed to close Accountant Agent: {e}")
