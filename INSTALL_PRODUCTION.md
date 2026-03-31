# IndiaCryptoAlpha - Production Installation Guide

**Status**: Production-Ready | **Python**: 3.11+ Required | **Updated**: March 31, 2026

---

## ⚡ Quick Start (All Platforms)

```bash
# 1. Clone repository
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha

# 2. Run automated setup (handles everything)
bash setup.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start trading system
python main.py

# 5. Start dashboard (new terminal)
streamlit run dashboard/app.py

# 6. Open browser
# http://localhost:8501
```

**That's it!** The setup script handles all platform-specific requirements automatically.

---

## 🔍 System Requirements

### Minimum
- **Python 3.11 or higher** (3.10 and below NOT supported)
- **2GB RAM**
- **500MB free disk space**
- **Internet connection**

### Supported Platforms
- ✅ **Termux (Android 7.0+)** - Full support with ARM wheels
- ✅ **Linux (Ubuntu, Debian, etc.)** - Full support
- ✅ **macOS (Intel & Apple Silicon)** - Full support
- ✅ **Windows 10/11** - Full support (via Git Bash or WSL2)

### Python Version Check

```bash
python3 --version
# Should output: Python 3.11.x or higher
```

If you have Python 3.10 or lower:
- **Ubuntu/Debian**: `sudo apt-get install python3.11`
- **macOS**: `brew install python@3.11`
- **Termux**: `pkg install python` (installs latest)
- **Windows**: Download from https://www.python.org/downloads/

---

## 📋 What the Setup Script Does

The `setup.sh` script is production-hardened and handles:

1. ✅ **Platform Detection** - Detects Termux, Linux, macOS, Windows
2. ✅ **Python Version Enforcement** - Requires Python 3.11+
3. ✅ **System Packages** - Installs required build tools automatically
4. ✅ **Virtual Environment** - Creates isolated Python environment
5. ✅ **Pip Upgrade** - Ensures latest pip, setuptools, wheel
6. ✅ **Dependency Installation** - Installs all packages with error handling
7. ✅ **Directory Setup** - Creates data/ and logs/ directories
8. ✅ **Database Init** - Initializes SQLite database
9. ✅ **Excel Log Init** - Initializes Excel logging
10. ✅ **Verification** - Tests critical imports

---

## 🚀 Installation by Platform

### Termux (Android)

```bash
# 1. Install Termux from F-Droid
# https://f-droid.org/packages/com.termux/

# 2. Open Termux and run
pkg update && pkg upgrade

# 3. Clone and setup
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha
bash setup.sh

# 4. Activate and run
source venv/bin/activate
python main.py
```

**Note**: Termux uses pre-built ARM wheels for all packages. No compilation needed.

### Linux (Ubuntu/Debian)

```bash
# 1. Ensure Python 3.11+ is installed
python3 --version

# 2. If not, install
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev

# 3. Clone and setup
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha
bash setup.sh

# 4. Activate and run
source venv/bin/activate
python main.py
```

### Linux (Fedora/RHEL)

```bash
# 1. Install Python 3.11
sudo dnf install python3.11 python3.11-devel

# 2. Clone and setup
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha
bash setup.sh

# 3. Activate and run
source venv/bin/activate
python main.py
```

### macOS

```bash
# 1. Install Python 3.11 (if not already installed)
brew install python@3.11

# 2. Clone and setup
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha
bash setup.sh

# 3. Activate and run
source venv/bin/activate
python main.py
```

### Windows (Git Bash)

```bash
# 1. Install Python 3.11 from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH"

# 2. Install Git Bash from https://git-scm.com/download/win

# 3. Open Git Bash and run
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha
bash setup.sh

# 4. Activate and run
source venv/bin/activate
python main.py
```

### Windows (Command Prompt)

```cmd
# 1. Install Python 3.11 from https://www.python.org/downloads/

# 2. Open Command Prompt and run
git clone https://github.com/googial/IndiaCryptoAlpha.git
cd IndiaCryptoAlpha
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 🔧 Troubleshooting

### "Python not found"

**Linux/macOS/Termux**:
```bash
# Check if Python 3.11 is installed
python3.11 --version

# If not, install it
# Ubuntu: sudo apt-get install python3.11
# macOS: brew install python@3.11
# Termux: pkg install python
```

**Windows**:
- Download Python 3.11 from https://www.python.org/downloads/
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Restart Command Prompt after installation

### "Python version too old (3.10 or lower)"

The setup script will exit with an error. You need Python 3.11+.

**Fix**:
```bash
# Ubuntu
sudo apt-get install python3.11

# macOS
brew install python@3.11

# Termux
pkg install python

# Windows
Download from https://www.python.org/downloads/
```

### "ModuleNotFoundError: No module named 'ccxt'"

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### "CoinDCX connection failed"

1. Check `.env` file has correct API keys
2. Check internet connection: `ping google.com`
3. Check CoinDCX API status
4. Test: `python -c "from core import MarketDataManager; MarketDataManager()"`

### "Telegram bot not responding"

1. Verify bot token in `.env`
2. Verify chat ID in `.env`
3. Test: `python -c "from monitor import TelegramMonitor; TelegramMonitor().test_connection()"`

### "Port 8501 already in use"

```bash
streamlit run dashboard/app.py --server.port 8502
# Then access: http://localhost:8502
```

### "Permission denied" on Linux/Termux

```bash
chmod +x setup.sh
bash setup.sh
```

### Setup script fails on Termux

```bash
# Try with explicit Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📦 Dependency Versions (Locked)

All dependencies are pinned to specific versions for reproducibility:

```
python-dotenv==1.0.0
ccxt==4.0.96
requests==2.31.0
python-telegram-bot==20.7
numpy==1.26.4
pandas==2.1.4
openpyxl==3.1.5
ta==0.10.2
scipy==1.11.4
scikit-learn==1.3.2
streamlit==1.31.1
plotly==5.18.0
APScheduler==3.10.4
SQLAlchemy==2.0.23
pytz==2023.3
```

**All packages have pre-built wheels for:**
- x86_64 (Intel/AMD)
- ARM (Termux, Raspberry Pi)
- Apple Silicon (M1/M2/M3)

**No compilation required on any platform.**

---

## ✅ Verification

After setup, verify everything works:

```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python -c "import ccxt, pandas, streamlit; print('✓ All packages installed')"

# Test database
python -c "from logger import TradeDatabase; db = TradeDatabase(); db.close(); print('✓ Database ready')"

# Test market data
python -c "from core import MarketDataManager; m = MarketDataManager(); print('✓ CoinDCX connected')"

# Test Telegram
python -c "from monitor import TelegramMonitor; t = TelegramMonitor(); t.test_connection()"
```

All should show ✓ (checkmark).

---

## 🚀 Running the System

### Terminal 1: Trading System

```bash
source venv/bin/activate
python main.py
```

You should see:
```
[INFO] 🚀 IndiaCryptoAlpha Trading System Starting
[INFO] ✓ Trading Orchestrator initialized successfully
```

### Terminal 2: Dashboard

```bash
source venv/bin/activate
streamlit run dashboard/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Terminal 3: Monitor Logs (Optional)

```bash
tail -f logs/trading_system.log
```

---

## 🔐 Configuration

Edit `.env` file with your credentials:

```bash
nano .env
```

Required variables:
```
COINDCX_API_KEY=your_key
COINDCX_API_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Market Data (CoinDCX API)             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Strategy Agents (3 implemented)            │
│  - RSI+MACD Momentum                                   │
│  - Bollinger Band + Volume                             │
│  - EMA Crossover + Supertrend                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Risk Engine                          │
│  - Trade validation                                    │
│  - P&L calculation                                     │
│  - Risk limit enforcement                              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                Order Execution (Simulated)              │
│  - Paper trading                                       │
│  - Slippage modeling                                   │
│  - Fill rate tracking                                  │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────────┐          ┌──────────▼────────┐
│  Logging         │          │  Monitoring       │
│  - SQLite        │          │  - Telegram       │
│  - Excel         │          │  - Alerts         │
│  - Tax Calc      │          │  - Health Check   │
└──────────────────┘          └───────────────────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │      Dashboard (Streamlit)      │
        │  - Overview                     │
        │  - Live Trades                  │
        │  - Leaderboard                  │
        │  - P&L Charts                   │
        │  - Risk Metrics                 │
        └─────────────────────────────────┘
```

---

## 🎯 Next Steps

1. **Read documentation**: `README.md`, `QUICKSTART.md`, `DOCUMENTATION.md`
2. **Configure API keys**: Edit `.env` file
3. **Run setup**: `bash setup.sh`
4. **Start system**: `python main.py`
5. **Open dashboard**: `http://localhost:8501`
6. **Monitor Telegram**: Check for alerts

---

## 📞 Support

For issues:
1. Check logs: `tail -f logs/trading_system.log`
2. Review `.env` configuration
3. Test individual components
4. Consult troubleshooting section above

---

## ✨ Features

✅ **3 Strategy Agents** (extensible to 6+)
✅ **Risk Management** (2% per trade, 10% exposure, 5% daily limit)
✅ **Paper Trading** (100% simulated, no real capital risk)
✅ **Telegram Alerts** (real-time notifications)
✅ **SQLite + Excel** (dual logging with tax calculations)
✅ **Streamlit Dashboard** (6 interactive pages)
✅ **Backtesting** (historical strategy analysis)
✅ **Hybrid Deployment** (Windows, Linux, Termux)
✅ **Production-Ready** (comprehensive error handling)

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: March 31, 2026
