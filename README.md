# IndiaCryptoAlpha - Multi-Agent Paper Trading System

A premium, production-ready multi-agent paper trading system for CoinDCX with Streamlit dashboard, Telegram alerts, and comprehensive risk management. Runs on both laptops and Android via Termux.

## 🎯 Features

### Core Trading System
- **6 Strategy Agents** (3 implemented, extensible to 6)
  - RSI + MACD Momentum
  - Bollinger Band + Volume Breakout
  - EMA Crossover + Supertrend
  
- **Paper Trading Mode** - Safe backtesting and simulation
- **Risk Engine** - Enforces strict risk parameters
- **Order Execution** - Simulated market orders with slippage

### Logging & Analytics
- **SQLite Database** - Persistent trade logging
- **Excel Export** - Professional trade reports
- **Financial Calculations** - Fees, GST, tax estimates
- **Performance Metrics** - Win rate, Sharpe ratio, drawdown

### Monitoring & Alerts
- **Telegram Integration** - Real-time alerts
- **Loss Alerts** - >2% per trade, >5% drawdown
- **Daily Summaries** - Performance reports
- **System Monitoring** - Error detection and alerts

### Dashboard
- **Streamlit UI** - Beautiful, interactive interface
- **Real-time Charts** - P&L, performance, agent comparison
- **Agent Leaderboard** - Strategy performance ranking
- **Risk Metrics** - Drawdown, exposure, daily loss tracking

### Researcher Agent
- **Backtesting Engine** - Historical strategy analysis
- **Market Regime Detection** - Bullish/bearish/sideways
- **Strategy Comparison** - Compare multiple strategies
- **Parameter Optimization** - Grid search optimization

## 📋 Requirements

### Laptop (Full System)
- Python 3.8+
- 2GB RAM minimum
- Internet connection
- CoinDCX API keys
- Telegram bot token

### Termux (Android)
- Termux app installed
- Python 3.8+
- 500MB free storage
- Same API credentials

## 🚀 Installation

### Laptop Setup

1. **Clone or download the project**
```bash
2. **Clone project**
```bash
cd ~
git clone https://github.com/googial/IndiaCryptoAlpha
cd IndiaCryptoAlpha
```
cd ~/IndiaCryptoAlpha
```

2. **Run setup script**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Activate virtual environment**
```bash
source venv/bin/activate
```

4. **Verify installation**
```bash
python -c "import ccxt, pandas, streamlit; print('✓ All dependencies installed')"
```

### Termux Setup

1. **Install Termux packages**
```bash
pkg update && pkg upgrade
pkg install python git
```

2. **Clone project**
```bash
cd ~
git clone https://github.com/googial/IndiaCryptoAlpha
cd IndiaCryptoAlpha
```

3. **Run setup**
```bash
bash setup.sh
```

4. **Activate environment**
```bash
source venv/bin/activate
```

## ⚙️ Configuration

### Environment Variables (.env)

The `.env` file contains all configuration:

```env
# CoinDCX API
COINDCX_API_KEY=your_api_key
COINDCX_API_SECRET=your_api_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Trading
INITIAL_PORTFOLIO=100000
PAPER_TRADING_MODE=true
RISK_PER_TRADE=0.02
MAX_PORTFOLIO_EXPOSURE=0.10
STOP_LOSS_PERCENT=0.03
DAILY_MAX_LOSS_PERCENT=0.05
```

### API Keys Setup

1. **CoinDCX API Keys**
   - Visit https://coindcx.com/api
   - Create API key with market data access
   - Copy key and secret to `.env`

2. **Telegram Bot**
   - Chat with @BotFather on Telegram
   - Create new bot: `/newbot`
   - Copy bot token to `.env`
   - Get your chat ID: Send message to bot, visit `https://api.telegram.org/bot<TOKEN>/getUpdates`

## 🎮 Usage

### Start Trading System

```bash
# Activate environment
source venv/bin/activate

# Start main system
python main.py
```

The system will:
- Initialize all agents
- Start scheduled tasks
- Begin monitoring and trading
- Send alerts to Telegram

### Start Dashboard

In a new terminal:

```bash
source venv/bin/activate
streamlit run dashboard/app.py
```

Access dashboard at: `http://localhost:8501`

### Dashboard Pages

1. **📊 Overview** - Key metrics and trade distribution
2. **📈 Live Trades** - Open positions and recent trades
3. **🏆 Agent Leaderboard** - Strategy performance ranking
4. **📉 P&L Charts** - Cumulative P&L and pair analysis
5. **🔬 Researcher Reports** - Market analysis and recommendations
6. **⚠️ Risk Dashboard** - Risk metrics and alerts

## 📊 Project Structure

```
IndiaCryptoAlpha/
├── config/                 # Configuration module
│   └── __init__.py        # Environment variables
├── core/                   # Core trading system
│   ├── market_data.py     # CoinDCX API integration
│   ├── risk_engine.py     # Risk management
│   ├── order_execution.py # Order simulation
│   └── __init__.py
├── agents/                 # Strategy agents
│   ├── base_agent.py      # Base class
│   ├── rsi_macd_agent.py  # RSI+MACD strategy
│   ├── bollinger_volume_agent.py  # Bollinger Band strategy
│   ├── ema_supertrend_agent.py    # EMA Crossover strategy
│   └── __init__.py
├── logger/                 # Logging and accounting
│   ├── database.py        # SQLite logging
│   ├── excel_logger.py    # Excel export
│   ├── accountant_agent.py # Financial calculations
│   └── __init__.py
├── monitor/                # Monitoring and alerts
│   ├── telegram_monitor.py # Telegram integration
│   ├── monitor_agent.py   # System monitoring
│   └── __init__.py
├── researcher/             # Research and backtesting
│   ├── backtest_engine.py # Backtesting
│   ├── researcher_agent.py # Market analysis
│   └── __init__.py
├── dashboard/              # Streamlit dashboard
│   ├── app.py            # Dashboard UI
│   └── __init__.py
├── data/                   # Data storage
│   ├── trades.db         # SQLite database
│   └── trades_log.xlsx   # Excel log
├── logs/                   # Log files
│   └── trading_system.log # System logs
├── main.py                 # Main orchestrator
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── .env                   # Configuration (create this)
└── README.md              # This file
```

## 🔄 System Architecture

### Agent Workflow

```
Market Data → Strategy Agents → Risk Engine → Order Execution
                                                      ↓
                                            Accountant Agent
                                                      ↓
                                          SQLite + Excel Logging
                                                      ↓
                                            Monitor Agent
                                                      ↓
                                          Telegram Alerts
```

### Scheduled Tasks

- **Hourly**: Strategy analysis and trade execution
- **Every 6 hours**: Researcher analysis and backtesting
- **Every 2-3 hours**: System monitoring and health checks
- **Daily (8 PM)**: Summary report and agent performance

## 📈 Trading Strategies

### 1. RSI + MACD Momentum
- **Entry**: RSI oversold (<30) + MACD bullish crossover
- **Exit**: RSI overbought (>70) + MACD bearish crossover
- **Best for**: Ranging markets with clear momentum

### 2. Bollinger Band + Volume
- **Entry**: Price breaks upper band + volume spike
- **Exit**: Price breaks lower band + volume spike
- **Best for**: Breakout trading

### 3. EMA Crossover + Supertrend
- **Entry**: EMA fast crosses above slow + Supertrend uptrend
- **Exit**: EMA fast crosses below slow + Supertrend downtrend
- **Best for**: Trend-following strategies

## ⚠️ Risk Management

### Risk Parameters
- **Max Risk Per Trade**: 2% of portfolio
- **Max Portfolio Exposure**: 10% per pair
- **Stop Loss**: 3-5% below entry
- **Daily Max Loss**: 5% → pause all trading

### Monitoring
- Real-time loss alerts (>2% per trade)
- Drawdown alerts (>5%)
- Daily loss limit enforcement
- System error notifications

## 📊 Financial Calculations

### Fees & Taxes
- **CoinDCX Fees**: 0.1% maker + 0.2% taker
- **GST**: 18% on fees
- **Income Tax**: 30% on profits (estimated)

### P&L Calculation
```
Gross P&L = (Exit Price - Entry Price) × Quantity
Fees = Entry Fee + Exit Fee
GST = Fees × 18%
Tax = max(0, Gross P&L × 30%)
Net P&L = Gross P&L - Fees - GST - Tax
```

## 🔧 Troubleshooting

### Issue: "CoinDCX connection failed"
- Check API keys in `.env`
- Verify internet connection
- Check CoinDCX API status

### Issue: "Telegram bot not responding"
- Verify bot token is correct
- Check chat ID format
- Ensure bot has permission to send messages

### Issue: "Dashboard not loading"
- Check Streamlit is running: `streamlit run dashboard/app.py`
- Verify database exists: `ls data/trades.db`
- Check logs: `tail -f logs/trading_system.log`

### Issue: "Insufficient data for backtest"
- Need at least 50 candles of historical data
- Try different trading pair
- Check CoinDCX API rate limits

## 📝 Logging

### Log Files
- `logs/trading_system.log` - Main system log
- `data/trades.db` - SQLite database
- `data/trades_log.xlsx` - Excel export

### Log Levels
- `INFO` - Normal operations
- `WARNING` - Alerts and warnings
- `ERROR` - System errors
- `DEBUG` - Detailed debugging info

## 🚀 Extending the System

### Adding New Strategy

1. Create new agent in `agents/` directory
2. Inherit from `BaseStrategyAgent`
3. Implement `generate_signal()` method
4. Add to orchestrator in `main.py`

Example:
```python
from agents import BaseStrategyAgent

class MyStrategy(BaseStrategyAgent):
    def __init__(self, pairs, risk_engine, order_executor, market_data):
        super().__init__("My Strategy", pairs, risk_engine, order_executor, market_data)
    
    def generate_signal(self, pair, data):
        # Your strategy logic here
        return signal
```

### Adding New Alert Type

1. Add method to `TelegramMonitor` class
2. Call from `MonitorAgent`
3. Configure in scheduler

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Support

For issues or questions:
1. Check logs: `tail -f logs/trading_system.log`
2. Review configuration: Check `.env` file
3. Test API connection: `python -c "from core import MarketDataManager; m = MarketDataManager()"`

## ⚡ Performance Tips

### For Laptop
- Use SSD for database
- Increase worker threads
- Enable caching for market data

### For Termux
- Use lighter strategies (fewer indicators)
- Reduce analysis frequency
- Limit number of pairs to 3-5
- Use SQLite only (no Excel)

## 📚 References

- [CoinDCX API Documentation](https://docs.coindcx.com/)
- [CCXT Library](https://github.com/ccxt/ccxt)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Built with ❤️ for Indian traders**

**Status**: Paper Trading Mode (Safe for testing)

**Last Updated**: 2026-03-31
