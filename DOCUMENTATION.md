# IndiaCryptoAlpha - Complete Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)

## System Overview

IndiaCryptoAlpha is a professional-grade multi-agent paper trading system designed for the Indian cryptocurrency exchange CoinDCX. It features:

- **Multi-Agent Architecture**: 3+ independent strategy agents
- **Risk Management**: Strict risk parameters and enforcement
- **Real-time Monitoring**: Telegram alerts and notifications
- **Comprehensive Logging**: SQLite + Excel trade records
- **Interactive Dashboard**: Streamlit-based UI
- **Research Capabilities**: Backtesting and market analysis
- **Hybrid Deployment**: Runs on laptops and Android (Termux)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                  Market Data Layer                       │
│              (CoinDCX API via CCXT)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │Strategy │  │Strategy │  │Strategy │
   │Agent 1  │  │Agent 2  │  │Agent 3  │
   └────┬────┘  └────┬────┘  └────┬────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  Risk Engine     │
            │  (Validation)    │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │Order Execution   │
            │(Simulated)       │
            └────────┬─────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │SQLite  │  │Excel   │  │Telegram  │
    │Logger  │  │Logger  │  │Monitor   │
    └────────┘  └────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │Streamlit         │
            │Dashboard         │
            └──────────────────┘
```

### Data Flow

1. **Market Data**: Fetched from CoinDCX API every hour
2. **Signal Generation**: Strategy agents analyze data
3. **Risk Validation**: Risk engine approves/rejects trades
4. **Order Execution**: Simulated orders are executed
5. **Logging**: Trades recorded to SQLite + Excel
6. **Monitoring**: Alerts sent via Telegram
7. **Dashboard**: Real-time visualization

## Components

### Core Module (`core/`)

#### MarketDataManager
Handles all market data operations:

```python
from core import MarketDataManager

manager = MarketDataManager()

# Get current price
ticker = manager.get_ticker('BTC/INR')

# Get candlestick data
ohlcv = manager.get_ohlcv('BTC/INR', timeframe='1h', limit=100)

# Get historical data for backtesting
historical = manager.get_historical_data('BTC/INR', days=30)

# Analyze market regime
regime = manager.get_market_regime('BTC/INR')  # 'bullish', 'bearish', 'sideways'
```

#### RiskEngine
Validates trades and manages portfolio risk:

```python
from core import RiskEngine

engine = RiskEngine(initial_portfolio=100000)

# Validate trade
is_valid, reason = engine.validate_trade(
    pair='BTC-INR',
    side='BUY',
    quantity=0.1,
    entry_price=2000000,
    current_price=2000000
)

# Calculate P&L
pnl_data = engine.calculate_pnl(
    pair='BTC-INR',
    entry_price=2000000,
    exit_price=2100000,
    quantity=0.1,
    side='BUY'
)

# Get risk metrics
metrics = engine.get_risk_metrics(current_portfolio_value=105000)
```

#### OrderExecutor
Simulates order execution:

```python
from core import OrderExecutor

executor = OrderExecutor()

# Create order
order = executor.create_order(
    pair='BTC-INR',
    side='BUY',
    quantity=0.1,
    price=2000000
)

# Execute order
execution = executor.execute_order(order['order_id'], execution_price=2000000)

# Get order history
history = executor.get_order_history(pair='BTC-INR', limit=50)
```

### Agents Module (`agents/`)

#### BaseStrategyAgent
Abstract base class for all strategies:

```python
from agents import BaseStrategyAgent

class MyStrategy(BaseStrategyAgent):
    def generate_signal(self, pair, data):
        # Your strategy logic
        return {
            'side': 'BUY',
            'confidence': 0.8,
            'quantity': 0.1,
            'reason': 'Your reason'
        }
```

#### RSIMACDAgent
Momentum strategy combining RSI and MACD:
- Entry: RSI oversold + MACD bullish crossover
- Exit: RSI overbought + MACD bearish crossover

#### BollingerVolumeAgent
Breakout strategy with volume confirmation:
- Entry: Price breaks Bollinger Band + volume spike
- Exit: Opposite break + volume

#### EMASupertrendAgent
Trend-following strategy:
- Entry: EMA fast crosses above slow + Supertrend uptrend
- Exit: EMA fast crosses below slow + Supertrend downtrend

### Logger Module (`logger/`)

#### TradeDatabase
SQLite database operations:

```python
from logger import TradeDatabase

db = TradeDatabase()

# Log trade
db.log_trade({
    'trade_id': 'TRADE_20260331120000_abc123',
    'strategy_name': 'RSI+MACD',
    'pair': 'BTC-INR',
    'side': 'BUY',
    'entry_price': 2000000,
    'exit_price': 2100000,
    'quantity': 0.1,
    'fees_inr': 600,
    'gst': 108,
    'realized_pnl_inr': 8292,
    'tax_estimate_30pct': 3000,
    'cumulative_pnl': 8292
})

# Get trades
trades = db.get_trades(pair='BTC-INR', limit=100)

# Get statistics
stats = db.get_statistics(strategy='RSI+MACD')
```

#### ExcelLogger
Excel export for professional reports:

```python
from logger import ExcelLogger

excel = ExcelLogger()

# Log trade to Excel
excel.log_trade({...})

# Add summary sheet
excel.add_summary_sheet({
    'Total Trades': 50,
    'Win Rate': 0.60,
    'Total P&L': 5000
})
```

#### AccountantAgent
Coordinates logging and financial calculations:

```python
from logger import AccountantAgent

accountant = AccountantAgent()

# Calculate financials
financials = accountant.calculate_trade_financials(
    entry_price=2000000,
    exit_price=2100000,
    quantity=0.1,
    side='BUY'
)

# Log completed trade
accountant.log_completed_trade({
    'strategy_name': 'RSI+MACD',
    'pair': 'BTC-INR',
    'side': 'BUY',
    'entry_price': 2000000,
    'exit_price': 2100000,
    'quantity': 0.1,
    'entry_time': '2026-03-31T12:00:00',
    'exit_time': '2026-03-31T13:00:00'
})
```

### Monitor Module (`monitor/`)

#### TelegramMonitor
Sends alerts via Telegram:

```python
from monitor import TelegramMonitor

telegram = TelegramMonitor()

# Send trade alert
telegram.send_trade_alert({
    'strategy_name': 'RSI+MACD',
    'pair': 'BTC-INR',
    'side': 'BUY',
    'entry_price': 2000000,
    'quantity': 0.1
})

# Send loss alert
telegram.send_loss_alert({
    'type': 'Trade Loss',
    'pair': 'BTC-INR',
    'loss_amount': -2000,
    'loss_percent': 2.5,
    'severity': 'HIGH'
})

# Send daily summary
telegram.send_daily_summary({
    'total_trades': 50,
    'winning_trades': 30,
    'losing_trades': 20,
    'win_rate': 0.60,
    'daily_pnl': 5000,
    'cumulative_pnl': 25000
})
```

#### MonitorAgent
System monitoring and alert coordination:

```python
from monitor import MonitorAgent

monitor = MonitorAgent()

# Check trade loss
monitor.check_trade_loss(trade_pnl=-2500, trade_pair='BTC-INR')

# Check drawdown
monitor.check_drawdown(current_value=95000, peak_value=100000)

# Send error alert
monitor.check_system_error('StrategyAgent', 'Connection timeout')
```

### Researcher Module (`researcher/`)

#### BacktestEngine
Backtests strategies on historical data:

```python
from researcher import BacktestEngine
from core import MarketDataManager

market_data = MarketDataManager()
backtest = BacktestEngine(market_data)

# Backtest strategy
results = backtest.backtest_strategy(
    pair='BTC-INR',
    strategy_func=my_strategy_function,
    days=30,
    initial_capital=100000
)

# Compare strategies
comparison = backtest.compare_strategies(
    pair='BTC-INR',
    strategies={
        'RSI+MACD': rsi_macd_func,
        'Bollinger': bollinger_func
    },
    days=30
)
```

#### ResearcherAgent
Market analysis and recommendations:

```python
from researcher import ResearcherAgent

researcher = ResearcherAgent(market_data)

# Analyze market
analysis = researcher.analyze_market_regime('BTC-INR')

# Generate report
report = researcher.generate_market_report()

# Get recommendations
recommendations = report['recommendations']
```

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| COINDCX_API_KEY | CoinDCX API key | `ec90cdd0...` |
| COINDCX_API_SECRET | CoinDCX API secret | `539bd5a2...` |
| TELEGRAM_BOT_TOKEN | Telegram bot token | `8718334360:AAG2...` |
| TELEGRAM_CHAT_ID | Telegram chat ID | `6248714124` |
| INITIAL_PORTFOLIO | Starting capital (INR) | `100000` |
| PAPER_TRADING_MODE | Enable paper trading | `true` |
| RISK_PER_TRADE | Max risk per trade | `0.02` (2%) |
| MAX_PORTFOLIO_EXPOSURE | Max exposure per pair | `0.10` (10%) |
| STOP_LOSS_PERCENT | Stop loss percentage | `0.03` (3%) |
| DAILY_MAX_LOSS_PERCENT | Daily loss limit | `0.05` (5%) |

### Strategy Configuration

Modify strategy parameters in agent files:

```python
# In agents/rsi_macd_agent.py
self.rsi_period = 14
self.rsi_overbought = 70
self.rsi_oversold = 30
self.macd_fast = 12
self.macd_slow = 26
self.macd_signal = 9
```

## API Reference

### Main Orchestrator

```python
from main import TradingOrchestrator

orchestrator = TradingOrchestrator()

# Start system
orchestrator.start()

# Get status
status = orchestrator.get_status()

# Stop system
orchestrator.stop()
```

### Dashboard

Access at `http://localhost:8501` after running:
```bash
streamlit run dashboard/app.py
```

## Deployment

### Laptop Deployment

1. Follow setup.sh
2. Run: `python main.py`
3. Dashboard: `streamlit run dashboard/app.py`

### Termux Deployment

1. Follow TERMUX_SETUP.md
2. Run lightweight version: `python termux_main.py`
3. Keep running with tmux or Termux:Boot

### Production Deployment

For production use:
1. Use real API keys (not test keys)
2. Set PAPER_TRADING_MODE=false
3. Implement additional monitoring
4. Set up automated backups
5. Use SSL for API connections

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| CoinDCX connection failed | Check API keys and internet |
| Telegram not responding | Verify bot token and chat ID |
| Database locked | Delete `data/trades.db-journal` |
| Low memory on Termux | Use lightweight mode, reduce pairs |

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Tuning

### Optimize for Speed
- Reduce number of pairs (3-5)
- Increase analysis interval (2-4 hours)
- Use SQLite only (disable Excel)
- Reduce historical data window

### Optimize for Accuracy
- Increase data window (50-100 candles)
- Use multiple timeframes
- Implement ensemble strategies
- Add more indicators

### Resource Management
- Monitor CPU: `top`
- Monitor memory: `free -h`
- Monitor disk: `df -h`
- Monitor network: `nethogs`

---

**For more help, check README.md or QUICKSTART.md**
