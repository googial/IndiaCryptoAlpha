# IndiaCryptoAlpha - Makefile
# 
# Usage: make <target>
# Examples:
#   make setup       - Run complete setup
#   make run         - Start trading system
#   make dashboard   - Start Streamlit dashboard
#   make clean       - Clean up virtual environment and cache
#   make test        - Run verification tests
#   make docker-build - Build Docker image
#   make docker-run  - Run Docker container

.PHONY: help setup run dashboard logs clean test verify docker-build docker-run

# Default target
help:
	@echo "IndiaCryptoAlpha - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Run complete automated setup"
	@echo "  make verify         - Verify installation"
	@echo ""
	@echo "Running:"
	@echo "  make run            - Start trading system"
	@echo "  make dashboard      - Start Streamlit dashboard"
	@echo "  make logs           - Tail system logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean virtual environment"
	@echo "  make test           - Run verification tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo ""

# ============================================================================
# Setup & Installation
# ============================================================================

setup:
	@echo "Running IndiaCryptoAlpha setup..."
	@bash setup.sh

verify:
	@echo "Verifying installation..."
	@. venv/bin/activate && python verify_install.py

# ============================================================================
# Running
# ============================================================================

run:
	@echo "Starting IndiaCryptoAlpha trading system..."
	@. venv/bin/activate && python main.py

dashboard:
	@echo "Starting Streamlit dashboard..."
	@. venv/bin/activate && streamlit run dashboard/app.py

logs:
	@echo "Tailing system logs..."
	@tail -f logs/trading_system.log

# ============================================================================
# Maintenance
# ============================================================================

clean:
	@echo "Cleaning up..."
	@rm -rf venv
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf .streamlit
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

test:
	@echo "Running verification tests..."
	@. venv/bin/activate && python -c "\
		import ccxt, pandas, numpy, requests, streamlit, plotly, sqlalchemy; \
		print('✓ All critical packages imported successfully')"
	@. venv/bin/activate && python -c "\
		from logger import TradeDatabase; \
		db = TradeDatabase(); \
		db.close(); \
		print('✓ Database ready')"
	@. venv/bin/activate && python -c "\
		from core import MarketDataManager; \
		m = MarketDataManager(); \
		print('✓ CoinDCX connected')"
	@echo "✓ All tests passed"

# ============================================================================
# Docker
# ============================================================================

docker-build:
	@echo "Building Docker image..."
	@docker build -t indiacryptoalpha:latest .
	@echo "✓ Docker image built successfully"

docker-run:
	@echo "Running Docker container..."
	@docker run -it -p 8501:8501 \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		indiacryptoalpha:latest

# ============================================================================
# Development
# ============================================================================

install-dev:
	@echo "Installing development dependencies..."
	@. venv/bin/activate && pip install pytest black flake8 mypy

format:
	@echo "Formatting code..."
	@. venv/bin/activate && black . --quiet

lint:
	@echo "Linting code..."
	@. venv/bin/activate && flake8 . --max-line-length=100

type-check:
	@echo "Type checking..."
	@. venv/bin/activate && mypy . --ignore-missing-imports

# ============================================================================
# Git
# ============================================================================

git-status:
	@git status

git-log:
	@git log --oneline -10

git-push:
	@git push origin main

# ============================================================================
# Info
# ============================================================================

info:
	@echo "IndiaCryptoAlpha - System Information"
	@echo "====================================="
	@echo ""
	@echo "Python Version:"
	@python3 --version
	@echo ""
	@echo "Git Status:"
	@git status --short
	@echo ""
	@echo "Virtual Environment:"
	@if [ -d "venv" ]; then echo "✓ venv/ exists"; else echo "✗ venv/ not found"; fi
	@echo ""
	@echo "Data Directory:"
	@if [ -d "data" ]; then echo "✓ data/ exists"; else echo "✗ data/ not found"; fi
	@echo ""
	@echo "Logs Directory:"
	@if [ -d "logs" ]; then echo "✓ logs/ exists"; else echo "✗ logs/ not found"; fi
	@echo ""
