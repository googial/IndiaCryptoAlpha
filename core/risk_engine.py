"""Risk management engine for validating and enforcing trading rules."""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from config import (
    RISK_PER_TRADE,
    MAX_PORTFOLIO_EXPOSURE,
    STOP_LOSS_PERCENT,
    DAILY_MAX_LOSS_PERCENT,
)

logger = logging.getLogger(__name__)


class RiskEngine:
    """Manages risk parameters and validates trade proposals."""

    def __init__(self, initial_portfolio: float):
        """
        Initialize the risk engine.
        
        Args:
            initial_portfolio: Initial portfolio value in INR
        """
        self.initial_portfolio = initial_portfolio
        self.current_portfolio = initial_portfolio
        self.positions = {}  # {pair: {quantity, entry_price, ...}}
        self.daily_pnl = 0.0
        self.cumulative_pnl = 0.0
        self.trade_history = []
        self.daily_loss_limit = initial_portfolio * DAILY_MAX_LOSS_PERCENT
        self.last_reset_date = datetime.now().date()

    def validate_trade(self, pair: str, side: str, quantity: float, 
                      entry_price: float, current_price: float) -> Tuple[bool, str]:
        """
        Validate a trade proposal against risk parameters.
        
        Args:
            pair: Trading pair (e.g., 'BTC-INR')
            side: 'BUY' or 'SELL'
            quantity: Number of units to trade
            entry_price: Entry price
            current_price: Current market price
            
        Returns:
            Tuple of (is_valid, reason_message)
        """
        # Check if daily loss limit exceeded
        if self.daily_pnl <= -self.daily_loss_limit:
            return False, f"Daily loss limit ({DAILY_MAX_LOSS_PERCENT*100}%) exceeded. Trading paused."

        # Calculate trade risk
        trade_risk = quantity * entry_price * RISK_PER_TRADE
        if trade_risk > self.current_portfolio * RISK_PER_TRADE:
            return False, f"Trade risk ({trade_risk:.2f}) exceeds max risk per trade ({self.current_portfolio * RISK_PER_TRADE:.2f})"

        # Check portfolio exposure
        if side == 'BUY':
            exposure = quantity * entry_price
            if exposure > self.current_portfolio * MAX_PORTFOLIO_EXPOSURE:
                return False, f"Portfolio exposure ({exposure:.2f}) exceeds max ({self.current_portfolio * MAX_PORTFOLIO_EXPOSURE:.2f})"

        # Validate stop loss
        if side == 'BUY':
            stop_loss = entry_price * (1 - STOP_LOSS_PERCENT)
            if stop_loss < 0:
                return False, "Stop loss would be negative"
        else:  # SELL
            stop_loss = entry_price * (1 + STOP_LOSS_PERCENT)

        logger.info(f"✓ Trade validated: {side} {quantity} {pair} @ {entry_price:.2f}")
        return True, "Trade validated successfully"

    def calculate_pnl(self, pair: str, entry_price: float, exit_price: float, 
                     quantity: float, side: str = 'BUY') -> Dict:
        """
        Calculate P&L for a completed trade.
        
        Args:
            pair: Trading pair
            entry_price: Entry price
            exit_price: Exit price
            quantity: Quantity traded
            side: 'BUY' or 'SELL'
            
        Returns:
            Dictionary with P&L details
        """
        if side == 'BUY':
            pnl = (exit_price - entry_price) * quantity
        else:  # SELL
            pnl = (entry_price - exit_price) * quantity

        # Calculate fees (CoinDCX: 0.1% maker, 0.2% taker)
        fees = (entry_price * quantity * 0.002) + (exit_price * quantity * 0.002)

        # Calculate GST (18% on fees)
        gst = fees * 0.18

        # Calculate tax (30% on profits)
        tax = max(0, pnl * 0.30)

        net_pnl = pnl - fees - gst - tax

        return {
            'gross_pnl': pnl,
            'fees': fees,
            'gst': gst,
            'tax': tax,
            'net_pnl': net_pnl,
        }

    def update_portfolio(self, pair: str, side: str, quantity: float, 
                        price: float, trade_type: str = 'entry'):
        """
        Update portfolio after a trade execution.
        
        Args:
            pair: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Quantity traded
            price: Trade price
            trade_type: 'entry' or 'exit'
        """
        trade_value = quantity * price

        if side == 'BUY':
            self.current_portfolio -= trade_value
            if pair not in self.positions:
                self.positions[pair] = {'quantity': 0, 'entry_price': 0, 'entry_time': None}
            self.positions[pair]['quantity'] += quantity
            self.positions[pair]['entry_price'] = price
            self.positions[pair]['entry_time'] = datetime.now()
        else:  # SELL
            self.current_portfolio += trade_value
            if pair in self.positions:
                self.positions[pair]['quantity'] -= quantity
                if self.positions[pair]['quantity'] <= 0:
                    del self.positions[pair]

        logger.info(f"✓ Portfolio updated: {side} {quantity} {pair} @ {price:.2f}")

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value including open positions.
        
        Args:
            current_prices: Dictionary of current prices {pair: price}
            
        Returns:
            Total portfolio value
        """
        total = self.current_portfolio
        for pair, position in self.positions.items():
            if pair in current_prices:
                total += position['quantity'] * current_prices[pair]
        return total

    def get_drawdown(self, current_portfolio_value: float) -> float:
        """
        Calculate current drawdown percentage.
        
        Args:
            current_portfolio_value: Current portfolio value
            
        Returns:
            Drawdown percentage
        """
        if self.initial_portfolio <= 0:
            return 0.0
        drawdown = (self.initial_portfolio - current_portfolio_value) / self.initial_portfolio
        return max(0, drawdown)

    def check_daily_reset(self):
        """Reset daily P&L if a new day has started."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = today
            logger.info("✓ Daily P&L reset")

    def get_risk_metrics(self, current_portfolio_value: float) -> Dict:
        """
        Get comprehensive risk metrics.
        
        Args:
            current_portfolio_value: Current portfolio value
            
        Returns:
            Dictionary with risk metrics
        """
        self.check_daily_reset()
        
        return {
            'portfolio_value': current_portfolio_value,
            'cash': self.current_portfolio,
            'positions': len(self.positions),
            'daily_pnl': self.daily_pnl,
            'cumulative_pnl': self.cumulative_pnl,
            'drawdown': self.get_drawdown(current_portfolio_value),
            'daily_loss_limit': self.daily_loss_limit,
            'daily_loss_remaining': self.daily_loss_limit - abs(min(0, self.daily_pnl)),
        }

    def apply_stop_loss(self, pair: str, current_price: float) -> Optional[Dict]:
        """
        Check if stop loss should be triggered for a position.
        
        Args:
            pair: Trading pair
            current_price: Current market price
            
        Returns:
            Trade execution details if stop loss triggered, None otherwise
        """
        if pair not in self.positions:
            return None

        position = self.positions[pair]
        entry_price = position['entry_price']
        stop_loss_price = entry_price * (1 - STOP_LOSS_PERCENT)

        if current_price <= stop_loss_price:
            logger.warning(f"⚠ Stop loss triggered for {pair}: {current_price:.2f} <= {stop_loss_price:.2f}")
            return {
                'pair': pair,
                'side': 'SELL',
                'quantity': position['quantity'],
                'price': current_price,
                'reason': 'stop_loss',
            }

        return None
