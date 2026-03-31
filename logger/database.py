"""SQLite database management for trade logging."""

import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class TradeDatabase:
    """Manages SQLite database for trade logging and analytics."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialize the database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def init_database(self):
        """Initialize database tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()

            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    strategy_name TEXT NOT NULL,
                    pair TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    quantity REAL NOT NULL,
                    leverage REAL DEFAULT 1.0,
                    entry_time DATETIME NOT NULL,
                    exit_time DATETIME,
                    fees_inr REAL DEFAULT 0.0,
                    gst REAL DEFAULT 0.0,
                    realized_pnl_inr REAL DEFAULT 0.0,
                    tax_estimate_30pct REAL DEFAULT 0.0,
                    cumulative_pnl REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'open',
                    notes TEXT
                )
            ''')

            # Agent performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent_name TEXT NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    total_pnl REAL DEFAULT 0.0,
                    avg_win REAL DEFAULT 0.0,
                    avg_loss REAL DEFAULT 0.0,
                    profit_factor REAL DEFAULT 0.0,
                    max_drawdown REAL DEFAULT 0.0,
                    sharpe_ratio REAL DEFAULT 0.0
                )
            ''')

            # Portfolio snapshot table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_snapshot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    portfolio_value REAL NOT NULL,
                    cash REAL NOT NULL,
                    positions_count INTEGER DEFAULT 0,
                    daily_pnl REAL DEFAULT 0.0,
                    cumulative_pnl REAL DEFAULT 0.0,
                    drawdown REAL DEFAULT 0.0
                )
            ''')

            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    agent_name TEXT,
                    pair TEXT
                )
            ''')

            self.connection.commit()
            logger.info(f"✓ Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize database: {e}")
            raise

    def log_trade(self, trade_data: Dict) -> bool:
        """
        Log a completed trade to the database.
        
        Args:
            trade_data: Dictionary with trade details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO trades (
                    trade_id, strategy_name, pair, side, entry_price, exit_price,
                    quantity, leverage, entry_time, exit_time, fees_inr, gst,
                    realized_pnl_inr, tax_estimate_30pct, cumulative_pnl, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('trade_id'),
                trade_data.get('strategy_name'),
                trade_data.get('pair'),
                trade_data.get('side'),
                trade_data.get('entry_price'),
                trade_data.get('exit_price'),
                trade_data.get('quantity'),
                trade_data.get('leverage', 1.0),
                trade_data.get('entry_time'),
                trade_data.get('exit_time'),
                trade_data.get('fees_inr', 0.0),
                trade_data.get('gst', 0.0),
                trade_data.get('realized_pnl_inr', 0.0),
                trade_data.get('tax_estimate_30pct', 0.0),
                trade_data.get('cumulative_pnl', 0.0),
                trade_data.get('status', 'closed'),
                trade_data.get('notes'),
            ))
            self.connection.commit()
            logger.info(f"✓ Trade logged: {trade_data.get('trade_id')}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to log trade: {e}")
            return False

    def get_trades(self, pair: Optional[str] = None, 
                  strategy: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve trades from database with optional filtering.
        
        Args:
            pair: Optional pair filter
            strategy: Optional strategy filter
            limit: Maximum number of trades to return
            
        Returns:
            List of trade records
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM trades WHERE 1=1"
            params = []

            if pair:
                query += " AND pair = ?"
                params.append(pair)
            if strategy:
                query += " AND strategy_name = ?"
                params.append(strategy)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            trades = [dict(row) for row in cursor.fetchall()]
            return trades
        except Exception as e:
            logger.error(f"✗ Failed to retrieve trades: {e}")
            return []

    def log_portfolio_snapshot(self, snapshot_data: Dict) -> bool:
        """
        Log a portfolio snapshot.
        
        Args:
            snapshot_data: Dictionary with portfolio details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO portfolio_snapshot (
                    portfolio_value, cash, positions_count, daily_pnl, cumulative_pnl, drawdown
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_data.get('portfolio_value'),
                snapshot_data.get('cash'),
                snapshot_data.get('positions_count', 0),
                snapshot_data.get('daily_pnl', 0.0),
                snapshot_data.get('cumulative_pnl', 0.0),
                snapshot_data.get('drawdown', 0.0),
            ))
            self.connection.commit()
            return True
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
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO agent_performance (
                    agent_name, total_trades, winning_trades, losing_trades,
                    win_rate, total_pnl, avg_win, avg_loss, profit_factor,
                    max_drawdown, sharpe_ratio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_data.get('agent_name'),
                agent_data.get('total_trades', 0),
                agent_data.get('winning_trades', 0),
                agent_data.get('losing_trades', 0),
                agent_data.get('win_rate', 0.0),
                agent_data.get('total_pnl', 0.0),
                agent_data.get('avg_win', 0.0),
                agent_data.get('avg_loss', 0.0),
                agent_data.get('profit_factor', 0.0),
                agent_data.get('max_drawdown', 0.0),
                agent_data.get('sharpe_ratio', 0.0),
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"✗ Failed to log agent performance: {e}")
            return False

    def log_alert(self, alert_data: Dict) -> bool:
        """
        Log an alert/event.
        
        Args:
            alert_data: Dictionary with alert details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, message, agent_name, pair)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alert_data.get('alert_type'),
                alert_data.get('severity'),
                alert_data.get('message'),
                alert_data.get('agent_name'),
                alert_data.get('pair'),
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"✗ Failed to log alert: {e}")
            return False

    def get_statistics(self, strategy: Optional[str] = None) -> Dict:
        """
        Calculate trading statistics.
        
        Args:
            strategy: Optional strategy filter
            
        Returns:
            Dictionary with statistics
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM trades WHERE status = 'closed'"
            params = []

            if strategy:
                query += " AND strategy_name = ?"
                params.append(strategy)

            cursor.execute(query, params)
            trades = cursor.fetchall()

            if not trades:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0,
                    'total_pnl': 0.0,
                    'avg_win': 0.0,
                    'avg_loss': 0.0,
                }

            total_pnl = sum(row['realized_pnl_inr'] for row in trades)
            winning_trades = sum(1 for row in trades if row['realized_pnl_inr'] > 0)
            losing_trades = sum(1 for row in trades if row['realized_pnl_inr'] < 0)
            
            wins = [row['realized_pnl_inr'] for row in trades if row['realized_pnl_inr'] > 0]
            losses = [row['realized_pnl_inr'] for row in trades if row['realized_pnl_inr'] < 0]

            return {
                'total_trades': len(trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': winning_trades / len(trades) if trades else 0.0,
                'total_pnl': total_pnl,
                'avg_win': sum(wins) / len(wins) if wins else 0.0,
                'avg_loss': sum(losses) / len(losses) if losses else 0.0,
                'profit_factor': abs(sum(wins) / sum(losses)) if losses else 0.0,
            }
        except Exception as e:
            logger.error(f"✗ Failed to calculate statistics: {e}")
            return {}

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("✓ Database connection closed")
