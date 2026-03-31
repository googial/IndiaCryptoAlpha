#!/usr/bin/env python3
"""Installation verification script for IndiaCryptoAlpha."""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("✓ Python version is compatible (3.10+)")
        return True
    else:
        print("✗ Python 3.10+ required")
        return False

def check_packages():
    """Check if all required packages are installed."""
    print_header("Package Installation Check")
    
    required_packages = {
        'dotenv': 'python-dotenv',
        'ccxt': 'ccxt',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'telegram': 'python-telegram-bot',
        'streamlit': 'streamlit',
        'plotly': 'plotly',
        'openpyxl': 'openpyxl',
        'ta': 'ta',
        'sklearn': 'scikit-learn',
        'apscheduler': 'APScheduler',
        'sqlalchemy': 'SQLAlchemy',
        'pytz': 'pytz',
    }
    
    all_installed = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_project_files():
    """Check if all critical project files exist."""
    print_header("Project Files Check")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'setup.sh',
        '.env',
        'config/__init__.py',
        'core/__init__.py',
        'core/market_data.py',
        'core/risk_engine.py',
        'core/order_execution.py',
        'agents/__init__.py',
        'agents/base_agent.py',
        'agents/rsi_macd_agent.py',
        'agents/bollinger_volume_agent.py',
        'agents/ema_supertrend_agent.py',
        'logger/__init__.py',
        'logger/database.py',
        'logger/excel_logger.py',
        'logger/accountant_agent.py',
        'monitor/__init__.py',
        'monitor/telegram_monitor.py',
        'monitor/monitor_agent.py',
        'researcher/__init__.py',
        'researcher/backtest_engine.py',
        'researcher/researcher_agent.py',
        'dashboard/__init__.py',
        'dashboard/app.py',
        'README.md',
        'QUICKSTART.md',
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ MISSING: {file_path}")
            all_exist = False
    
    return all_exist

def check_directories():
    """Check if required directories exist."""
    print_header("Directory Structure Check")
    
    required_dirs = ['data', 'logs', 'config', 'core', 'agents', 'logger', 'monitor', 'researcher', 'dashboard']
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ MISSING: {dir_path}/")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test critical imports."""
    print_header("Import Test")
    
    test_imports_list = [
        ('config', 'Configuration module'),
        ('core', 'Core module'),
        ('agents', 'Agents module'),
        ('logger', 'Logger module'),
        ('monitor', 'Monitor module'),
        ('researcher', 'Researcher module'),
    ]
    
    all_ok = True
    for module_name, description in test_imports_list:
        try:
            __import__(module_name)
            print(f"✓ {description} ({module_name})")
        except Exception as e:
            print(f"✗ {description} ({module_name}): {e}")
            all_ok = False
    
    return all_ok

def test_database():
    """Test database initialization."""
    print_header("Database Test")
    
    try:
        from logger import TradeDatabase
        db = TradeDatabase()
        db.close()
        print("✓ SQLite database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_market_data():
    """Test market data connection."""
    print_header("Market Data Connection Test")
    
    try:
        from core import MarketDataManager
        manager = MarketDataManager()
        print("✓ Market data manager initialized")
        
        # Try to get a ticker
        try:
            ticker = manager.get_ticker('BTC-INR')
            if ticker:
                print(f"✓ Successfully fetched BTC-INR ticker: ₹{ticker.get('last', 'N/A')}")
                return True
            else:
                print("⚠ Ticker returned empty (API may be rate limited)")
                return True
        except Exception as e:
            print(f"⚠ Could not fetch ticker (may be rate limited): {e}")
            return True
    except Exception as e:
        print(f"✗ Market data connection failed: {e}")
        return False

def test_telegram():
    """Test Telegram connection."""
    print_header("Telegram Connection Test")
    
    try:
        from monitor import TelegramMonitor
        telegram = TelegramMonitor()
        result = telegram.test_connection()
        if result:
            print("✓ Telegram bot connected successfully")
            return True
        else:
            print("✗ Telegram bot connection failed (check token and chat ID)")
            return False
    except Exception as e:
        print(f"✗ Telegram test failed: {e}")
        return False

def test_streamlit():
    """Test Streamlit installation."""
    print_header("Streamlit Test")
    
    try:
        import streamlit
        print(f"✓ Streamlit {streamlit.__version__} installed")
        return True
    except Exception as e:
        print(f"✗ Streamlit test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  IndiaCryptoAlpha - Installation Verification".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {
        'Python Version': check_python_version(),
        'Project Files': check_project_files(),
        'Directories': check_directories(),
        'Packages': check_packages(),
        'Imports': test_imports(),
        'Database': test_database(),
        'Market Data': test_market_data(),
        'Telegram': test_telegram(),
        'Streamlit': test_streamlit(),
    }
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("  ✓ ALL TESTS PASSED - SYSTEM READY FOR USE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Read QUICKSTART.md for quick reference")
        print("2. Run: python main.py")
        print("3. In another terminal: streamlit run dashboard/app.py")
        print("4. Access dashboard at: http://localhost:8501")
        return 0
    else:
        print("\n" + "=" * 60)
        print("  ✗ SOME TESTS FAILED - PLEASE FIX ISSUES ABOVE")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Check that all packages are installed: pip install -r requirements.txt")
        print("2. Verify .env file has correct API credentials")
        print("3. Check internet connection")
        print("4. Review error messages above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
