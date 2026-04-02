"""Telegram Monitor Agent for alerts and notifications."""

import logging
from typing import Dict, Optional
from datetime import datetime
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramMonitor:
    """Sends alerts and summaries via Telegram."""

    def __init__(self):
        """Initialize Telegram monitor."""
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.test_connection()

    def test_connection(self) -> bool:
        """
        Test Telegram bot connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{self.bot_token}/getMe",
                timeout=5
            )
            if response.status_code == 200:
                logger.info("✓ Telegram bot connection successful")
                return True
            else:
                logger.error(f"✗ Telegram bot connection failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"✗ Telegram connection error: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """
        Send a message via Telegram.
        
        Args:
            message: Message text
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
            }
            response = requests.post(self.api_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.debug(f"✓ Telegram message sent")
                return True
            else:
                logger.error(f"✗ Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"✗ Telegram send error: {e}")
            return False

    def send_trade_alert(self, trade_data: Dict) -> bool:
        """
        Send trade execution alert.
        
        Args:
            trade_data: Trade details
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
<b>🔔 Trade Executed</b>
<b>Strategy:</b> {trade_data.get('strategy_name', 'N/A')}
<b>Pair:</b> {trade_data.get('pair', 'N/A')}
<b>Side:</b> {trade_data.get('side', 'N/A')}
<b>Entry Price:</b> ₹{trade_data.get('entry_price', 0):.2f}
<b>Quantity:</b> {trade_data.get('quantity', 0)}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send trade alert: {e}")
            return False

    def send_loss_alert(self, loss_data: Dict) -> bool:
        """
        Send alert for significant loss.
        
        Args:
            loss_data: Loss details
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
<b>⚠️ LOSS ALERT</b>
<b>Type:</b> {loss_data.get('type', 'N/A')}
<b>Pair:</b> {loss_data.get('pair', 'N/A')}
<b>Loss Amount:</b> ₹{loss_data.get('loss_amount', 0):.2f}
<b>Loss Percentage:</b> {loss_data.get('loss_percent', 0):.2f}%
<b>Severity:</b> {loss_data.get('severity', 'HIGH')}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send loss alert: {e}")
            return False

    def send_daily_summary(self, summary_data: Dict) -> bool:
        """
        Send daily trading summary.
        
        Args:
            summary_data: Summary statistics
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
<b>📊 Daily Trading Summary</b>
<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

<b>Performance:</b>
<b>Total Trades:</b> {summary_data.get('total_trades', 0)}
<b>Winning Trades:</b> {summary_data.get('winning_trades', 0)}
<b>Losing Trades:</b> {summary_data.get('losing_trades', 0)}
<b>Win Rate:</b> {summary_data.get('win_rate', 0):.2f}%

<b>Financial:</b>
<b>Daily P&L:</b> ₹{summary_data.get('daily_pnl', 0):.2f}
<b>Cumulative P&L:</b> ₹{summary_data.get('cumulative_pnl', 0):.2f}
<b>Avg Win:</b> ₹{summary_data.get('avg_win', 0):.2f}
<b>Avg Loss:</b> ₹{summary_data.get('avg_loss', 0):.2f}

<b>Risk:</b>
<b>Drawdown:</b> {summary_data.get('drawdown', 0):.2f}%
<b>Portfolio Value:</b> ₹{summary_data.get('portfolio_value', 0):.2f}
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send daily summary: {e}")
            return False

    def send_error_alert(self, error_data: Dict) -> bool:
        """
        Send system error alert.
        
        Args:
            error_data: Error details
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
<b>🚨 SYSTEM ERROR</b>
<b>Component:</b> {error_data.get('component', 'N/A')}
<b>Error:</b> {error_data.get('error_message', 'Unknown error')}
<b>Severity:</b> {error_data.get('severity', 'HIGH')}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send error alert: {e}")
            return False

    def send_drawdown_alert(self, drawdown_data: Dict) -> bool:
        """
        Send drawdown alert.
        
        Args:
            drawdown_data: Drawdown details
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
<b>⚠️ DRAWDOWN ALERT</b>
<b>Current Drawdown:</b> {drawdown_data.get('drawdown_percent', 0):.2f}%
<b>Max Allowed:</b> {drawdown_data.get('max_allowed', 0):.2f}%
<b>Portfolio Value:</b> ₹{drawdown_data.get('portfolio_value', 0):.2f}
<b>Peak Value:</b> ₹{drawdown_data.get('peak_value', 0):.2f}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>Action:</b> {drawdown_data.get('action', 'Monitoring')}
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send drawdown alert: {e}")
            return False

    def send_agent_performance(self, agent_data: Dict) -> bool:
        """
        Send agent performance report.
        
        Args:
            agent_data: Agent performance data
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
<b>📈 Agent Performance Report</b>
<b>Agent:</b> {agent_data.get(\'agent_name\', \'N/A\')}

<b>Statistics:</b>
<b>Total Trades:</b> {agent_data.get(\'total_trades\', 0)}
<b>Winning Trades:</b> {agent_data.get(\'winning_trades\', 0)}
<b>Losing Trades:</b> {agent_data.get(\'losing_trades\', 0)}
<b>Win Rate:</b> {agent_data.get(\'win_rate\', 0):.2f}%

<b>P&L:</b>
<b>Total P&L:</b> ₹{agent_data.get(\'total_pnl\', 0):.2f}
<b>Avg Win:</b> ₹{agent_data.get(\'avg_win\', 0):.2f}
<b>Avg Loss:</b> ₹{agent_data.get(\'avg_loss\', 0):.2f}
<b>Profit Factor:</b> {agent_data.get(\'profit_factor\', 0):.2f}
<b>Max Drawdown:</b> {agent_data.get(\'max_drawdown\', 0):.2f}%
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send agent performance: {e}")
            return False

    def send_race_start_alert(self, start_time: datetime, duration_hours: int) -> bool:
        """
        Send alert when a new race starts.
        """
        try:
            message = f"""
<b>🏁 AI Race Started!</b>
<b>Start Time:</b> {start_time.strftime(\'%Y-%m-%d %H:%M:%S\')}
<b>Duration:</b> {duration_hours} hours
Good luck to all agents!
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send race start alert: {e}")
            return False

    def send_leader_change_alert(self, old_leader: str, new_leader: str, new_leader_pnl: float) -> bool:
        """
        Send alert when the race leader changes.
        """
        try:
            message = f"""
<b>👑 Leader Change!</b>
<b>New Leader:</b> {new_leader}
<b>Old Leader:</b> {old_leader}
<b>New Leader P&L:</b> ₹{new_leader_pnl:,.2f}
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send leader change alert: {e}")
            return False

    def send_race_end_alert(self, end_time: datetime, winner_name: str, winner_pnl: float) -> bool:
        """
        Send alert when the race ends.
        """
        try:
            message = f"""
<b>🏆 AI Race Concluded!</b>
<b>End Time:</b> {end_time.strftime(\'%Y-%m-%d %H:%M:%S\')}
<b>Winner:</b> {winner_name}
<b>Winner P&L:</b> ₹{winner_pnl:,.2f}
Congratulations to the champion!
            """
            return self.send_message(message)
        except Exception as e:
            logger.error(f"✗ Failed to send race end alert: {e}")
            return False
