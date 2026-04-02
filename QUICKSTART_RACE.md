# IndiaAI Race Alpha - Quickstart Guide: AI Race Mode

This guide will get you up and running with a simulated AI trading race in minutes. This is perfect for demonstration, testing, and understanding the core functionality of IndiaAI Race Alpha.

## 🚀 One-Command Race Launch

To launch a short demo race with dummy agents, simply run the following commands in your terminal:

```bash
# 1. Navigate to the project directory
cd IndiaCryptoAlpha

# 2. Ensure dependencies are installed (run only once or after updates)
# If you haven't run setup.sh yet, do it now:
# chmod +x setup.sh
# ./setup.sh

# 3. Activate your Python virtual environment
source venv/bin/activate

# 4. Launch the demo race
python generate_demo_race.py
```

This will start a race with a small number of agents for a short duration, logging their activities to the console and to `logs/demo_race.log`.

## 📊 Launching the Race Dashboard

While the demo race is running, you can open a **new terminal** to launch the real-time race dashboard:

```bash
# 1. Navigate to the project directory
cd IndiaCryptoAlpha

# 2. Activate your Python virtual environment
source venv/bin/activate

# 3. Launch the Streamlit race dashboard
streamlit run dashboard/race_app.py
```

Access the dashboard in your web browser at `http://localhost:8501` (or the address provided by Streamlit).

## ⚙️ Configuration for Race Mode

Race parameters can be configured in your `.env` file. Create or update `.env` in the project root with the following (example values shown):

```env
# Race Configuration
RACE_DURATION_HOURS=0.1  # Duration of the race in hours (e.g., 24 for 24 hours, 0.1 for 6 minutes demo)
NUM_RACE_AGENTS=3        # Number of AI trading agents to compete (e.g., 12, 24, 36)
RACE_UPDATE_INTERVAL_SEC=5 # How often agents analyze/trade and dashboard updates (seconds)
EVOLUTION_INTERVAL_MIN=10 # How often LLM agents review and evolve strategies (minutes)

# LLM Configuration (Choose one and provide API key)
LLM_PROVIDER=openai      # Options: openai, anthropic, google, xai
OPENAI_API_KEY=sk-your_openai_api_key
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=

# m.Stock Configuration (if enabling live stock trading)
MSTOCK_USER_ID=
MSTOCK_PASSWORD=
MSTOCK_PIN=
MSTOCK_API_KEY=
MSTOCK_API_SECRET=

# CoinDCX API Configuration (for crypto trading)
COINDCX_API_KEY=your_coindcx_api_key
COINDCX_API_SECRET=your_coindcx_api_secret

# Other Trading Settings
INITIAL_PORTFOLIO=100000 # Starting virtual capital for each agent
PAPER_TRADING_MODE=true  # Set to 'false' to enable live trading (use with caution!)
```

**Important:** For live trading, set `PAPER_TRADING_MODE=false` and ensure you have valid API keys for CoinDCX and/or m.Stock. Always start with paper trading to validate your setup.

## 💡 Next Steps

-   **Explore the Dashboard**: Interact with the live race visualization, leaderboard, and agent details.
-   **Customize Agents**: Modify `agents/llm_agent.py` to experiment with different LLM prompts or strategy evolution logic.
-   **Add New LLM Providers**: Extend the `LLMTradingAgent` to integrate other LLMs.
-   **Live Trading**: Once confident, switch `PAPER_TRADING_MODE` to `false` and enable live trading for CoinDCX and/or m.Stock.

Enjoy the race!
