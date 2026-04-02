"""Configuration module for IndiaCryptoAlpha trading system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Logs directory
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# CoinDCX API Configuration
COINDCX_API_KEY = os.getenv("COINDCX_API_KEY", "")
COINDCX_API_SECRET = os.getenv("COINDCX_API_SECRET", "")
COINDCX_BASE_URL = "https://api.coindcx.com"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Trading Configuration
INITIAL_PORTFOLIO = float(os.getenv("INITIAL_PORTFOLIO", "100000"))
PAPER_TRADING_MODE = os.getenv("PAPER_TRADING_MODE", "true").lower() == "true"
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.02"))
MAX_PORTFOLIO_EXPOSURE = float(os.getenv("MAX_PORTFOLIO_EXPOSURE", "0.10"))
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "0.03"))
DAILY_MAX_LOSS_PERCENT = float(os.getenv("DAILY_MAX_LOSS_PERCENT", "0.05"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATABASE_PATH = DATA_DIR / os.getenv("DATABASE_PATH", "trades.db").split("/")[-1]
EXCEL_LOG_PATH = DATA_DIR / os.getenv("EXCEL_LOG_PATH", "trades_log.xlsx").split("/")[-1]

# Researcher Configuration
BACKTEST_DAYS = int(os.getenv("BACKTEST_DAYS", "30"))
RESEARCHER_INTERVAL_HOURS = int(os.getenv("RESEARCHER_INTERVAL_HOURS", "6"))

# Race Configuration
RACE_DURATION_HOURS = int(os.getenv("RACE_DURATION_HOURS", "24"))
NUM_RACE_AGENTS = int(os.getenv("NUM_RACE_AGENTS", "12"))
RACE_UPDATE_INTERVAL_SEC = int(os.getenv("RACE_UPDATE_INTERVAL_SEC", "10"))
EVOLUTION_INTERVAL_MIN = int(os.getenv("EVOLUTION_INTERVAL_MIN", "60"))

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, google, xai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
XAI_API_KEY = os.getenv("XAI_API_KEY", "")

# m.Stock Configuration
MSTOCK_USER_ID = os.getenv("MSTOCK_USER_ID", "")
MSTOCK_PASSWORD = os.getenv("MSTOCK_PASSWORD", "")
MSTOCK_PIN = os.getenv("MSTOCK_PIN", "")
MSTOCK_API_KEY = os.getenv("MSTOCK_API_KEY", "")
MSTOCK_API_SECRET = os.getenv("MSTOCK_API_SECRET", "")

# Monitor Configuration
MONITOR_INTERVAL_HOURS = int(os.getenv("MONITOR_INTERVAL_HOURS", "2"))

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CoinDCX Fee Tier (Public, non-VIP)
COINDCX_MAKER_FEE = 0.001  # 0.1%
COINDCX_TAKER_FEE = 0.002  # 0.2%

# India Tax Configuration
GST_RATE = 0.18  # 18% GST
INCOME_TAX_RATE = 0.30  # 30% estimated tax on profits

# Supported trading pairs
SUPPORTED_PAIRS = [
    "BTC-INR",
    "ETH-INR",
    "XRP-INR",
    "ADA-INR",
    "SOL-INR",
    "DOGE-INR",
]

# Timeframes for technical analysis
TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]

# Default timeframe for strategy analysis
DEFAULT_TIMEFRAME = "1h"

# Paper trading virtual portfolio
VIRTUAL_PORTFOLIO = {
    "cash": INITIAL_PORTFOLIO,
    "positions": {},
    "total_value": INITIAL_PORTFOLIO,
    "daily_pnl": 0.0,
    "cumulative_pnl": 0.0,
}
