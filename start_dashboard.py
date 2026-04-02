#!/usr/bin/env python3
"""Start Streamlit dashboard in background and verify it's accessible."""

import subprocess
import time
import sys
import os


def start_dashboard():
    """Start the Streamlit dashboard."""
    print("Starting Streamlit dashboard...")

    # Set environment
    env = os.environ.copy()
    env["PYTHONPATH"] = "/workspace/IndiaCryptoAlpha"
    env["PAPER_TRADING_MODE"] = "true"

    # Start Streamlit
    process = subprocess.Popen(
        [
            "/workspace/IndiaCryptoAlpha/venv/bin/streamlit",
            "run",
            "dashboard/race_app.py",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ],
        cwd="/workspace/IndiaCryptoAlpha",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for startup
    time.sleep(5)

    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"Dashboard failed to start. Exit code: {process.returncode()}")
        print(f"Stdout: {stdout.decode()}")
        print(f"Stderr: {stderr.decode()}")
        return False

    # Test if port is listening
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 8501))
    sock.close()

    if result == 0:
        print("✓ Streamlit dashboard is running on http://localhost:8501")

        # Save PID to file for cleanup
        with open("/tmp/streamlit_dashboard.pid", "w") as f:
            f.write(str(process.pid))

        print(f"Dashboard PID: {process.pid}")
        return True
    else:
        print("✗ Dashboard port 8501 not responding")
        process.terminate()
        return False


if __name__ == "__main__":
    success = start_dashboard()
    sys.exit(0 if success else 1)
