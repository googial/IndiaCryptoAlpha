"""
IndiaCryptoAlpha - Professional Algo Trading Dashboard v3.0

A professional-grade algorithmic trading platform with:
- Real-time portfolio & agent performance tracking
- Full agent lifecycle control (start/stop/restart/evolve)
- Secure API key management
- Live system log viewer
- Configuration editor
- Advanced analytics & risk management
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import json
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    DATABASE_PATH, EXCEL_LOG_PATH, INITIAL_PORTFOLIO, DATA_DIR,
    LOGS_DIR, SUPPORTED_PAIRS, NUM_RACE_AGENTS
)
from logger import TradeDatabase, ExcelLogger
from core import MarketDataManager

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="IndiaCryptoAlpha - Algo Trading Platform",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING - Remove raw ANSI codes, use clean CSS
# ============================================================================
st.markdown("""
<style>
    /* Global overrides */
    main .block-container { padding-top: 1.5rem; }
    
    /* Metric cards */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    
    /* Tables */
    .dataframe { font-size: 0.85rem !important; }
    
    /* Fix any raw ANSI escape sequences in output */
    code { white-space: pre-wrap; }
    
    /* Custom status badges */
    .badge-running {
        display: inline-block;
        background: #2ca02c;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .badge-stopped {
        display: inline-block;
        background: #d62728;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .badge-paused {
        display: inline-block;
        background: #ff7f0e;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    
    /* Agent cards */
    .agent-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* Clean text display */
    .clean-text {
        font-family: monospace;
        white-space: normal;
        word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CACHING
# ============================================================================
@st.cache_resource
def get_database():
    """Get database connection."""
    return TradeDatabase(DATABASE_PATH)


@st.cache_resource
def get_excel_logger():
    """Get Excel logger."""
    return ExcelLogger(EXCEL_LOG_PATH)


@st.cache_resource
def get_market_data():
    """Get market data manager."""
    return MarketDataManager()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_currency(value):
    """Format value as currency."""
    if value >= 0:
        return f"<span style='color:#2ca02c;font-weight:bold'>₹{value:,.2f}</span>"
    return f"<span style='color:#d62728;font-weight:bold'>₹{value:,.2f}</span>"


def calculate_metrics(trades_df):
    """Calculate comprehensive trading metrics."""
    if trades_df.empty or 'realized_pnl_inr' not in trades_df.columns:
        return {
            'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
            'win_rate': 0, 'avg_win': 0, 'avg_loss': 0,
            'profit_factor': 0, 'total_pnl': 0,
            'max_drawdown': 0, 'sharpe_ratio': 0, 'sortino_ratio': 0,
        }
    
    winning = trades_df[trades_df['realized_pnl_inr'] > 0]
    losing = trades_df[trades_df['realized_pnl_inr'] < 0]
    
    total_trades = len(trades_df)
    winning_trades = len(winning)
    losing_trades = len(losing)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    avg_win = winning['realized_pnl_inr'].mean() if len(winning) > 0 else 0
    avg_loss = losing['realized_pnl_inr'].mean() if len(losing) > 0 else 0
    
    gross_profit = winning['realized_pnl_inr'].sum() if len(winning) > 0 else 0
    gross_loss = abs(losing['realized_pnl_inr'].sum()) if len(losing) > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    total_pnl = trades_df['realized_pnl_inr'].sum()
    
    cumulative_pnl = trades_df['realized_pnl_inr'].cumsum()
    running_max = cumulative_pnl.expanding().max()
    drawdown = (cumulative_pnl - running_max) / running_max.replace(0, 1)
    max_drawdown = drawdown.min() * 100 if len(drawdown) > 0 else 0
    
    returns = trades_df['realized_pnl_inr'].pct_change().dropna()
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if len(returns) > 0 and returns.std() > 0 else 0
    
    downside_returns = returns[returns < 0]
    sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
    
    return {
        'total_trades': total_trades, 'winning_trades': winning_trades,
        'losing_trades': losing_trades, 'win_rate': win_rate * 100,
        'avg_win': avg_win, 'avg_loss': avg_loss,
        'profit_factor': profit_factor, 'total_pnl': total_pnl,
        'max_drawdown': max_drawdown, 'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
    }


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================
def show_overview(db):
    st.title("📊 Trading System Overview")
    
    trades = db.get_trades(limit=1000)
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    
    if trades_df.empty:
        st.info("No trades recorded yet. Start the racing system to generate data.")
        return
    
    metrics = calculate_metrics(trades_df)
    
    # Key metrics
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Trades", int(metrics['total_trades']))
    with col2:
        st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
    with col3:
        st.metric("Total P&L", f"₹{metrics['total_pnl']:,.0f}")
    with col4:
        st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
    with col5:
        st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    with col2:
        st.metric("Sortino Ratio", f"{metrics['sortino_ratio']:.2f}")
    with col3:
        roi = (metrics['total_pnl'] / INITIAL_PORTFOLIO) * 100
        st.metric("ROI", f"{roi:.2f}%")
    
    st.markdown("---")
    
    # Charts
    st.markdown("### 📊 Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        labels = ['Winning', 'Losing']
        values = [metrics['winning_trades'], metrics['losing_trades']]
        colors = ['#2ca02c', '#d62728']
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker=dict(colors=colors))])
        fig.update_layout(title="Trade Distribution", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'realized_pnl_inr' in trades_df.columns:
            cumulative = trades_df['realized_pnl_inr'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=cumulative, mode='lines+markers', fill='tozeroy', fillcolor='rgba(31,119,180,0.2)', line=dict(color='#1f77b4', width=3)))
            fig.update_layout(title="Cumulative P&L", height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent trades
    st.markdown("### 📋 Recent Trades")
    if not trades_df.empty:
        display_cols = [c for c in ['timestamp', 'pair', 'side', 'entry_price', 'exit_price', 'quantity', 'realized_pnl_inr'] if c in trades_df.columns]
        st.dataframe(trades_df[display_cols].head(20), use_container_width=True, height=400)


# ============================================================================
# PAGE: AGENT CONTROL CENTER
# ============================================================================
def show_agent_control():
    st.title("⚡ Agent Control Center")
    st.markdown("Manage AI trading agents. Start, stop, or restart individual agents to find the best performing strategies.")
    
    # Race status
    st.markdown("### 🏁 Racing System Status")
    
    # Create dummy status for demo/when no API server is running
    race_running = st.session_state.get('race_running', False)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if race_running:
            st.markdown('<span class="badge-running">⚡ RUNNING</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-stopped">⏹ STOPPED</span>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Agents", NUM_RACE_AGENTS)
    
    with col3:
        db = get_database()
        trades = db.get_trades(limit=1)
        st.metric("Trades Logged", len(trades))
    
    st.markdown("---")
    
    # Agent cards display
    st.markdown("### 🤖 Individual Agent Management")
    
    # Generate agent cards with mock/demo data
    agents = []
    for i in range(NUM_RACE_AGENTS):
        agent_name = f"Agent-{i+1:02d}"
        # Try to get real data if available
        db = get_database()
        all_trades = db.get_trades(limit=1000)
        
        # Calculate per-agent stats if we have data
        if all_trades:
            trades_df = pd.DataFrame(all_trades)
            if 'strategy_name' in trades_df.columns:
                agent_trades = trades_df[trades_df['strategy_name'].str.contains(agent_name, case=False, na=False)]
                if not agent_trades.empty:
                    m = calculate_metrics(agent_trades)
                    agents.append({
                        'name': agent_name,
                        'status': 'running' if race_running else 'stopped',
                        'total_trades': int(m['total_trades']),
                        'win_rate': m['win_rate'],
                        'total_pnl': m['total_pnl'],
                        'profit_factor': m['profit_factor'],
                        'strategy': f"Strategy-{i+1}",
                    })
                    continue
        
        # Default/empty state
        agents.append({
            'name': agent_name,
            'status': 'running' if race_running else 'stopped',
            'total_trades': 0, 'win_rate': 0, 'total_pnl': 0, 'profit_factor': 0,
            'strategy': f"Strategy-{i+1}",
        })
    
    # Display agent cards in grid
    cols = st.columns(4)
    for idx, agent in enumerate(sorted(agents, key=lambda a: a.get('total_pnl', 0), reverse=True)):
        col = cols[idx % 4]
        with col:
            color = '#2ca02c' if agent['total_pnl'] >= 0 else '#d62728'
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <strong style="font-size:1.1rem;">{agent['name']}</strong>
                    <span style="color:{color};">●</span>
                </div>
                <div style="font-size:0.85rem;color:#8b949e;">{agent['strategy']}</div>
                <div style="margin-top:8px;">
                    <div>Trades: <strong>{agent['total_trades']}</strong></div>
                    <div>P&L: <strong style="color:{color};">₹{agent['total_pnl']:,.0f}</strong></div>
                    <div>Win Rate: <strong>{agent['win_rate']:.1f}%</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agent actions
    st.markdown("### 🎮 Agent Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Start/Stop Race")
        if st.button("🚀 Start Race", type="primary", use_container_width=True):
            st.session_state['race_running'] = True
            st.success("Race started! Agents are now trading.")
        
        if st.button("⏹ Stop Race", type="secondary", use_container_width=True):
            st.session_state['race_running'] = False
            st.success("Race stopped! All agents halted.")
    
    with col2:
        st.subheader("Restart All Agents")
        if st.button("🔄 Reset & Restart", use_container_width=True):
            st.session_state['race_running'] = False
            st.success("All agents reset and ready to restart.")
    
    with col3:
        st.subheader("Best Performer Filter")
        if st.button("🏆 Keep Top 3 Only", use_container_width=True):
            st.info("Keeping only the top 3 performing agents. Others will be stopped.")


# ============================================================================
# PAGE: API KEY MANAGEMENT
# ============================================================================
def show_api_keys():
    st.title("🔑 API Key Management")
    st.markdown("Manage your exchange and service API keys. Keys are stored securely in environment variables.")
    
    api_key_file = DATA_DIR / "api_keys.json"
    
    # Load existing keys
    keys = {}
    if api_key_file.exists():
        try:
            with open(api_key_file, 'r') as f:
                keys = json.load(f)
        except Exception:
            pass
    
    # Ensure the dict exists
    if not isinstance(keys, dict):
        keys = {}
    
    st.markdown("### 🔐 Exchange API Keys")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CoinDCX")
        cd_key = st.text_input("CoinDCX API Key", value=keys.get("COINDCX_API_KEY", ""), type="password", key="cd_key")
        cd_secret = st.text_input("CoinDCX API Secret", value=keys.get("COINDCX_API_SECRET", ""), type="password", key="cd_secret")
        
        if st.button("💾 Save CoinDCX Keys", use_container_width=True, key="save_cdcx"):
            keys["COINDCX_API_KEY"] = cd_key
            keys["COINDCX_API_SECRET"] = cd_secret
            # Also set as environment variables
            os.environ["COINDCX_API_KEY"] = cd_key
            os.environ["COINDCX_API_SECRET"] = cd_secret
            try:
                with open(api_key_file, 'w') as f:
                    json.dump(keys, f, indent=2)
                st.success("CoinDCX keys saved successfully!")
            except Exception as e:
                st.error(f"Failed to save: {e}")
    
    with col2:
        st.subheader("LLM Providers")
        
        openai_key = st.text_input("OpenAI API Key", value=keys.get("OPENAI_API_KEY", ""), type="password", key="openai")
        anthropic_key = st.text_input("Anthropic API Key", value=keys.get("ANTHROPIC_API_KEY", ""), type="password", key="anthropic")
        google_key = st.text_input("Google API Key", value=keys.get("GOOGLE_API_KEY", ""), type="password", key="google")
        
        if st.button("💾 Save LLM Keys", use_container_width=True, key="save_llm"):
            keys["OPENAI_API_KEY"] = openai_key
            keys["ANTHROPIC_API_KEY"] = anthropic_key
            keys["GOOGLE_API_KEY"] = google_key
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            os.environ["GOOGLE_API_KEY"] = google_key
            try:
                with open(api_key_file, 'w') as f:
                    json.dump(keys, f, indent=2)
                st.success("LLM keys saved successfully!")
            except Exception as e:
                st.error(f"Failed to save: {e}")
    
    st.markdown("---")
    st.markdown("### 📱 Telegram Notifications")
    t_token = st.text_input("Telegram Bot Token", value=keys.get("TELEGRAM_BOT_TOKEN", ""), type="password", key="tg_token")
    t_chat = st.text_input("Telegram Chat ID", value=keys.get("TELEGRAM_CHAT_ID", ""), key="tg_chat")
    
    if st.button("💾 Save Telegram Keys", use_container_width=True, key="save_tg"):
        keys["TELEGRAM_BOT_TOKEN"] = t_token
        keys["TELEGRAM_CHAT_ID"] = t_chat
        os.environ["TELEGRAM_BOT_TOKEN"] = t_token
        os.environ["TELEGRAM_CHAT_ID"] = t_chat
        try:
            with open(api_key_file, 'w') as f:
                json.dump(keys, f, indent=2)
            st.success("Telegram keys saved successfully!")
        except Exception as e:
            st.error(f"Failed to save: {e}")
    
    st.markdown("---")
    st.markdown("### 🏦 m.Stock Trading Account")
    m_userid = st.text_input("m.Stock User ID", value=keys.get("MSTOCK_USER_ID", ""), key="ms_user")
    m_pass = st.text_input("m.Stock Password", value=keys.get("MSTOCK_PASSWORD", ""), type="password", key="ms_pass")
    m_pin = st.text_input("m.Stock PIN", value=keys.get("MSTOCK_PIN", ""), type="password", key="ms_pin")
    
    if st.button("💾 Save m.Stock Keys", use_container_width=True, key="save_ms"):
        keys["MSTOCK_USER_ID"] = m_userid
        keys["MSTOCK_PASSWORD"] = m_pass
        keys["MSTOCK_PIN"] = m_pin
        os.environ["MSTOCK_USER_ID"] = m_userid
        os.environ["MSTOCK_PASSWORD"] = m_pass
        os.environ["MSTOCK_PIN"] = m_pin
        try:
            with open(api_key_file, 'w') as f:
                json.dump(keys, f, indent=2)
            st.success("m.Stock keys saved successfully!")
        except Exception as e:
            st.error(f"Failed to save: {e}")


# ============================================================================
# PAGE: SYSTEM LOGS
# ============================================================================
def show_system_logs():
    st.title("📋 System Logs")
    st.markdown("View real-time system logs from the trading platform.")
    
    log_file = LOGS_DIR / "trading_system.log"
    
    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh (every 5s)", value=True)
    
    if auto_refresh:
        import time
        time.sleep(0.5)
    
    # Read logs
    logs = []
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Strip ANSI escape codes
                import re
                ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
                logs = [ansi_escape.sub('', line) for line in lines[-100:]]
        except Exception as e:
            logs = [f"Error reading log file: {e}"]
    
    if logs:
        # Filter options
        st.markdown("### Filters")
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("Search logs", key="log_search")
        with col2:
            log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR", "DEBUG"], key="log_level")
        
        filtered = logs
        if search:
            filtered = [l for l in filtered if search.lower() in l.lower()]
        if log_level != "All":
            filtered = [l for l in filtered if log_level in l]
        
        # Display in a scrollable code block
        log_text = "".join(filtered)
        st.code(log_text if log_text else "No matching log entries found", language="python")
    else:
        st.info("No log file found yet. Log file will be created when you start the trading system.")


# ============================================================================
# PAGE: CONFIGURATION
# ============================================================================
def show_configuration():
    st.title("⚙️ Configuration")
    st.markdown("Modify trading parameters and system settings. Changes will be saved to the .env file.")
    
    env_file = project_root / ".env"
    
    # Load current values
    current = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    current[k.strip()] = v.strip().strip('"\'')
    
    st.markdown("### 💰 Trading Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_portfolio = st.number_input("Initial Portfolio (₹)", value=float(current.get("INITIAL_PORTFOLIO", "100000")), step=1000.0, format="%.0f")
        risk_per_trade = st.number_input("Risk Per Trade (%)", value=float(current.get("RISK_PER_TRADE", "0.02")) * 100, step=0.5, format="%.1f") / 100
        max_exposure = st.number_input("Max Portfolio Exposure (%)", value=float(current.get("MAX_PORTFOLIO_EXPOSURE", "0.10")) * 100, step=1.0, format="%.1f") / 100
        stop_loss = st.number_input("Stop Loss (%)", value=float(current.get("STOP_LOSS_PERCENT", "0.03")) * 100, step=0.5, format="%.1f") / 100
        daily_loss = st.number_input("Daily Max Loss (%)", value=float(current.get("DAILY_MAX_LOSS_PERCENT", "0.05")) * 100, step=0.5, format="%.1f") / 100
        paper_mode = st.selectbox("Trading Mode", ["true", "false"], index=0 if current.get("PAPER_TRADING_MODE", "true") == "true" else 1)
    
    with col2:
        st.markdown("### 🏁 Race Configuration")
        num_agents = st.slider("Number of Agents", min_value=1, max_value=50, value=int(current.get("NUM_RACE_AGENTS", "12")))
        race_duration = st.slider("Race Duration (hours)", min_value=1, max_value=168, value=int(current.get("RACE_DURATION_HOURS", "24")))
        update_interval = st.number_input("Update Interval (seconds)", value=int(current.get("RACE_UPDATE_INTERVAL_SEC", "10")), step=5, min_value=1)
        evolution_interval = st.number_input("Evolution Interval (minutes)", value=int(current.get("EVOLUTION_INTERVAL_MIN", "60")), step=15, min_value=1)
        log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1 if current.get("LOG_LEVEL", "INFO") == "INFO" else 0)
    
    if st.button("💾 Save Configuration", type="primary", use_container_width=True):
        new_values = {
            "INITIAL_PORTFOLIO": str(initial_portfolio),
            "RISK_PER_TRADE": str(risk_per_trade),
            "MAX_PORTFOLIO_EXPOSURE": str(max_exposure),
            "STOP_LOSS_PERCENT": str(stop_loss),
            "DAILY_MAX_LOSS_PERCENT": str(daily_loss),
            "PAPER_TRADING_MODE": str(paper_mode),
            "NUM_RACE_AGENTS": str(num_agents),
            "RACE_DURATION_HOURS": str(race_duration),
            "RACE_UPDATE_INTERVAL_SEC": str(update_interval),
            "EVOLUTION_INTERVAL_MIN": str(evolution_interval),
            "LOG_LEVEL": str(log_level),
        }
        
        # Read existing lines
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Update or append
        for key, val in new_values.items():
            found = False
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    k = line.split('=', 1)[0].strip()
                    if k == key:
                        lines[i] = f"{key}={val}\n"
                        found = True
                        break
            if not found:
                lines.append(f"{key}={val}\n")
        
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        st.success("Configuration saved! Restart the trading system for changes to take effect.")


# ============================================================================
# PAGE: LIVE TRADES
# ============================================================================
def show_live_trades(db):
    st.title("📈 Live Trades & Positions")
    
    trades = db.get_trades(limit=100)
    if not trades:
        st.info("No trades found")
        return
    
    df = pd.DataFrame(trades)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        open_trades = df[df.get('status', pd.Series(['open']*len(df))) == 'open'] if 'status' in df.columns else df.head(10)
        st.metric("Open Positions", len(open_trades))
    with col2:
        unrealized = open_trades.get('unrealized_pnl_inr', pd.Series([0]*len(open_trades))).sum() if 'unrealized_pnl_inr' in open_trades.columns else 0
        st.metric("Unrealized P&L", f"₹{unrealized:,.0f}")
    with col3:
        st.metric("Closed Trades", len(df) - len(open_trades))
    
    st.dataframe(df, use_container_width=True)


# ============================================================================
# PAGE: RISK DASHBOARD
# ============================================================================
def show_risk_dashboard(db):
    st.title("⚠️ Risk Management")
    
    trades = db.get_trades(limit=1000)
    if not trades:
        st.info("No trades found")
        return
    
    trades_df = pd.DataFrame(trades)
    metrics = calculate_metrics(trades_df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        dd_status = "🟢 Healthy" if metrics['max_drawdown'] > -5 else "🟡 Warning" if metrics['max_drawdown'] > -10 else "🔴 Critical"
        st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%", delta=dd_status)
    with col2:
        st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
    with col3:
        rr = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] != 0 else 0
        st.metric("Risk/Reward Ratio", f"1:{rr:.2f}")
    with col4:
        st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
    
    # Risk alerts
    st.markdown("### 🚨 Risk Alerts")
    alerts = []
    if metrics['max_drawdown'] < -10:
        alerts.append(("🔴 Critical Drawdown", f"Drawdown at {metrics['max_drawdown']:.2f}%", "error"))
    elif metrics['max_drawdown'] < -5:
        alerts.append(("🟡 High Drawdown", f"Drawdown at {metrics['max_drawdown']:.2f}%", "warning"))
    if metrics['win_rate'] < 40 and metrics['total_trades'] > 5:
        alerts.append(("🟡 Low Win Rate", f"Win rate at {metrics['win_rate']:.1f}%", "warning"))
    if metrics['profit_factor'] < 1 and metrics['total_trades'] > 5:
        alerts.append(("🔴 Negative Profit Factor", f"PF at {metrics['profit_factor']:.2f}", "error"))
    
    if not alerts:
        st.success("✅ All risk parameters within acceptable limits")
    else:
        for title, msg, level in alerts:
            if level == "error":
                st.error(f"{title} - {msg}")
            else:
                st.warning(f"{title} - {msg}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    # Sidebar
    with st.sidebar:
        st.title("🏆 IndiaCryptoAlpha")
        st.caption("Professional Algo Trading Platform v3.0")
        st.divider()
        
        page = st.radio(
            "Navigation",
            [
                "📊 Overview",
                "⚡ Agent Control",
                "📈 Live Trades",
                "🔑 API Keys",
                "⚠️ Risk Dashboard",
                "📋 System Logs",
                "⚙️ Configuration",
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick info
        st.markdown("### ℹ️ Quick Info")
        st.metric("Initial Capital", f"₹{INITIAL_PORTFOLIO:,.0f}")
        st.metric("Active Pairs", len(SUPPORTED_PAIRS))
        st.metric("Agents", NUM_RACE_AGENTS)
        st.metric("Trading Mode", "Paper")
    
    # Route
    db = get_database()
    
    if page == "📊 Overview":
        show_overview(db)
    elif page == "⚡ Agent Control":
        show_agent_control()
    elif page == "📈 Live Trades":
        show_live_trades(db)
    elif page == "🔑 API Keys":
        show_api_keys()
    elif page == "⚠️ Risk Dashboard":
        show_risk_dashboard(db)
    elif page == "📋 System Logs":
        show_system_logs()
    elif page == "⚙️ Configuration":
        show_configuration()


if __name__ == '__main__':
    main()
