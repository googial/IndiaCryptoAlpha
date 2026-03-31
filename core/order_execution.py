"""Simulated order execution engine for paper trading."""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from uuid import uuid4
from config import PAPER_TRADING_MODE

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Handles simulated order execution for paper trading."""

    def __init__(self):
        """Initialize the order executor."""
        self.orders = {}  # {order_id: order_details}
        self.filled_orders = []
        self.pending_orders = []
        self.order_counter = 0

    def create_order(self, pair: str, side: str, quantity: float, 
                    price: float, order_type: str = 'limit') -> Dict:
        """
        Create a new order.
        
        Args:
            pair: Trading pair (e.g., 'BTC-INR')
            side: 'BUY' or 'SELL'
            quantity: Quantity to trade
            price: Order price
            order_type: 'limit' or 'market'
            
        Returns:
            Order details dictionary
        """
        order_id = str(uuid4())[:8]
        order = {
            'order_id': order_id,
            'pair': pair,
            'side': side,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'filled_at': None,
            'filled_quantity': 0,
        }
        
        self.orders[order_id] = order
        self.pending_orders.append(order_id)
        
        logger.info(f"✓ Order created: {order_id} | {side} {quantity} {pair} @ {price:.2f}")
        return order

    def execute_order(self, order_id: str, execution_price: float) -> Dict:
        """
        Execute (fill) a pending order.
        
        Args:
            order_id: Order ID to execute
            execution_price: Price at which order is filled
            
        Returns:
            Execution details
        """
        if order_id not in self.orders:
            logger.error(f"✗ Order not found: {order_id}")
            return {}

        order = self.orders[order_id]
        
        if order['status'] != 'pending':
            logger.warning(f"⚠ Order {order_id} is not pending (status: {order['status']})")
            return {}

        # Simulate order fill
        order['status'] = 'filled'
        order['filled_quantity'] = order['quantity']
        order['filled_at'] = datetime.now().isoformat()
        order['execution_price'] = execution_price

        self.filled_orders.append(order_id)
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)

        execution = {
            'order_id': order_id,
            'pair': order['pair'],
            'side': order['side'],
            'quantity': order['quantity'],
            'price': execution_price,
            'executed_at': order['filled_at'],
            'commission': order['quantity'] * execution_price * 0.002,  # 0.2% taker fee
        }

        logger.info(f"✓ Order executed: {order_id} | {order['side']} {order['quantity']} {order['pair']} @ {execution_price:.2f}")
        return execution

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if order_id not in self.orders:
            logger.error(f"✗ Order not found: {order_id}")
            return False

        order = self.orders[order_id]
        
        if order['status'] != 'pending':
            logger.warning(f"⚠ Cannot cancel non-pending order: {order_id}")
            return False

        order['status'] = 'cancelled'
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)

        logger.info(f"✓ Order cancelled: {order_id}")
        return True

    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """
        Get status of an order.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order details or None if not found
        """
        return self.orders.get(order_id)

    def get_pending_orders(self) -> List[Dict]:
        """
        Get all pending orders.
        
        Returns:
            List of pending order details
        """
        return [self.orders[oid] for oid in self.pending_orders]

    def get_filled_orders(self, limit: int = 100) -> List[Dict]:
        """
        Get recent filled orders.
        
        Args:
            limit: Maximum number of orders to return
            
        Returns:
            List of filled order details
        """
        return [self.orders[oid] for oid in self.filled_orders[-limit:]]

    def get_order_history(self, pair: Optional[str] = None, 
                         limit: int = 100) -> List[Dict]:
        """
        Get order history, optionally filtered by pair.
        
        Args:
            pair: Optional pair to filter by
            limit: Maximum number of orders to return
            
        Returns:
            List of order details
        """
        history = []
        for order_id in self.filled_orders[-limit:]:
            order = self.orders[order_id]
            if pair is None or order['pair'] == pair:
                history.append(order)
        return history

    def simulate_market_execution(self, pair: str, side: str, quantity: float,
                                 current_price: float, slippage: float = 0.001) -> Dict:
        """
        Simulate a market order execution with slippage.
        
        Args:
            pair: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Quantity to trade
            current_price: Current market price
            slippage: Slippage percentage (default 0.1%)
            
        Returns:
            Execution details
        """
        # Apply slippage
        if side == 'BUY':
            execution_price = current_price * (1 + slippage)
        else:  # SELL
            execution_price = current_price * (1 - slippage)

        # Create and execute order
        order = self.create_order(pair, side, quantity, current_price, order_type='market')
        execution = self.execute_order(order['order_id'], execution_price)

        return execution

    def get_statistics(self) -> Dict:
        """
        Get order execution statistics.
        
        Returns:
            Statistics dictionary
        """
        total_orders = len(self.orders)
        filled_count = len(self.filled_orders)
        pending_count = len(self.pending_orders)
        
        total_volume = sum(
            self.orders[oid]['quantity'] * self.orders[oid]['price']
            for oid in self.filled_orders
        )

        return {
            'total_orders': total_orders,
            'filled_orders': filled_count,
            'pending_orders': pending_count,
            'total_volume': total_volume,
            'fill_rate': filled_count / total_orders if total_orders > 0 else 0,
        }
