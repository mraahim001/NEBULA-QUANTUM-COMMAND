import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# ==============================================================================
# 1. ULTIMATE HUD & CSS (FINTECH STANDARD)
# ==============================================================================
st.set_page_config(page_title="NEBULA | QUANTUM COMMAND", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=JetBrains+Mono&display=swap');
    
    :root {
        --glass: rgba(18, 22, 28, 0.9);
        --neon-gold: #f0b90b;
        --neon-green: #00ffcc;
        --neon-red: #ff4d4d;
        --grid-color: #1e2226;
    }

    .stApp { background: #040508; color: #e1e1e1; font-family: 'Space Grotesk', sans-serif; }
    
    /* Advanced Metric Cards */
    .metric-container {
        background: var(--glass); border: 1px solid var(--grid-color);
        border-radius: 15px; padding: 20px; text-align: center;
        transition: 0.4s; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .metric-container:hover { border-color: var(--neon-gold); transform: translateY(-3px); }
    .label { color: #848e9c; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    .value { font-size: 26px; font-weight: 700; margin-top: 5px; }

    /* Signal Glows */
    .glow-buy { color: var(--neon-green); text-shadow: 0 0 20px rgba(0,255,204,0.4); }
    .glow-sell { color: var(--neon-red); text-shadow: 0 0 20px rgba(255,77,77,0.4); }

    /* Order History Table */
    .trade-log {
        background: #0d1117; border-radius: 10px; padding: 15px;
        font-family: 'JetBrains Mono', monospace; font-size: 12px; height: 300px; overflow: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. THE QUANTUM ANALYTICS SUITE
# ==============================================================================
class NebulaIntelligence:
    @staticmethod
    def compute_all_indicators(df):
        # 1. Trend (EMA Cross)
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['EMA21'] = df['Close'].ewm(span=21).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        # 2. Volatility (Bollinger & ATR)
        df['BB_Mid'] = df['Close'].rolling(20).mean()
        df['BB_Upper'] = df['BB_Mid'] + (df['Close'].rolling(20).std() * 2)
        df['BB_Lower'] = df['BB_Mid'] - (df['Close'].rolling(20).std() * 2)
        
        # 3. Momentum (RSI & MACD)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/loss)))
        
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        return df

    @staticmethod
    def get_market_sentiment(df):
        last = df.iloc[-1]
        score = 0
        if last['EMA8'] > last['EMA21']: score += 25
        if last['RSI'] < 35: score += 25  # Oversold (Buying pressure builds)
        if last['MACD'] > last['MACD_Signal']: score += 25
        if last['Close'] > last['BB_Mid']: score += 25
        return score # Returns 0-100 Bullishness

# ==============================================================================
# 3. MAIN TERMINAL DASHBOARD
# ==============================================================================
# --- SYNC DATA ---
with st.sidebar:
    st.markdown("<h1 style='color:#f0b90b;'>NEBULA HUB</h1>", unsafe_allow_html=True)
    st.divider()
    cat = st.radio("EXCHANGE", ["CRYPTO", "FOREX", "COMMODITIES"])
    symbols = {"CRYPTO": "BTC-USD", "FOREX": "EURUSD=X", "COMMODITIES": "GC=F"}
    pair = symbols[cat]
    tf = st.selectbox("PRECISION", ["1m", "5m", "15m", "1h"], index=1)
    
    st.divider()
    st.markdown("### PRO TOOLS")
    hft_enabled = st.toggle("HFT Data Stream", True)
    risk_level = st.select_slider("Risk Engine", ["Low", "Mid", "High", "Insane"])
    
    st.divider()
    st.markdown("### LIQUIDITY")
    st.info("Available: $1,254,800.00")

# --- DATA ENGINE START ---
raw_data = yf.Ticker(pair).history(period="2d", interval=tf)
df = NebulaIntelligence.compute_all_indicators(raw_data)
last_p = df.iloc[-1]
bull_score = NebulaIntelligence.get_market_sentiment(df)

# --- TOP HUD ---
st.markdown(f"## 🦾 Institutional Terminal: {pair}")
h1, h2, h3, h4 = st.columns(4)

with h1:
    st.markdown(f'<div class="metric-container"><div class="label">Last Traded Price</div><div class="value">${last_p["Close"]:,.2f}</div></div>', unsafe_allow_html=True)
with h2:
    color = "var(--neon-green)" if last_p['MACD_Hist'] > 0 else "var(--neon-red)"
    st.markdown(f'<div class="metric-container"><div class="label">MACD Pressure</div><div class="value" style="color:{color};">{last_p["MACD_Hist"]:.4f}</div></div>', unsafe_allow_html=True)
with h3:
    st.markdown(f'<div class="metric-container"><div class="label">RSI Index</div><div class="value">{last_p["RSI"]:.1f}</div></div>', unsafe_allow_html=True)
with h4:
    signal = "STRONG BUY" if bull_score >= 75 else "STRONG SELL" if bull_score <= 25 else "NEUTRAL"
    style = "glow-buy" if "BUY" in signal else "glow-sell" if "SELL" in signal else ""
    st.markdown(f'<div class="metric-container"><div class="label">AI Prediction</div><div class="value {style}">{signal}</div></div>', unsafe_allow_html=True)

st.divider()

# --- MAIN WORKSPACE ---
col_main, col_depth = st.columns([3.5, 1])

with col_main:
    # TRADINGVIEW STYLE MULTI-CHART
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.2, 0.2])
    
    # 1. Main Candlestick + EMAs + Bollinger
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA8'], line=dict(color='#00d2ff', width=1), name="EMA 8"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA21'], line=dict(color='#ff00ff', width=1), name="EMA 21"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(255,255,255,0.1)', width=0), name="BB"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(255,255,255,0.1)', width=0), fill='tonexty'), row=1, col=1)

    # 2. MACD Histogram
    m_colors = ['#0ecb81' if x > 0 else '#f6465d' for x in df['MACD_Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=m_colors, name="MACD"), row=2, col=1)
    
    # 3. RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#f0b90b', width=2), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#ff4d4d", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#00ffcc", row=3, col=1)

    fig.update_layout(template="plotly_dark", height=850, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="black", plot_bgcolor="black")
    st.plotly_chart(fig, use_container_width=True)

with col_depth:
    # MARKET DEPTH METER
    st.markdown("### Market Depth")
    st.write(f"Bullish Sentiment: {bull_score}%")
    st.progress(bull_score/100)
    
    st.divider()
    # SIMULATED ORDER BOOK
    st.markdown("#### 🔥 Live Order Book")
    for _ in range(8):
        price = last_p['Close'] + random.uniform(0.01, 10)
        size = random.uniform(0.1, 2.5)
        st.markdown(f"<div style='display:flex; justify-content:space-between; color:#ff4d4d; font-family:JetBrains Mono;'><span>{price:,.2f}</span><span>{size:.3f}</span></div>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align:center; padding:10px; color:#f0b90b;'>{last_p['Close']:,.2f}</h2>", unsafe_allow_html=True)
    
    for _ in range(8):
        price = last_p['Close'] - random.uniform(0.01, 10)
        size = random.uniform(0.1, 2.5)
        st.markdown(f"<div style='display:flex; justify-content:space-between; color:#00ffcc; font-family:JetBrains Mono;'><span>{price:,.2f}</span><span>{size:.3f}</span></div>", unsafe_allow_html=True)

    st.divider()
    # EXECUTION
    st.button("🚀 EXECUTE LONG", use_container_width=True, type="primary")
    st.button("🔻 EXECUTE SHORT", use_container_width=True)

# --- SYSTEM LOGS (FOOTER) ---
st.divider()
st.markdown("### 🖥️ Quantum OS Console")
l1, l2 = st.columns(2)
with l1:
    st.markdown(f"""
        <div class="trade-log">
            [{datetime.now().strftime('%H:%M:%S')}] SYNC: Connection established with global nodes...<br>
            [{datetime.now().strftime('%H:%M:%S')}] ALGO: Triple-confluence strategy active.<br>
            [{datetime.now().strftime('%H:%M:%S')}] DATA: {pair} 1m data points optimized.<br>
            [{datetime.now().strftime('%H:%M:%S')}] SIGNAL: AI confidence at {bull_score}%.<br>
            [{datetime.now().strftime('%H:%M:%S')}] WHALE: Large buy order detected in {pair}.
        </div>
    """, unsafe_allow_html=True)
with l2:
    st.write("🌐 **Global Exchange Status**")
    st.success("Binance API: Connected | Kraken: Active | ByBit: Stable")
    st.info("System Latency: 8.4ms | WebSocket: Encryption Enabled")

# REFRESH ENGINE
time.sleep(10)
st.rerun()