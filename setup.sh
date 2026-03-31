#!/bin/bash

# IndiaCryptoAlpha Setup Script
# This script sets up the trading system for both laptop and Termux environments

set -e

echo "================================"
echo "IndiaCryptoAlpha Setup"
echo "================================"
echo ""

# Detect environment
if [ -d "$PREFIX" ]; then
    echo "✓ Detected Termux environment"
    IS_TERMUX=true
else
    echo "✓ Detected Linux/Windows environment"
    IS_TERMUX=false
fi

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ "$IS_TERMUX" = true ]; then
    python -m venv venv
else
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory
echo "Creating data directory..."
mkdir -p data logs

# Initialize database
echo ""
echo "Initializing database..."
python -c "from logger import TradeDatabase; db = TradeDatabase(); db.close(); print('✓ Database initialized')"

# Create Excel log
echo "Initializing Excel log..."
python -c "from logger import ExcelLogger; excel = ExcelLogger(); excel.close(); print('✓ Excel log initialized')"

echo ""
echo "================================"
echo "✓ Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start trading system: python main.py"
echo "3. Start dashboard (new terminal): streamlit run dashboard/app.py"
echo ""
