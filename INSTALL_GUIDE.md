# IndiaCryptoAlpha - Complete Installation Guide

This guide covers installation on Windows, Linux, and Termux (Android).

## Table of Contents

1. [Windows Installation](#windows-installation)
2. [Linux Installation](#linux-installation)
3. [Termux (Android) Installation](#termux-android-installation)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Windows Installation

### Prerequisites

- Windows 10/11 (64-bit)
- Python 3.10+ from https://www.python.org/downloads/
- **During installation, check "Add Python to PATH"**
- Administrator access (optional, for some packages)

### Step-by-Step

#### 1. Extract Project

```
Extract IndiaCryptoAlpha.zip to: C:\Users\YourName\IndiaCryptoAlpha
```

#### 2. Open Command Prompt

```
Win+R → type "cmd" → Enter
```

#### 3. Navigate to Project

```cmd
cd C:\Users\YourName\IndiaCryptoAlpha
```

#### 4. Create Virtual Environment

```cmd
python -m venv venv
```

#### 5. Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

#### 6. Upgrade pip

```cmd
python -m pip install --upgrade pip setuptools wheel
```

#### 7. Install Dependencies

```cmd
pip install -r requirements.txt
```

**Wait 5-10 minutes for installation to complete.**

#### 8. Configure API Keys

```cmd
notepad .env
```

Edit these lines with your credentials:
```
COINDCX_API_KEY=your_key_here
COINDCX_API_SECRET=your_secret_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Save: `Ctrl+S` → Close

#### 9. Verify Installation

```cmd
python verify_install.py
```

You should see all tests pass with ✓ marks.

#### 10. Run System

**Terminal 1:**
```cmd
venv\Scripts\activate
python main.py
```

**Terminal 2 (new Command Prompt):**
```cmd
cd C:\Users\YourName\IndiaCryptoAlpha
venv\Scripts\activate
streamlit run dashboard/app.py
```

Open browser: `http://localhost:8501`

---

## Linux Installation

### Prerequisites

- Python 3.10+
- pip and venv
- git (optional)

### Step-by-Step

#### 1. Extract Project

```bash
unzip IndiaCryptoAlpha.zip
cd IndiaCryptoAlpha
```

Or clone:
```bash
git clone <repository-url> IndiaCryptoAlpha
cd IndiaCryptoAlpha
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

#### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

#### 4. Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

#### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 6. Configure API Keys

```bash
nano .env
```

Edit credentials, then save: `Ctrl+X` → `Y` → `Enter`

#### 7. Verify Installation

```bash
python verify_install.py
```

#### 8. Run System

**Terminal 1:**
```bash
source venv/bin/activate
python main.py
```

**Terminal 2:**
```bash
source venv/bin/activate
streamlit run dashboard/app.py
```

Open browser: `http://localhost:8501`

---

## Termux (Android) Installation

### Prerequisites

- Termux app from F-Droid (https://f-droid.org/packages/com.termux/)
- Android 7.0+
- 1GB free storage
- Stable internet

### Step-by-Step

#### 1. Install Termux

Download from F-Droid and install.

#### 2. Update Packages

```bash
pkg update && pkg upgrade
```

Press `y` when prompted.

#### 3. Install Python

```bash
pkg install python git
```

Press `y` when prompted.

#### 4. Verify Python

```bash
python --version
```

Should show Python 3.10+

#### 5. Clone Project

```bash
cd ~
git clone <repository-url> IndiaCryptoAlpha
cd IndiaCryptoAlpha
```

Or extract if you have the zip:
```bash
unzip IndiaCryptoAlpha.zip
cd IndiaCryptoAlpha
```

#### 6. Create Virtual Environment

```bash
python -m venv venv
```

#### 7. Activate Virtual Environment

```bash
source venv/bin/activate
```

#### 8. Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

#### 9. Install Dependencies

```bash
pip install -r requirements.txt
```

**This may take 15-20 minutes on first run.**

#### 10. Configure API Keys

```bash
nano .env
```

Edit credentials, save: `Ctrl+X` → `Y` → `Enter`

#### 11. Verify Installation

```bash
python verify_install.py
```

#### 12. Run System

**Lightweight Mode (Recommended for Termux):**

```bash
source venv/bin/activate
python main.py
```

**Keep Running in Background:**

Use tmux:
```bash
pkg install tmux
tmux new-session -d -s trading -c ~/IndiaCryptoAlpha
tmux send-keys -t trading "source venv/bin/activate && python main.py" Enter
```

View logs:
```bash
tmux attach-session -t trading
```

Detach (keep running):
```
Ctrl+B then D
```

#### 13. Dashboard on Termux

Streamlit is resource-intensive. Options:

**Option A: CLI Dashboard**
```bash
python -c "from logger import TradeDatabase; db = TradeDatabase(); stats = db.get_statistics(); print(f\"Total Trades: {stats.get('total_trades', 0)}\"); print(f\"Win Rate: {stats.get('win_rate', 0)*100:.2f}%\")"
```

**Option B: Streamlit (if device has enough RAM)**
```bash
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

Access from another device on same network:
```
http://your_phone_ip:8501
```

---

## Verification

### Quick Verification

```bash
python verify_install.py
```

All tests should pass with ✓ marks.

### Manual Verification

**Test Python packages:**
```bash
python -c "import ccxt, pandas, streamlit; print('✓ All packages installed')"
```

**Test database:**
```bash
python -c "from logger import TradeDatabase; db = TradeDatabase(); db.close(); print('✓ Database ready')"
```

**Test market data:**
```bash
python -c "from core import MarketDataManager; m = MarketDataManager(); print('✓ CoinDCX connected')"
```

**Test Telegram:**
```bash
python -c "from monitor import TelegramMonitor; t = TelegramMonitor(); t.test_connection()"
```

---

## Troubleshooting

### "Python not found"

**Windows:**
- Reinstall Python from https://www.python.org/downloads/
- **Check "Add Python to PATH" during installation**
- Restart Command Prompt

**Linux/Termux:**
```bash
which python3
python3 --version
```

### "venv not found"

**Windows:**
```cmd
python -m venv venv
```

**Linux/Termux:**
```bash
python3 -m venv venv
```

### "ModuleNotFoundError: No module named 'ccxt'"

```bash
# Activate venv first
source venv/bin/activate  # Linux/Termux
venv\Scripts\activate     # Windows

# Reinstall
pip install --upgrade -r requirements.txt
```

### "CoinDCX connection failed"

1. Check `.env` file has correct API keys
2. Test internet: `ping google.com`
3. Check CoinDCX API status
4. Try: `python -c "from core import MarketDataManager; MarketDataManager()"`

### "Telegram bot not responding"

1. Verify bot token in `.env`
2. Verify chat ID in `.env`
3. Test: `python -c "from monitor import TelegramMonitor; TelegramMonitor().test_connection()"`

### "Port 8501 already in use"

```bash
streamlit run dashboard/app.py --server.port 8502
```

Then access: `http://localhost:8502`

### "Permission denied" on Linux/Termux

```bash
chmod +x setup.sh
chmod +x verify_install.py
```

### Low Memory on Termux

1. Close other apps
2. Use lightweight mode (no Streamlit)
3. Reduce number of pairs to 2-3
4. Disable Excel logging

---

## Next Steps

1. Read `QUICKSTART.md` for quick reference
2. Read `README.md` for complete documentation
3. Check `DOCUMENTATION.md` for API reference
4. Review `DELIVERY_SUMMARY.md` for system overview

---

## Support

For issues:
1. Check `logs/trading_system.log`
2. Review `.env` configuration
3. Run `python verify_install.py`
4. Consult troubleshooting section above

---

**Status**: ✅ Ready for Production Use
**Version**: 1.0.0
**Last Updated**: March 31, 2026
