"""
Generate demo trading data for dashboard testing
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import DATABASE_PATH

def generate_demo_trades(num_trades=100):
    """Generate realistic demo trading data."""
    
    trades = []
    base_price = 100000
    
    strategies = ['RSI+MACD Momentum', 'Bollinger Band + Volume', 'EMA Crossover + Supertrend']
    pairs = ['BTC-INR', 'ETH-INR', 'BNB-INR']
    
    for i in range(num_trades):
        entry_price = base_price + np.random.randn() * 5000
        pnl_pct = np.random.normal(0.5, 2)  # Slightly positive bias
        exit_price = entry_price * (1 + pnl_pct / 100)
        quantity = np.random.uniform(0.1, 1.0)
        realized_pnl = (exit_price - entry_price) * quantity
        
        trade = {
            'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
            'strategy': np.random.choice(strategies),
            'pair': np.random.choice(pairs),
            'side': np.random.choice(['BUY', 'SELL']),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'realized_pnl_inr': realized_pnl,
            'unrealized_pnl_inr': 0,
            'status': 'closed',
        }
        trades.append(trade)
    
    return trades

def insert_demo_data():
    """Insert demo data into database."""
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy TEXT NOT NULL,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                quantity REAL NOT NULL,
                realized_pnl_inr REAL NOT NULL,
                unrealized_pnl_inr REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        # Generate and insert demo trades
        trades = generate_demo_trades(100)
        
        for trade in trades:
            cursor.execute('''
                INSERT INTO trades (timestamp, strategy, pair, side, entry_price, exit_price, quantity, realized_pnl_inr, unrealized_pnl_inr, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade['timestamp'],
                trade['strategy'],
                trade['pair'],
                trade['side'],
                trade['entry_price'],
                trade['exit_price'],
                trade['quantity'],
                trade['realized_pnl_inr'],
                trade['unrealized_pnl_inr'],
                trade['status']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Inserted {len(trades)} demo trades into database")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    insert_demo_data()
