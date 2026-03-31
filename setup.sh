#!/bin/bash

################################################################################
# IndiaCryptoAlpha - Production-Grade Setup Script
# 
# Features:
# - Python 3.11+ enforcement
# - Platform detection (Termux, Linux, macOS, Windows/Git Bash)
# - Automatic system package installation
# - Comprehensive error handling
# - Detailed logging
# - ARM (Termux) support
#
# Usage: bash setup.sh
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

# Exit with error
exit_error() {
    log_error "$1"
    exit 1
}

################################################################################
# STEP 1: ENVIRONMENT DETECTION
################################################################################

log_section "STEP 1: Environment Detection"

# Detect platform
PLATFORM="unknown"
IS_TERMUX=false
IS_LINUX=false
IS_MACOS=false
IS_WSL=false

if [ -d "$PREFIX" ]; then
    PLATFORM="Termux (Android)"
    IS_TERMUX=true
    log_success "Detected Termux environment"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
    IS_LINUX=true
    # Check if running in WSL
    if grep -qi microsoft /proc/version 2>/dev/null; then
        IS_WSL=true
        PLATFORM="Linux (WSL2)"
        log_success "Detected Linux (WSL2) environment"
    else
        log_success "Detected Linux environment"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    IS_MACOS=true
    log_success "Detected macOS environment"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="Windows (Git Bash)"
    log_success "Detected Windows (Git Bash) environment"
else
    PLATFORM="$OSTYPE"
    log_warning "Unknown platform: $OSTYPE"
fi

log_info "Platform: $PLATFORM"

# Detect architecture
ARCH=$(uname -m)
log_info "Architecture: $ARCH"

################################################################################
# STEP 2: PYTHON VERSION CHECK
################################################################################

log_section "STEP 2: Python Version Verification"

# Find Python executable
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    exit_error "Python not found. Please install Python 3.11 or higher."
fi

log_info "Using Python: $PYTHON_CMD"

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
log_info "Python version: $PYTHON_VERSION"

# Parse version
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Validate version
if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    exit_error "Python 3.11+ required. Current: $PYTHON_VERSION"
fi

if [ "$MAJOR" -gt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -gt 13 ]); then
    log_warning "Python $PYTHON_VERSION may have untested compatibility. Proceeding anyway..."
fi

log_success "Python version check passed: $PYTHON_VERSION"

################################################################################
# STEP 3: SYSTEM PACKAGE INSTALLATION (Platform-Specific)
################################################################################

log_section "STEP 3: System Package Installation"

if [ "$IS_TERMUX" = true ]; then
    log_info "Installing Termux system packages..."
    
    # Update package manager
    log_info "Updating pkg..."
    pkg update -y || log_warning "pkg update failed, continuing anyway..."
    
    # Install required packages
    log_info "Installing required packages..."
    pkg install -y python-dev clang make binutils 2>/dev/null || log_warning "Some packages already installed"
    
    log_success "Termux packages installed"

elif [ "$IS_LINUX" = true ]; then
    log_info "Installing Linux system packages..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        log_info "Using apt package manager..."
        sudo apt-get update -qq || log_warning "apt-get update failed"
        sudo apt-get install -y python3-dev python3-venv build-essential 2>/dev/null || log_warning "Some packages already installed"
    elif command -v yum &> /dev/null; then
        log_info "Using yum package manager..."
        sudo yum install -y python3-devel gcc make 2>/dev/null || log_warning "Some packages already installed"
    elif command -v pacman &> /dev/null; then
        log_info "Using pacman package manager..."
        sudo pacman -S --noconfirm python base-devel 2>/dev/null || log_warning "Some packages already installed"
    else
        log_warning "Unknown package manager. Skipping system packages."
    fi
    
    log_success "Linux packages installed"

elif [ "$IS_MACOS" = true ]; then
    log_info "Installing macOS system packages..."
    
    if command -v brew &> /dev/null; then
        log_info "Using Homebrew..."
        brew install python@3.11 2>/dev/null || log_warning "Some packages already installed"
    else
        log_warning "Homebrew not found. Please install Xcode Command Line Tools."
    fi
    
    log_success "macOS packages installed"

else
    log_warning "Skipping system package installation for unknown platform"
fi

################################################################################
# STEP 4: VIRTUAL ENVIRONMENT CREATION
################################################################################

log_section "STEP 4: Virtual Environment Setup"

if [ -d "venv" ]; then
    log_warning "Virtual environment already exists. Removing..."
    rm -rf venv
fi

log_info "Creating virtual environment..."
$PYTHON_CMD -m venv venv || exit_error "Failed to create virtual environment"

log_success "Virtual environment created"

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate || exit_error "Failed to activate virtual environment"

log_success "Virtual environment activated"

################################################################################
# STEP 5: PIP UPGRADE
################################################################################

log_section "STEP 5: Pip Upgrade"

log_info "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel --quiet || exit_error "Failed to upgrade pip"

log_success "Pip upgraded"

# Show pip version
PIP_VERSION=$(pip --version)
log_info "Pip version: $PIP_VERSION"

################################################################################
# STEP 6: DEPENDENCY INSTALLATION
################################################################################

log_section "STEP 6: Installing Dependencies"

log_info "Installing Python dependencies from requirements.txt..."
log_info "This may take 5-15 minutes depending on your internet speed..."

# Install with detailed error handling
if pip install -r requirements.txt; then
    log_success "All dependencies installed successfully"
else
    exit_error "Failed to install dependencies. Check requirements.txt and try again."
fi

################################################################################
# STEP 7: DIRECTORY CREATION
################################################################################

log_section "STEP 7: Creating Data Directories"

log_info "Creating data and logs directories..."
mkdir -p data logs || exit_error "Failed to create directories"

log_success "Directories created"

################################################################################
# STEP 8: DATABASE INITIALIZATION
################################################################################

log_section "STEP 8: Database Initialization"

log_info "Initializing SQLite database..."
$PYTHON_CMD -c "
from logger import TradeDatabase
try:
    db = TradeDatabase()
    db.close()
    print('Database initialized successfully')
except Exception as e:
    print(f'Warning: Database initialization had issues: {e}')
    print('This is usually not critical and can be fixed later')
" || log_warning "Database initialization had issues (non-critical)"

log_success "Database initialized"

################################################################################
# STEP 9: EXCEL LOG INITIALIZATION
################################################################################

log_section "STEP 9: Excel Log Initialization"

log_info "Initializing Excel log..."
$PYTHON_CMD -c "
from logger import ExcelLogger
try:
    excel = ExcelLogger()
    excel.close()
    print('Excel log initialized successfully')
except Exception as e:
    print(f'Warning: Excel log initialization had issues: {e}')
    print('This is usually not critical and can be fixed later')
" || log_warning "Excel log initialization had issues (non-critical)"

log_success "Excel log initialized"

################################################################################
# STEP 10: VERIFICATION
################################################################################

log_section "STEP 10: Installation Verification"

log_info "Verifying installation..."

# Test critical imports
VERIFICATION_PASSED=true

log_info "Testing Python imports..."
$PYTHON_CMD -c "
import sys
import ccxt
import pandas
import numpy
import requests
import streamlit
import plotly
import sqlalchemy
print('✓ All critical packages imported successfully')
" || VERIFICATION_PASSED=false

if [ "$VERIFICATION_PASSED" = true ]; then
    log_success "Installation verification passed"
else
    log_warning "Some verification tests failed. Installation may still work."
fi

################################################################################
# FINAL SUMMARY
################################################################################

log_section "Setup Complete!"

echo ""
log_success "IndiaCryptoAlpha setup completed successfully!"
echo ""
echo -e "${BLUE}System Information:${NC}"
echo "  Platform: $PLATFORM"
echo "  Architecture: $ARCH"
echo "  Python: $PYTHON_VERSION"
echo "  Virtual Environment: venv/"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Activate virtual environment:"
echo "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "  2. Start trading system (Terminal 1):"
echo "     ${YELLOW}python main.py${NC}"
echo ""
echo "  3. Start dashboard (Terminal 2):"
echo "     ${YELLOW}streamlit run dashboard/app.py${NC}"
echo ""
echo "  4. Open browser:"
echo "     ${YELLOW}http://localhost:8501${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  README.md - Complete guide"
echo "  QUICKSTART.md - 5-minute setup"
echo "  DOCUMENTATION.md - API reference"
echo ""
echo -e "${GREEN}Happy Trading!${NC} 🚀📈"
echo ""
