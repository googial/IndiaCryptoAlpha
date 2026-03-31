# IndiaCryptoAlpha - Quick Start Guide

Get up and running in 5 minutes!

## 1️⃣ Prerequisites

- Python 3.8+
- CoinDCX API keys
- Telegram bot token
- Internet connection

## 2️⃣ Installation (Laptop)

```bash
# Navigate to project
cd ~/IndiaCryptoAlpha

# Run setup
chmod +x setup.sh
./setup.sh

# Activate environment
source venv/bin/activate
```

## 3️⃣ Configuration

Edit `.env` file with your credentials:

```env
COINDCX_API_KEY=your_key_here
COINDCX_API_SECRET=your_secret_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 4️⃣ Start System

**Terminal 1 - Trading System:**
```bash
source venv/bin/activate
python main.py
```

**Terminal 2 - Dashboard:**
```bash
source venv/bin/activate
streamlit run dashboard/app.py
```

## 5️⃣ Access Dashboard

Open browser: `http://localhost:8501`

## 📱 Termux Setup

```bash
# Install packages
pkg install python git

# Clone project
git clone <url> IndiaCryptoAlpha
cd IndiaCryptoAlpha

# Setup
bash setup.sh
source venv/bin/activate

# Start (lightweight mode)
python main.py
```

## 🎯 What Happens Next

1. System initializes all agents
2. Agents analyze trading pairs hourly
3. Trades are executed based on signals
4. Results logged to SQLite + Excel
5. Telegram alerts sent on important events
6. Dashboard updates in real-time

## ✅ Verify Setup

```bash
# Check database
ls -lh data/trades.db

# Check logs
tail -20 logs/trading_system.log

# Check Excel
ls -lh data/trades_log.xlsx
```

## 🚨 Common Issues

**"ModuleNotFoundError"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"CoinDCX connection failed"**
- Verify API keys in `.env`
- Check internet connection
- Test: `python -c "from core import MarketDataManager; MarketDataManager()"`

**"Telegram bot not responding"**
- Verify token format
- Check chat ID
- Test: `python -c "from monitor import TelegramMonitor; TelegramMonitor().test_connection()"`

## 📊 Dashboard Pages

| Page | Purpose |
|------|---------|
| Overview | Key metrics and statistics |
| Live Trades | Open positions |
| Agent Leaderboard | Strategy performance |
| P&L Charts | Profit/loss visualization |
| Researcher | Market analysis |
| Risk Dashboard | Risk metrics and alerts |

## 🎮 Controls

- **Stop System**: Press `Ctrl+C` in terminal
- **View Logs**: `tail -f logs/trading_system.log`
- **Reset Database**: Delete `data/trades.db`
- **Export Trades**: Check `data/trades_log.xlsx`

## 📈 Next Steps

1. Monitor first few trades
2. Review performance in dashboard
3. Adjust risk parameters if needed
4. Add more strategies
5. Backtest on historical data

## 🔗 Resources

- Full Documentation: See `README.md`
- API Docs: https://docs.coindcx.com/
- Telegram Bot: @BotFather

## 💡 Tips

- Start with small portfolio (₹10,000)
- Monitor first 24 hours
- Review daily summaries
- Adjust strategies based on performance
- Never trade with real money until confident

---

**Ready to trade? Start the system now!** 🚀
