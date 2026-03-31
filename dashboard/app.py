"""Streamlit Dashboard for IndiaCryptoAlpha Trading System."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATABASE_PATH, EXCEL_LOG_PATH, INITIAL_PORTFOLIO
from logger import TradeDatabase, ExcelLogger
from core import MarketDataManager

# Page configuration
st.set_page_config(
    page_title="IndiaCryptoAlpha Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive {
        color: #00cc00;
        font-weight: bold;
    }
    .negative {
        color: #ff0000;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


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


def format_currency(value):
    """Format value as currency."""
    return f"₹{value:,.2f}"


def format_percentage(value):
    """Format value as percentage."""
    return f"{value:.2f}%"


def main():
    """Main dashboard application."""
    
    # Sidebar navigation
    st.sidebar.title("🚀 IndiaCryptoAlpha")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Overview", "📈 Live Trades", "🏆 Agent Leaderboard", 
         "📉 P&L Charts", "🔬 Researcher Reports", "⚠️ Risk Dashboard"]
    )

    # Initialize data sources
    db = get_database()
    excel = get_excel_logger()
    market_data = get_market_data()

    if page == "📊 Overview":
        show_overview(db, excel)
    elif page == "📈 Live Trades":
        show_live_trades(db)
    elif page == "🏆 Agent Leaderboard":
        show_agent_leaderboard(db)
    elif page == "📉 P&L Charts":
        show_pnl_charts(db)
    elif page == "🔬 Researcher Reports":
        show_researcher_reports()
    elif page == "⚠️ Risk Dashboard":
        show_risk_dashboard(db)


def show_overview(db, excel):
    """Display overview page."""
    st.title("📊 Trading System Overview")
    
    # Get statistics
    stats = db.get_statistics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Trades",
            stats.get('total_trades', 0),
            delta=None
        )
    
    with col2:
        win_rate = stats.get('win_rate', 0) * 100
        st.metric(
            "Win Rate",
            f"{win_rate:.2f}%",
            delta=None
        )
    
    with col3:
        total_pnl = stats.get('total_pnl', 0)
        st.metric(
            "Total P&L",
            format_currency(total_pnl),
            delta=format_currency(total_pnl),
            delta_color="normal" if total_pnl >= 0 else "inverse"
        )
    
    with col4:
        profit_factor = stats.get('profit_factor', 0)
        st.metric(
            "Profit Factor",
            f"{profit_factor:.2f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Win/Loss distribution
        labels = ['Winning Trades', 'Losing Trades']
        values = [stats.get('winning_trades', 0), stats.get('losing_trades', 0)]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(title="Trade Distribution", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # P&L summary
        avg_win = stats.get('avg_win', 0)
        avg_loss = abs(stats.get('avg_loss', 0))
        
        fig = go.Figure(data=[
            go.Bar(x=['Avg Win', 'Avg Loss'], y=[avg_win, avg_loss],
                   marker_color=['green', 'red'])
        ])
        fig.update_layout(title="Average Win/Loss", height=400, yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent trades
    st.subheader("Recent Trades")
    trades = db.get_trades(limit=10)
    
    if trades:
        df = pd.DataFrame(trades)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No trades yet")


def show_live_trades(db):
    """Display live trades page."""
    st.title("📈 Live Trades")
    
    # Get open trades
    trades = db.get_trades(limit=50)
    
    if trades:
        df = pd.DataFrame(trades)
        
        # Filter for open trades
        open_trades = df[df['status'] == 'open'] if 'status' in df.columns else df
        
        if not open_trades.empty:
            st.subheader(f"Open Positions ({len(open_trades)})")
            st.dataframe(open_trades, use_container_width=True)
        else:
            st.info("No open positions")
        
        st.markdown("---")
        
        st.subheader("Recent Closed Trades")
        closed_trades = df[df['status'] == 'closed'] if 'status' in df.columns else df.head(10)
        st.dataframe(closed_trades, use_container_width=True)
    else:
        st.info("No trades found")


def show_agent_leaderboard(db):
    """Display agent leaderboard."""
    st.title("🏆 Agent Leaderboard")
    
    # Get agent performance data
    agent_stats = {}
    strategies = ['RSI+MACD Momentum', 'Bollinger Band + Volume', 'EMA Crossover + Supertrend']
    
    for strategy in strategies:
        stats = db.get_statistics(strategy=strategy)
        agent_stats[strategy] = stats
    
    # Create leaderboard
    leaderboard_data = []
    for strategy, stats in agent_stats.items():
        leaderboard_data.append({
            'Agent': strategy,
            'Trades': stats.get('total_trades', 0),
            'Win Rate': f"{stats.get('win_rate', 0) * 100:.2f}%",
            'Total P&L': format_currency(stats.get('total_pnl', 0)),
            'Profit Factor': f"{stats.get('profit_factor', 0):.2f}",
        })
    
    df = pd.DataFrame(leaderboard_data)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    # Agent comparison chart
    if leaderboard_data:
        agents = [d['Agent'] for d in leaderboard_data]
        pnls = [float(d['Total P&L'].replace('₹', '').replace(',', '')) for d in leaderboard_data]
        
        fig = go.Figure(data=[
            go.Bar(x=agents, y=pnls, marker_color=['green' if p >= 0 else 'red' for p in pnls])
        ])
        fig.update_layout(title="Agent P&L Comparison", yaxis_title="P&L (₹)", height=400)
        st.plotly_chart(fig, use_container_width=True)


def show_pnl_charts(db):
    """Display P&L charts."""
    st.title("📉 P&L Charts")
    
    trades = db.get_trades(limit=100)
    
    if trades:
        df = pd.DataFrame(trades)
        
        # Cumulative P&L
        if 'cumulative_pnl' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=df['cumulative_pnl'],
                mode='lines',
                name='Cumulative P&L',
                line=dict(color='blue', width=2)
            ))
            fig.update_layout(
                title="Cumulative P&L Over Time",
                yaxis_title="P&L (₹)",
                xaxis_title="Trade Number",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # P&L by pair
        if 'pair' in df.columns and 'realized_pnl_inr' in df.columns:
            pair_pnl = df.groupby('pair')['realized_pnl_inr'].sum().reset_index()
            pair_pnl.columns = ['Pair', 'Total P&L']
            
            fig = go.Figure(data=[
                go.Bar(x=pair_pnl['Pair'], y=pair_pnl['Total P&L'],
                       marker_color=['green' if p >= 0 else 'red' for p in pair_pnl['Total P&L']])
            ])
            fig.update_layout(title="P&L by Trading Pair", yaxis_title="P&L (₹)", height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trades found")


def show_researcher_reports():
    """Display researcher reports."""
    st.title("🔬 Researcher Reports")
    
    st.info("Market analysis and backtesting reports will appear here")
    
    # Placeholder for researcher reports
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Market Regime")
        st.write("BTC-INR: Bullish")
        st.write("ETH-INR: Sideways")
    
    with col2:
        st.subheader("Recommendations")
        st.write("✓ Increase BTC position")
        st.write("⚠ Reduce ETH exposure")


def show_risk_dashboard(db):
    """Display risk dashboard."""
    st.title("⚠️ Risk Dashboard")
    
    # Risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Max Drawdown", "5.2%", delta="-0.3%", delta_color="inverse")
    
    with col2:
        st.metric("Daily Loss", "₹-2,500", delta="-₹500", delta_color="inverse")
    
    with col3:
        st.metric("Portfolio Exposure", "45%", delta="+5%")
    
    with col4:
        st.metric("Risk/Reward Ratio", "1:2.5", delta=None)
    
    st.markdown("---")
    
    # Risk alerts
    st.subheader("Active Alerts")
    
    alerts = [
        {"type": "⚠️ Drawdown", "message": "Drawdown at 5.2%, approaching limit", "severity": "high"},
        {"type": "ℹ️ Info", "message": "Daily summary sent to Telegram", "severity": "low"},
    ]
    
    for alert in alerts:
        if alert['severity'] == 'high':
            st.error(f"{alert['type']}: {alert['message']}")
        else:
            st.info(f"{alert['type']}: {alert['message']}")


if __name__ == '__main__':
    main()
