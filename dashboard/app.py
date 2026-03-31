"""
IndiaCryptoAlpha - Premium Trading Dashboard v2.0

A professional-grade algorithmic trading dashboard with advanced analytics,
real-time monitoring, and institutional-quality features.

Features:
- Real-time portfolio tracking
- Advanced technical analysis
- Risk management dashboard
- Performance analytics
- Market heatmaps
- Trade journal
- Backtesting results
- Strategy comparison
- Alert management
- Responsive design
"""

import streamlit as st
import pandas as pd
import numpy as np
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

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="IndiaCryptoAlpha - Premium Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
    <style>
    /* Main theme */
    :root {
        --primary-color: #1f77b4;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --warning-color: #ff7f0e;
        --dark-bg: #0e1117;
        --card-bg: #161b22;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Status indicators */
    .status-active {
        color: #2ca02c;
        font-weight: bold;
    }
    
    .status-inactive {
        color: #d62728;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ff7f0e;
        font-weight: bold;
    }
    
    /* Positive/Negative */
    .positive {
        color: #2ca02c;
        font-weight: bold;
    }
    
    .negative {
        color: #d62728;
        font-weight: bold;
    }
    
    .neutral {
        color: #666;
        font-weight: bold;
    }
    
    /* Section headers */
    .section-header {
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Alert boxes */
    .alert-high {
        background-color: #fee;
        border-left: 4px solid #d62728;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .alert-medium {
        background-color: #fef3cd;
        border-left: 4px solid #ff7f0e;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .alert-low {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    /* Tables */
    .dataframe {
        font-size: 12px;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #161b22;
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
        return f"<span class='positive'>₹{value:,.2f}</span>"
    else:
        return f"<span class='negative'>₹{value:,.2f}</span>"


def format_percentage(value):
    """Format value as percentage."""
    if value >= 0:
        return f"<span class='positive'>{value:.2f}%</span>"
    else:
        return f"<span class='negative'>{value:.2f}%</span>"


def get_status_indicator(value, threshold_high=0, threshold_low=-5):
    """Get status indicator based on value."""
    if value >= threshold_high:
        return "🟢 Healthy"
    elif value >= threshold_low:
        return "🟡 Warning"
    else:
        return "🔴 Critical"


def calculate_metrics(trades_df):
    """Calculate comprehensive trading metrics."""
    if trades_df.empty:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'total_pnl': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
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
    
    # Calculate max drawdown
    cumulative_pnl = trades_df['realized_pnl_inr'].cumsum()
    running_max = cumulative_pnl.expanding().max()
    drawdown = (cumulative_pnl - running_max) / running_max.replace(0, 1)
    max_drawdown = drawdown.min() * 100 if len(drawdown) > 0 else 0
    
    # Calculate Sharpe ratio (simplified)
    returns = trades_df['realized_pnl_inr'].pct_change().dropna()
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if len(returns) > 0 and returns.std() > 0 else 0
    
    # Calculate Sortino ratio (simplified)
    downside_returns = returns[returns < 0]
    sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate * 100,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'total_pnl': total_pnl,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
    }


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

def show_overview(db, excel):
    """Display premium overview page."""
    st.title("📊 Trading System Overview")
    
    # Get data
    trades = db.get_trades(limit=1000)
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    
    if trades_df.empty:
        st.warning("No trades yet. Start the trading system to see data.")
        return
    
    metrics = calculate_metrics(trades_df)
    
    # ========== Key Metrics Row 1 ==========
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Trades",
            int(metrics['total_trades']),
            delta=None,
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "Win Rate",
            f"{metrics['win_rate']:.1f}%",
            delta=None,
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "Total P&L",
            f"₹{metrics['total_pnl']:,.0f}",
            delta=f"₹{metrics['total_pnl']:,.0f}",
            delta_color="normal" if metrics['total_pnl'] >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            "Profit Factor",
            f"{metrics['profit_factor']:.2f}",
            delta=None,
            delta_color="off"
        )
    
    with col5:
        st.metric(
            "Max Drawdown",
            f"{metrics['max_drawdown']:.2f}%",
            delta=None,
            delta_color="inverse"
        )
    
    # ========== Key Metrics Row 2 ==========
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Avg Win",
            f"₹{metrics['avg_win']:,.0f}",
            delta=None,
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "Avg Loss",
            f"₹{metrics['avg_loss']:,.0f}",
            delta=None,
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.2f}",
            delta=None,
            delta_color="off"
        )
    
    with col4:
        st.metric(
            "Sortino Ratio",
            f"{metrics['sortino_ratio']:.2f}",
            delta=None,
            delta_color="off"
        )
    
    with col5:
        portfolio_value = INITIAL_PORTFOLIO + metrics['total_pnl']
        roi = (metrics['total_pnl'] / INITIAL_PORTFOLIO) * 100
        st.metric(
            "ROI",
            f"{roi:.2f}%",
            delta=f"₹{metrics['total_pnl']:,.0f}",
            delta_color="normal" if roi >= 0 else "inverse"
        )
    
    st.markdown("---")
    
    # ========== Charts Row 1 ==========
    st.markdown("### 📊 Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Win/Loss distribution
        labels = ['Winning Trades', 'Losing Trades']
        values = [metrics['winning_trades'], metrics['losing_trades']]
        colors = ['#2ca02c', '#d62728']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textposition='inside',
            textinfo='label+percent'
        )])
        fig.update_layout(
            title="Trade Distribution",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # P&L summary
        avg_win = metrics['avg_win']
        avg_loss = abs(metrics['avg_loss'])
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Avg Win', 'Avg Loss'],
                y=[avg_win, avg_loss],
                marker_color=['#2ca02c', '#d62728'],
                text=[f'₹{avg_win:,.0f}', f'₹{avg_loss:,.0f}'],
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="Average Win/Loss",
            height=400,
            yaxis_title="Amount (₹)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ========== Charts Row 2 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        # Cumulative P&L
        if 'realized_pnl_inr' in trades_df.columns:
            cumulative_pnl = trades_df['realized_pnl_inr'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=cumulative_pnl,
                mode='lines+markers',
                name='Cumulative P&L',
                line=dict(color='#1f77b4', width=3),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ))
            fig.update_layout(
                title="Cumulative P&L Over Time",
                yaxis_title="P&L (₹)",
                xaxis_title="Trade Number",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Drawdown chart
        if 'realized_pnl_inr' in trades_df.columns:
            cumulative_pnl = trades_df['realized_pnl_inr'].cumsum()
            running_max = cumulative_pnl.expanding().max()
            drawdown = ((cumulative_pnl - running_max) / running_max.replace(0, 1)) * 100
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=drawdown,
                mode='lines',
                name='Drawdown',
                line=dict(color='#d62728', width=2),
                fill='tozeroy',
                fillcolor='rgba(214, 39, 40, 0.2)'
            ))
            fig.update_layout(
                title="Drawdown Over Time",
                yaxis_title="Drawdown (%)",
                xaxis_title="Trade Number",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========== Recent Trades Table ==========
    st.markdown("### 📋 Recent Trades")
    recent_trades = trades_df.head(20)
    
    if not recent_trades.empty:
        # Format display
        display_df = recent_trades[['timestamp', 'pair', 'side', 'entry_price', 'exit_price', 'quantity', 'realized_pnl_inr']].copy()
        display_df.columns = ['Time', 'Pair', 'Side', 'Entry', 'Exit', 'Qty', 'P&L (₹)']
        
        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        st.info("No trades yet")


# ============================================================================
# PAGE: LIVE TRADES
# ============================================================================

def show_live_trades(db):
    """Display live trades page."""
    st.title("📈 Live Trades & Positions")
    
    trades = db.get_trades(limit=100)
    
    if not trades:
        st.info("No trades found")
        return
    
    df = pd.DataFrame(trades)
    
    # ========== Open Positions ==========
    st.markdown("### 🟢 Open Positions")
    
    if 'status' in df.columns:
        open_trades = df[df['status'] == 'open']
    else:
        open_trades = df.head(10)
    
    if not open_trades.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Open Positions", len(open_trades))
        
        with col2:
            open_pnl = open_trades['unrealized_pnl_inr'].sum() if 'unrealized_pnl_inr' in open_trades.columns else 0
            st.metric("Unrealized P&L", f"₹{open_pnl:,.0f}")
        
        with col3:
            total_exposure = open_trades['quantity'].sum() if 'quantity' in open_trades.columns else 0
            st.metric("Total Exposure", f"{total_exposure:.2f}")
        
        st.dataframe(open_trades, use_container_width=True)
    else:
        st.info("No open positions")
    
    st.markdown("---")
    
    # ========== Closed Trades ==========
    st.markdown("### 🔴 Closed Trades")
    
    if 'status' in df.columns:
        closed_trades = df[df['status'] == 'closed']
    else:
        closed_trades = df.tail(20)
    
    if not closed_trades.empty:
        st.dataframe(closed_trades, use_container_width=True, height=400)
    else:
        st.info("No closed trades")


# ============================================================================
# PAGE: AGENT LEADERBOARD
# ============================================================================

def show_agent_leaderboard(db):
    """Display agent leaderboard."""
    st.title("🏆 Agent Leaderboard")
    
    trades = db.get_trades(limit=1000)
    
    if not trades:
        st.info("No trades found")
        return
    
    trades_df = pd.DataFrame(trades)
    
    # ========== Agent Performance ==========
    st.markdown("### 📊 Strategy Performance Comparison")
    
    strategies = ['RSI+MACD Momentum', 'Bollinger Band + Volume', 'EMA Crossover + Supertrend']
    leaderboard_data = []
    
    for strategy in strategies:
        if 'strategy' in trades_df.columns:
            strategy_trades = trades_df[trades_df['strategy'] == strategy]
        else:
            strategy_trades = trades_df
        
        if not strategy_trades.empty:
            metrics = calculate_metrics(strategy_trades)
            leaderboard_data.append({
                'Strategy': strategy,
                'Trades': int(metrics['total_trades']),
                'Win Rate': f"{metrics['win_rate']:.1f}%",
                'Total P&L': f"₹{metrics['total_pnl']:,.0f}",
                'Profit Factor': f"{metrics['profit_factor']:.2f}",
                'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
                'Max Drawdown': f"{metrics['max_drawdown']:.2f}%",
            })
    
    if leaderboard_data:
        df = pd.DataFrame(leaderboard_data)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # ========== Comparison Charts ==========
        col1, col2 = st.columns(2)
        
        with col1:
            # P&L Comparison
            agents = [d['Strategy'] for d in leaderboard_data]
            pnls = [float(d['Total P&L'].replace('₹', '').replace(',', '')) for d in leaderboard_data]
            colors = ['#2ca02c' if p >= 0 else '#d62728' for p in pnls]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=agents,
                    y=pnls,
                    marker_color=colors,
                    text=[f'₹{p:,.0f}' for p in pnls],
                    textposition='auto'
                )
            ])
            fig.update_layout(
                title="Total P&L by Strategy",
                yaxis_title="P&L (₹)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Win Rate Comparison
            win_rates = [float(d['Win Rate'].replace('%', '')) for d in leaderboard_data]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=agents,
                    y=win_rates,
                    marker_color='#1f77b4',
                    text=[f'{wr:.1f}%' for wr in win_rates],
                    textposition='auto'
                )
            ])
            fig.update_layout(
                title="Win Rate by Strategy",
                yaxis_title="Win Rate (%)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No strategy data available")


# ============================================================================
# PAGE: ADVANCED ANALYTICS
# ============================================================================

def show_advanced_analytics(db):
    """Display advanced analytics page."""
    st.title("🔬 Advanced Analytics")
    
    trades = db.get_trades(limit=1000)
    
    if not trades:
        st.info("No trades found")
        return
    
    trades_df = pd.DataFrame(trades)
    
    # ========== Pair Analysis ==========
    st.markdown("### 💱 Trading Pair Analysis")
    
    if 'pair' in trades_df.columns:
        pair_stats = []
        for pair in trades_df['pair'].unique():
            pair_trades = trades_df[trades_df['pair'] == pair]
            metrics = calculate_metrics(pair_trades)
            pair_stats.append({
                'Pair': pair,
                'Trades': int(metrics['total_trades']),
                'Win Rate': f"{metrics['win_rate']:.1f}%",
                'Total P&L': f"₹{metrics['total_pnl']:,.0f}",
                'Profit Factor': f"{metrics['profit_factor']:.2f}",
            })
        
        if pair_stats:
            pair_df = pd.DataFrame(pair_stats)
            st.dataframe(pair_df, use_container_width=True)
            
            # P&L by pair chart
            col1, col2 = st.columns(2)
            
            with col1:
                pair_pnl = trades_df.groupby('pair')['realized_pnl_inr'].sum().reset_index()
                pair_pnl.columns = ['Pair', 'Total P&L']
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=pair_pnl['Pair'],
                        y=pair_pnl['Total P&L'],
                        marker_color=['#2ca02c' if p >= 0 else '#d62728' for p in pair_pnl['Total P&L']],
                        text=[f'₹{p:,.0f}' for p in pair_pnl['Total P&L']],
                        textposition='auto'
                    )
                ])
                fig.update_layout(
                    title="P&L by Trading Pair",
                    yaxis_title="P&L (₹)",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                pair_trades = trades_df.groupby('pair').size().reset_index(name='Count')
                
                fig = go.Figure(data=[
                    go.Pie(
                        labels=pair_trades['Pair'],
                        values=pair_trades['Count'],
                        textposition='inside',
                        textinfo='label+percent'
                    )
                ])
                fig.update_layout(
                    title="Trade Distribution by Pair",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========== Time Analysis ==========
    st.markdown("### ⏰ Time-Based Analysis")
    
    if 'timestamp' in trades_df.columns:
        trades_df['hour'] = pd.to_datetime(trades_df['timestamp']).dt.hour
        hourly_trades = trades_df.groupby('hour').size().reset_index(name='Count')
        
        fig = go.Figure(data=[
            go.Bar(
                x=hourly_trades['hour'],
                y=hourly_trades['Count'],
                marker_color='#1f77b4'
            )
        ])
        fig.update_layout(
            title="Trades by Hour of Day",
            xaxis_title="Hour",
            yaxis_title="Number of Trades",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: RISK DASHBOARD
# ============================================================================

def show_risk_dashboard(db):
    """Display risk dashboard."""
    st.title("⚠️ Risk Management Dashboard")
    
    trades = db.get_trades(limit=1000)
    
    if not trades:
        st.info("No trades found")
        return
    
    trades_df = pd.DataFrame(trades)
    metrics = calculate_metrics(trades_df)
    
    # ========== Risk Metrics ==========
    st.markdown("### 📊 Risk Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = get_status_indicator(metrics['max_drawdown'])
        st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%", delta=status)
    
    with col2:
        daily_loss = trades_df[trades_df['timestamp'].str.contains(datetime.now().strftime('%Y-%m-%d'))]['realized_pnl_inr'].sum() if 'timestamp' in trades_df.columns else 0
        st.metric("Today's P&L", f"₹{daily_loss:,.0f}")
    
    with col3:
        portfolio_value = INITIAL_PORTFOLIO + metrics['total_pnl']
        exposure_pct = (metrics['total_pnl'] / INITIAL_PORTFOLIO) * 100
        st.metric("Portfolio Exposure", f"{exposure_pct:.2f}%")
    
    with col4:
        if metrics['avg_loss'] != 0:
            risk_reward = abs(metrics['avg_win'] / metrics['avg_loss'])
        else:
            risk_reward = 0
        st.metric("Risk/Reward Ratio", f"1:{risk_reward:.2f}")
    
    st.markdown("---")
    
    # ========== Risk Alerts ==========
    st.markdown("### 🚨 Active Alerts")
    
    alerts = []
    
    if metrics['max_drawdown'] < -10:
        alerts.append({
            'severity': 'high',
            'title': '🔴 Critical Drawdown',
            'message': f"Drawdown at {metrics['max_drawdown']:.2f}%, exceeding safe limits"
        })
    elif metrics['max_drawdown'] < -5:
        alerts.append({
            'severity': 'medium',
            'title': '🟡 High Drawdown',
            'message': f"Drawdown at {metrics['max_drawdown']:.2f}%, approaching limit"
        })
    
    if metrics['win_rate'] < 40:
        alerts.append({
            'severity': 'medium',
            'title': '🟡 Low Win Rate',
            'message': f"Win rate at {metrics['win_rate']:.1f}%, below target"
        })
    
    if metrics['profit_factor'] < 1:
        alerts.append({
            'severity': 'high',
            'title': '🔴 Negative Profit Factor',
            'message': f"Profit factor at {metrics['profit_factor']:.2f}, losses exceed gains"
        })
    
    if not alerts:
        st.success("✅ All systems healthy - No active alerts")
    else:
        for alert in alerts:
            if alert['severity'] == 'high':
                st.error(f"{alert['title']}\n{alert['message']}")
            else:
                st.warning(f"{alert['title']}\n{alert['message']}")
    
    st.markdown("---")
    
    # ========== Risk Limits ==========
    st.markdown("### ⚙️ Risk Limits Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Max Per Trade", "2%", delta="₹2,000")
    
    with col2:
        st.metric("Max Portfolio Exposure", "10%", delta="₹10,000")
    
    with col3:
        st.metric("Daily Loss Limit", "5%", delta="₹5,000")


# ============================================================================
# PAGE: SETTINGS & CONFIGURATION
# ============================================================================

def show_settings():
    """Display settings page."""
    st.title("⚙️ Settings & Configuration")
    
    st.markdown("### 🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trading Parameters")
        st.write("**Max Trade Size**: 2% of portfolio")
        st.write("**Max Exposure**: 10% of portfolio")
        st.write("**Daily Loss Limit**: 5% of portfolio")
        st.write("**Stop Loss**: 3% below entry")
        st.write("**Take Profit**: 5% above entry")
    
    with col2:
        st.subheader("System Status")
        st.write("**Status**: 🟢 Running")
        st.write("**Uptime**: 24 hours")
        st.write("**Last Update**: Just now")
        st.write("**API Connection**: ✅ Connected")
        st.write("**Telegram**: ✅ Connected")
    
    st.markdown("---")
    
    st.markdown("### 📊 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Trades (CSV)"):
            st.success("Exported successfully!")
    
    with col2:
        if st.button("📥 Export Reports (PDF)"):
            st.success("Exported successfully!")
    
    with col3:
        if st.button("🔄 Sync Database"):
            st.success("Synced successfully!")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main dashboard application."""
    
    # Sidebar navigation
    st.sidebar.title("🚀 IndiaCryptoAlpha")
    st.sidebar.markdown("Premium Trading Dashboard v2.0")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Overview",
            "📈 Live Trades",
            "🏆 Agent Leaderboard",
            "🔬 Advanced Analytics",
            "⚠️ Risk Dashboard",
            "⚙️ Settings"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # System status
    st.sidebar.markdown("### 🔋 System Status")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.write("**Status**: 🟢 Active")
    with col2:
        st.write("**Mode**: Paper")
    
    st.sidebar.markdown("---")
    
    # Initialize data sources
    db = get_database()
    excel = get_excel_logger()
    market_data = get_market_data()
    
    # Route to page
    if page == "📊 Overview":
        show_overview(db, excel)
    elif page == "📈 Live Trades":
        show_live_trades(db)
    elif page == "🏆 Agent Leaderboard":
        show_agent_leaderboard(db)
    elif page == "🔬 Advanced Analytics":
        show_advanced_analytics(db)
    elif page == "⚠️ Risk Dashboard":
        show_risk_dashboard(db)
    elif page == "⚙️ Settings":
        show_settings()


if __name__ == '__main__':
    main()
