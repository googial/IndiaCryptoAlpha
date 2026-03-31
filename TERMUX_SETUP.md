# IndiaCryptoAlpha - Termux Setup Guide

Complete guide to running IndiaCryptoAlpha on Android via Termux.

## 📱 Prerequisites

- **Device**: Android 7.0+
- **Storage**: 1GB free space
- **RAM**: 2GB minimum
- **Internet**: Stable connection

## 1️⃣ Install Termux

1. Download Termux from [F-Droid](https://f-droid.org/en/packages/com.termux/) or [Google Play](https://play.google.com/store/apps/details?id=com.termux)
2. Install and open Termux
3. Grant storage permissions when prompted

## 2️⃣ Install Dependencies

```bash
# Update package manager
pkg update && pkg upgrade

# Install Python and Git
pkg install python git

# Install build tools (required for some packages)
pkg install build-essential clang

# Verify Python version
python --version  # Should be 3.8+
```

## 3️⃣ Clone Project

```bash
# Navigate to home directory
cd ~

# Clone the project (replace with actual URL)
git clone https://github.com/yourusername/IndiaCryptoAlpha.git

# Navigate to project
cd IndiaCryptoAlpha
```

## 4️⃣ Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

**Note**: This may take 10-15 minutes on first run.

## 5️⃣ Configure API Keys

```bash
# Edit .env file
nano .env
```

Add your credentials:
```env
COINDCX_API_KEY=your_key
COINDCX_API_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

Save: `Ctrl+X` → `Y` → `Enter`

## 6️⃣ Initialize System

```bash
# Create data directories
mkdir -p data logs

# Initialize database
python -c "from logger import TradeDatabase; db = TradeDatabase(); db.close(); print('✓ Database ready')"

# Test API connection
python -c "from core import MarketDataManager; m = MarketDataManager(); print('✓ CoinDCX connected')"

# Test Telegram
python -c "from monitor import TelegramMonitor; t = TelegramMonitor(); t.test_connection()"
```

## 🚀 Running on Termux

### Lightweight Mode (Recommended for Termux)

Create `termux_main.py`:

```python
#!/usr/bin/env python3
"""Lightweight trading system for Termux."""

import logging
import sys
from datetime import datetime
from config import INITIAL_PORTFOLIO, PAPER_TRADING_MODE
from core import MarketDataManager, RiskEngine, OrderExecutor
from agents import RSIMACDAgent, BollingerVolumeAgent
from logger import AccountantAgent
from monitor import MonitorAgent

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 IndiaCryptoAlpha Termux Edition")
    logger.info(f"Mode: {'PAPER' if PAPER_TRADING_MODE else 'LIVE'}")
    
    # Initialize components
    market_data = MarketDataManager()
    risk_engine = RiskEngine(INITIAL_PORTFOLIO)
    order_executor = OrderExecutor()
    
    # Initialize agents (2 only for Termux)
    agents = [
        RSIMACDAgent(['BTC-INR'], risk_engine, order_executor, market_data),
        BollingerVolumeAgent(['ETH-INR'], risk_engine, order_executor, market_data),
    ]
    
    accountant = AccountantAgent()
    monitor = MonitorAgent()
    
    logger.info("✓ System initialized")
    logger.info("Running strategy analysis every hour...")
    
    # Simple loop (no scheduler for Termux)
    import time
    iteration = 0
    
    try:
        while True:
            iteration += 1
            logger.info(f"\n=== Cycle {iteration} ===")
            
            for agent in agents:
                for pair in ['BTC-INR', 'ETH-INR']:
                    signal = agent.analyze(pair)
                    if signal:
                        logger.info(f"Signal: {agent.name} → {signal}")
            
            # Wait 1 hour
            logger.info("Waiting 1 hour until next cycle...")
            time.sleep(3600)
            
    except KeyboardInterrupt:
        logger.info("\n✓ System stopped")
        accountant.close()

if __name__ == '__main__':
    main()
```

Run it:
```bash
python termux_main.py
```

### Full Mode (If device has enough resources)

```bash
source venv/bin/activate
python main.py
```

## 📊 Dashboard on Termux

Streamlit can run on Termux but is resource-intensive. Options:

### Option 1: Access from Another Device

On Termux:
```bash
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

On another device (same network):
```
http://your_phone_ip:8501
```

### Option 2: CLI Dashboard

Create `termux_dashboard.py`:
```python
#!/usr/bin/env python3
"""CLI dashboard for Termux."""

from logger import TradeDatabase
from config import DATABASE_PATH
import os

def show_dashboard():
    db = TradeDatabase(DATABASE_PATH)
    stats = db.get_statistics()
    
    os.system('clear')
    print("=" * 50)
    print("📊 IndiaCryptoAlpha Dashboard")
    print("=" * 50)
    print(f"Total Trades: {stats.get('total_trades', 0)}")
    print(f"Win Rate: {stats.get('win_rate', 0)*100:.2f}%")
    print(f"Total P&L: ₹{stats.get('total_pnl', 0):.2f}")
    print(f"Profit Factor: {stats.get('profit_factor', 0):.2f}")
    print("=" * 50)

if __name__ == '__main__':
    while True:
        show_dashboard()
        input("Press Enter to refresh...")
```

Run:
```bash
python termux_dashboard.py
```

## 🔄 Keep Running in Background

### Option 1: Termux Session

```bash
# Start new session
termux-new-session -n trading

# List sessions
termux-list-sessions

# Attach to session
termux-session attach trading
```

### Option 2: Screen or Tmux

```bash
# Install tmux
pkg install tmux

# Create session
tmux new-session -d -s trading -c ~/IndiaCryptoAlpha

# Run system
tmux send-keys -t trading "source venv/bin/activate && python termux_main.py" Enter

# Attach to view
tmux attach-session -t trading

# Detach (keep running)
# Ctrl+B then D
```

### Option 3: Cron Job

```bash
# Edit crontab
crontab -e

# Add (runs every hour)
0 * * * * cd ~/IndiaCryptoAlpha && source venv/bin/activate && python termux_main.py >> logs/cron.log 2>&1
```

## 📁 File Locations on Termux

```
/data/data/com.termux/files/home/
├── IndiaCryptoAlpha/
│   ├── data/
│   │   ├── trades.db
│   │   └── trades_log.xlsx
│   ├── logs/
│   │   └── trading_system.log
│   └── venv/
```

## 📊 Accessing Files from PC

### Via USB
1. Connect phone to PC via USB
2. Enable "File Transfer" mode
3. Access files from `Internal Storage/IndiaCryptoAlpha/data/`

### Via SSH (if available)
```bash
# On Termux
pkg install openssh
sshd

# On PC
scp -r user@phone_ip:/data/data/com.termux/files/home/IndiaCryptoAlpha/data/ ./
```

## 🔧 Troubleshooting

### "No module named 'ccxt'"
```bash
source venv/bin/activate
pip install ccxt
```

### "Permission denied" on .sh files
```bash
chmod +x setup.sh
bash setup.sh
```

### Low memory errors
- Use lightweight mode (`termux_main.py`)
- Reduce number of pairs (2-3 only)
- Disable Excel logging
- Close other apps

### Network issues
- Check internet: `ping google.com`
- Restart Termux
- Check API rate limits

### Database locked
```bash
# Remove lock file
rm data/trades.db-journal

# Restart system
```

## 💡 Tips for Termux

1. **Battery**: Keep device plugged in while running
2. **Screen**: Use Termux:Boot app to prevent sleep
3. **Storage**: Monitor free space regularly
4. **Updates**: Keep Termux and packages updated
5. **Backup**: Regularly backup `data/` directory

## 📈 Performance Optimization

### Reduce Resource Usage
```python
# In termux_main.py, use:
- 2-3 strategy agents only
- 2-3 trading pairs only
- 1-hour analysis interval
- SQLite only (no Excel)
- Minimal logging
```

### Monitor Resources
```bash
# Check memory
free -h

# Check storage
df -h

# Check CPU
top -n 1
```

## 🚀 Advanced: Automation

### Telegram Commands

Create `telegram_bot.py` to control system via Telegram:
```python
from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("Trading system running...")

async def status(update, context):
    # Get system status
    await update.message.reply_text("Status: Active")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()

if __name__ == '__main__':
    main()
```

## 📞 Support

For Termux-specific issues:
- Check Termux wiki: https://wiki.termux.com/
- Join Termux community: https://t.me/termux
- Report issues on GitHub

---

**Happy Trading on Android!** 📱📈
