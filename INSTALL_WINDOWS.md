# IndiaCryptoAlpha - Windows Installation Guide

Complete step-by-step guide for running IndiaCryptoAlpha on Windows.

## Prerequisites

- **Windows 10/11** (64-bit recommended)
- **Python 3.10 or higher** (download from https://www.python.org/downloads/)
- **Git** (optional, for cloning: https://git-scm.com/download/win)
- **Administrator access** (for some installations)
- **Internet connection**

## Step 1: Verify Python Installation

Open **Command Prompt** (Win+R, type `cmd`, press Enter):

```cmd
python --version
pip --version
```

You should see Python 3.10+ and pip installed. If not, download from https://www.python.org/

**Important**: During Python installation, check "Add Python to PATH"

## Step 2: Extract Project

1. Download the `IndiaCryptoAlpha.zip` file
2. Extract to a folder, e.g., `C:\Users\YourName\IndiaCryptoAlpha`
3. Open Command Prompt and navigate:

```cmd
cd C:\Users\YourName\IndiaCryptoAlpha
```

## Step 3: Create Virtual Environment

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

## Step 4: Upgrade pip

```cmd
python -m pip install --upgrade pip setuptools wheel
```

## Step 5: Install Dependencies

```cmd
pip install -r requirements.txt
```

**This may take 5-10 minutes.** If you see warnings, they're usually safe to ignore.

### Troubleshooting Installation Issues

**Issue: "No module named pip"**
```cmd
python -m ensurepip --upgrade
```

**Issue: "Microsoft Visual C++ 14.0 is required"**
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++"
- Retry: `pip install -r requirements.txt`

**Issue: Specific package fails**
```cmd
# Try installing without optional packages
pip install --no-cache-dir -r requirements.txt
```

## Step 6: Configure API Keys

1. Open `.env` file with Notepad:
   ```cmd
   notepad .env
   ```

2. You should see:
   ```
   COINDCX_API_KEY=your_key_here
   COINDCX_API_SECRET=your_secret_here
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

3. **Replace** with your actual credentials (already configured if provided)

4. Save and close

## Step 7: Verify Setup

```cmd
# Test imports
python -c "import ccxt, pandas, streamlit; print('✓ All packages installed')"

# Test database
python -c "from logger import TradeDatabase; db = TradeDatabase(); db.close(); print('✓ Database ready')"

# Test API connection
python -c "from core import MarketDataManager; m = MarketDataManager(); print('✓ CoinDCX connected')"
```

All three should show ✓ (checkmark).

## Step 8: Run the System

### Terminal 1: Trading System

```cmd
# Make sure (venv) is active
venv\Scripts\activate

# Start trading system
python main.py
```

You should see:
```
[INFO] 🚀 IndiaCryptoAlpha Trading System Starting
[INFO] ✓ Trading Orchestrator initialized successfully
```

### Terminal 2: Dashboard

Open a **new Command Prompt** window:

```cmd
# Navigate to project
cd C:\Users\YourName\IndiaCryptoAlpha

# Activate venv
venv\Scripts\activate

# Start dashboard
streamlit run dashboard/app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Terminal 3: Monitor Logs (Optional)

Open a **third Command Prompt** window:

```cmd
cd C:\Users\YourName\IndiaCryptoAlpha
type logs\trading_system.log
```

Or use PowerShell to tail logs:
```powershell
Get-Content logs\trading_system.log -Wait
```

## Step 9: Access Dashboard

Open your browser and go to:
```
http://localhost:8501
```

You should see the IndiaCryptoAlpha dashboard with:
- Overview page
- Live trades
- Agent leaderboard
- P&L charts
- Risk dashboard

## Step 10: Verify Paper Trading

Check if system is executing trades:

1. Look at `main.py` output for "Trade Executed" messages
2. Check dashboard for trades in "Live Trades" page
3. Check `data/trades.db` file exists and grows in size

## Stopping the System

To stop the system:

1. In `main.py` terminal: Press `Ctrl+C`
2. In dashboard terminal: Press `Ctrl+C`
3. Close terminals

## Troubleshooting

### "venv is not recognized"

Make sure you're in the project directory:
```cmd
cd C:\Users\YourName\IndiaCryptoAlpha
venv\Scripts\activate
```

### "ModuleNotFoundError: No module named 'ccxt'"

Reinstall dependencies:
```cmd
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### "Streamlit not found"

```cmd
venv\Scripts\activate
pip install streamlit==1.31.1
```

### "CoinDCX connection failed"

1. Check `.env` file has correct API keys
2. Test internet connection: `ping google.com`
3. Check CoinDCX API status
4. Try: `python -c "from core import MarketDataManager; MarketDataManager()"`

### "Telegram bot not responding"

1. Verify bot token in `.env`
2. Verify chat ID in `.env`
3. Test: `python -c "from monitor import TelegramMonitor; TelegramMonitor().test_connection()"`

### Port 8501 already in use

If Streamlit fails with "Address already in use":
```cmd
streamlit run dashboard/app.py --server.port 8502
```

Then access: `http://localhost:8502`

## Performance Tips

1. **Keep venv activated**: Always run `venv\Scripts\activate` first
2. **Close other apps**: Frees up memory for trading system
3. **Use SSD**: Faster database operations
4. **Monitor resources**: Use Task Manager to check CPU/Memory
5. **Disable antivirus scanning** of project folder (optional)

## Uninstalling

To completely remove:

```cmd
# Deactivate venv
deactivate

# Delete project folder
rmdir /s C:\Users\YourName\IndiaCryptoAlpha
```

## Next Steps

1. Read `README.md` for complete documentation
2. Read `QUICKSTART.md` for quick reference
3. Check `DOCUMENTATION.md` for API reference
4. Review `DELIVERY_SUMMARY.md` for system overview

## Support

For issues:
1. Check `logs/trading_system.log`
2. Review `.env` configuration
3. Test individual components
4. Consult troubleshooting section above

---

**Happy Trading on Windows!** 🚀📈

**Status**: Ready for Production Use
**Version**: 1.0.0
**Last Updated**: March 31, 2026
