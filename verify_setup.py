#!/usr/bin/env python3
"""
Verification script for IndiaCryptoAlpha demo race.
Tests: imports, configuration, and demo race generation.
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        import ccxt
        import pandas
        import streamlit
        import numpy
        import plotly
        import openai
        import anthropic
        import google.generativeai
        import dotenv
        import requests
        import telegram
        import ta
        import sqlalchemy
        import openpyxl
        import apscheduler

        print("  ✓ All critical imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_env_file():
    """Test .env configuration exists and has required keys"""
    print("Testing .env configuration...")
    env_path = Path("/workspace/IndiaCryptoAlpha/.env")
    if not env_path.exists():
        print("  ✗ .env file not found")
        return False

    required_keys = [
        "LLM_PROVIDER",
        "PAPER_TRADING_MODE",
        "RACE_DURATION_HOURS",
        "NUM_RACE_AGENTS",
    ]

    content = env_path.read_text()
    missing = [k for k in required_keys if k not in content]

    if missing:
        print(f"  ✗ Missing required keys: {missing}")
        return False

    print("  ✓ .env configuration valid")
    return True


def test_demo_script():
    """Test that demo race script exists and is importable"""
    print("Testing demo race script...")
    script_path = Path("/workspace/IndiaCryptoAlpha/generate_demo_race.py")
    if not script_path.exists():
        print("  ✗ generate_demo_race.py not found")
        return False

    # Try to import it
    try:
        sys.path.insert(0, "/workspace/IndiaCryptoAlpha")
        # We don't actually import the module to avoid side effects
        # Just check syntax by compiling
        with open(script_path) as f:
            compile(f.read(), script_path, "exec")
        print("  ✓ Demo race script syntax valid")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error in demo script: {e}")
        return False


def test_venv_activation():
    """Test that virtual environment binaries are accessible"""
    print("Testing virtual environment...")
    venv_python = Path("/workspace/IndiaCryptoAlpha/venv/bin/python")
    if not venv_python.exists():
        print("  ✗ Virtual environment python not found")
        return False

    # Test python -c "import ..."
    import subprocess

    result = subprocess.run(
        [str(venv_python), "-c", "import sys; print(sys.executable)"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"  ✓ Virtual environment working: {result.stdout.strip()}")
        return True
    else:
        print(f"  ✗ Virtual environment test failed: {result.stderr}")
        return False


def run_all_tests():
    print("=" * 60)
    print("IndiaCryptoAlpha Pre-Run Verification")
    print("=" * 60)

    tests = [test_imports, test_env_file, test_demo_script, test_venv_activation]

    results = [t() for t in tests]

    print("=" * 60)
    if all(results):
        print("✓ ALL PRE-RUN CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME CHECKS FAILED - FIX BEFORE PROCEEDING")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
