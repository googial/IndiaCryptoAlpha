"""Monitor Agent for system monitoring and alerts."""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from .telegram_monitor import TelegramMonitor
from config import DAILY_MAX_LOSS_PERCENT

logger = logging.getLogger(__name__)


class MonitorAgent:
    """Monitors system health, trades, and sends alerts."""

    def __init__(self):
        """Initialize monitor agent."""
        self.telegram = TelegramMonitor()
        self.last_alert_time = {}
        self.alert_cooldown = 300  # 5 minutes between similar alerts
        logger.info("✓ Monitor Agent initialized")

    def check_trade_loss(self, trade_pnl: float, trade_pair: str) -> bool:
        """
        Check if a trade loss exceeds threshold (>2% loss).
        
        Args:
            trade_pnl: Trade P&L in INR
            trade_pair: Trading pair
            
        Returns:
            True if alert sent, False otherwise
        """
        try:
            # Assuming 100,000 initial portfolio
            loss_percent = abs(trade_pnl) / 100000 * 100
            
            if trade_pnl < 0 and loss_percent > 2:
                alert_key = f"trade_loss_{trade_pair}"
                if self._should_alert(alert_key):
                    alert_data = {
                        'type': 'Trade Loss',
                        'pair': trade_pair,
                        'loss_amount': trade_pnl,
                        'loss_percent': loss_percent,
                        'severity': 'HIGH' if loss_percent > 5 else 'MEDIUM',
                    }
                    self.telegram.send_loss_alert(alert_data)
                    self._update_alert_time(alert_key)
                    logger.warning(f"⚠ Trade loss alert sent for {trade_pair}: {loss_percent:.2f}%")
                    return True
        except Exception as e:
            logger.error(f"✗ Failed to check trade loss: {e}")
        
        return False

    def check_drawdown(self, current_value: float, peak_value: float, 
                      max_allowed: float = DAILY_MAX_LOSS_PERCENT) -> bool:
        """
        Check if portfolio drawdown exceeds threshold.
        
        Args:
            current_value: Current portfolio value
            peak_value: Peak portfolio value
            max_allowed: Maximum allowed drawdown percentage
            
        Returns:
            True if alert sent, False otherwise
        """
        try:
            if peak_value <= 0:
                return False
            
            drawdown = (peak_value - current_value) / peak_value * 100
            
            if drawdown > max_allowed * 100:
                alert_key = "drawdown_alert"
                if self._should_alert(alert_key):
                    alert_data = {
                        'drawdown_percent': drawdown,
                        'max_allowed': max_allowed * 100,
                        'portfolio_value': current_value,
                        'peak_value': peak_value,
                        'action': 'PAUSE' if drawdown > max_allowed * 100 * 1.5 else 'MONITOR',
                    }
                    self.telegram.send_drawdown_alert(alert_data)
                    self._update_alert_time(alert_key)
                    logger.warning(f"⚠ Drawdown alert sent: {drawdown:.2f}%")
                    return True
        except Exception as e:
            logger.error(f"✗ Failed to check drawdown: {e}")
        
        return False

    def check_system_error(self, component: str, error_message: str) -> bool:
        """
        Send system error alert.
        
        Args:
            component: Component that failed
            error_message: Error message
            
        Returns:
            True if alert sent, False otherwise
        """
        try:
            alert_key = f"error_{component}"
            if self._should_alert(alert_key):
                error_data = {
                    'component': component,
                    'error_message': error_message,
                    'severity': 'CRITICAL',
                }
                self.telegram.send_error_alert(error_data)
                self._update_alert_time(alert_key)
                logger.error(f"✗ System error alert sent for {component}")
                return True
        except Exception as e:
            logger.error(f"✗ Failed to send error alert: {e}")
        
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
            return self.telegram.send_daily_summary(summary_data)
        except Exception as e:
            logger.error(f"✗ Failed to send daily summary: {e}")
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
            return self.telegram.send_agent_performance(agent_data)
        except Exception as e:
            logger.error(f"✗ Failed to send agent performance: {e}")
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
            return self.telegram.send_trade_alert(trade_data)
        except Exception as e:
            logger.error(f"✗ Failed to send trade alert: {e}")
            return False

    def _should_alert(self, alert_key: str) -> bool:
        """
        Check if enough time has passed since last similar alert.
        
        Args:
            alert_key: Unique alert identifier
            
        Returns:
            True if alert should be sent, False otherwise
        """
        if alert_key not in self.last_alert_time:
            return True
        
        last_time = self.last_alert_time[alert_key]
        if datetime.now() - last_time > timedelta(seconds=self.alert_cooldown):
            return True
        
        return False

    def _update_alert_time(self, alert_key: str):
        """
        Update last alert time for a key.
        
        Args:
            alert_key: Unique alert identifier
        """
        self.last_alert_time[alert_key] = datetime.now()

    def get_status(self) -> Dict:
        """
        Get monitor agent status.
        
        Returns:
            Status dictionary
        """
        return {
            'status': 'active',
            'telegram_connected': self.telegram.test_connection(),
            'last_alerts': len(self.last_alert_time),
            'timestamp': datetime.now().isoformat(),
        }
