"""
IndiaAI Race Alpha - Real-Time AI Race Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import INITIAL_PORTFOLIO, NUM_RACE_AGENTS, SUPPORTED_PAIRS
from race.orchestrator import RaceOrchestrator

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="IndiaAI Race Alpha - Live AI Trading Race",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM STYLING (Matching the Video)
# ============================================================================

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .race-lane {
        background-color: #161b22;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #1f77b4;
        transition: transform 0.2s;
    }
    .race-lane:hover {
        transform: scale(1.01);
        background-color: #1c2128;
    }
    .agent-name {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    .pnl-positive {
        color: #00ff00;
        font-weight: bold;
    }
    .pnl-negative {
        color: #ff4b4b;
        font-weight: bold;
    }
    .progress-container {
        width: 100%;
        background-color: #30363d;
        border-radius: 5px;
        margin-top: 10px;
    }
    .progress-bar {
        height: 20px;
        border-radius: 5px;
        text-align: center;
        line-height: 20px;
        color: white;
        font-size: 12px;
        font-weight: bold;
    }
    .leaderboard-card {
        background-color: #161b22;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #30363d;
    }
    .stat-box {
        text-align: center;
        padding: 10px;
        background-color: #1c2128;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = RaceOrchestrator(num_agents=NUM_RACE_AGENTS)
    # For demo purposes, we'll start it automatically if not running
    if not st.session_state.orchestrator.is_running:
        st.session_state.orchestrator.start_race()

orchestrator = st.session_state.orchestrator

# ============================================================================
# HEADER
# ============================================================================

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    st.title("🏁 IndiaAI Race Alpha")
    st.caption("Real-time Autonomous AI Trading Competition")

with col2:
    status = "🟢 LIVE" if orchestrator.is_running else "🔴 STOPPED"
    st.markdown(f"<div class='stat-box'><h3>{status}</h3><p>Race Status</p></div>", unsafe_allow_html=True)

with col3:
    time_rem = orchestrator.get_race_status()['time_remaining'] or "00:00:00"
    # Format time remaining
    st.markdown(f"<div class='stat-box'><h3>{time_rem.split('.')[0]}</h3><p>Time Remaining</p></div>", unsafe_allow_html=True)

with col4:
    total_trades = sum(a.performance['total_trades'] for a in orchestrator.agents)
    st.markdown(f"<div class='stat-box'><h3>{total_trades}</h3><p>Total Trades</p></div>", unsafe_allow_html=True)

st.divider()

# ============================================================================
# MAIN VIEW: RACE LANES
# ============================================================================

race_col, side_col = st.columns([2, 1])

with race_col:
    st.subheader("🏎 Live Race Lanes")
    
    # Sort agents by P&L for the lanes
    sorted_agents = sorted(orchestrator.agents, 
                         key=lambda a: a.risk_engine.current_portfolio, 
                         reverse=True)
    
    for i, agent in enumerate(sorted_agents):
        pnl = agent.risk_engine.current_portfolio - INITIAL_PORTFOLIO
        pnl_pct = (pnl / INITIAL_PORTFOLIO) * 100
        
        # Color based on P&L
        bar_color = "#00ff00" if pnl >= 0 else "#ff4b4b"
        # Width based on P&L % (normalized for visualization)
        # 0% P&L is 50% width. +10% P&L is 100% width. -10% P&L is 0% width.
        width_pct = max(0, min(100, 50 + (pnl_pct * 5)))
        
        pnl_class = "pnl-positive" if pnl >= 0 else "pnl-negative"
        
        st.markdown(f"""
            <div class="race-lane">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="agent-name">#{i+1} {agent.name}</span>
                    <span class="{pnl_class}">₹{pnl:,.2f} ({pnl_pct:+.2f}%)</span>
                </div>
                <div style="font-size: 12px; color: #8b949e; margin-top: 5px;">
                    Strategy: {agent.strategy_description}
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {width_pct}%; background-color: {bar_color};">
                        {pnl_pct:+.1f}%
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with side_col:
    st.subheader("🏆 Leaderboard")
    
    leaderboard_data = []
    for i, agent in enumerate(sorted_agents):
        pnl = agent.risk_engine.current_portfolio - INITIAL_PORTFOLIO
        pnl_pct = (pnl / INITIAL_PORTFOLIO) * 100
        leaderboard_data.append({
            "Rank": i + 1,
            "Agent": agent.name,
            "P&L (₹)": f"₹{pnl:,.2f}",
            "P&L %": f"{pnl_pct:+.2f}%",
            "Trades": agent.performance['total_trades'],
            "Win Rate": f"{(agent.performance['winning_trades']/agent.performance['total_trades']*100 if agent.performance['total_trades']>0 else 0):.1f}%"
        })
    
    st.table(pd.DataFrame(leaderboard_data).set_index('Rank'))
    
    st.subheader("📈 Equity Curves")
    # Mocking equity curve data for visualization
    # In a real app, we'd pull this from the snapshots
    fig = go.Figure()
    for agent in sorted_agents[:5]: # Show top 5
        # Generate some random-ish walk for demo
        y = [INITIAL_PORTFOLIO]
        curr = INITIAL_PORTFOLIO
        for _ in range(10):
            curr *= (1 + np.random.normal(0.001, 0.005))
            y.append(curr)
        
        fig.add_trace(go.Scatter(y=y, name=agent.name, mode='lines'))
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# AGENT DETAILS
# ============================================================================

st.divider()
st.subheader("🤖 Agent Intelligence & Research")

selected_agent_name = st.selectbox("Select Agent to Inspect", [a.name for a in orchestrator.agents])
selected_agent = next(a for a in orchestrator.agents if a.name == selected_agent_name)

det_col1, det_col2 = st.columns(2)

with det_col1:
    st.info(f"**Current Strategy:**\n\n{selected_agent.strategy_description}")
    st.success(f"**Research Notes:**\n\n{selected_agent.research_notes}")

with det_col2:
    st.write("**Recent Activity:**")
    if selected_agent.trades:
        trades_df = pd.DataFrame(selected_agent.trades).tail(5)
        st.dataframe(trades_df)
    else:
        st.write("No trades executed yet.")

# ============================================================================
# AUTO-REFRESH
# ============================================================================

time.sleep(5)
st.rerun()
