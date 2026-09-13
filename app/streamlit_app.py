"""Streamlit dashboard for the educational Trading Assistant."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.market_data import get_latest_quote, get_price_history, normalize_ticker
from src.indicators.technical import add_technical_indicators, latest_indicator_values
from src.risk.position_sizing import (
    atr_stop_reference,
    calculate_position_size,
    calculate_risk_amount,
)
from src.signals.signal_engine import build_signal

st.set_page_config(page_title="Trading Assistant", page_icon="📈", layout="wide")

# Lightweight, professional styling that works on Streamlit Community Cloud.
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    [data-testid="stMetricValue"] {font-size: 1.65rem;}
    .disclaimer {font-size: 0.85rem; opacity: 0.78;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📈 Trading Assistant")
st.caption("Technical market analysis and paper-trading references for educational use.")
st.markdown(
    '<div class="disclaimer">No brokerage execution, real-money orders, or investment recommendations. '
    'Market data may be delayed or incomplete.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Market")
    ticker_input = st.text_input(
        "Ticker symbol",
        value="SPY",
        max_chars=20,
        help="Examples: AAPL, MSFT, NVDA, SPY, BTC-USD",
    )
    period = st.selectbox("History", ["6mo", "1y", "2y", "5y", "10y", "max"], index=1)

    st.header("Chart overlays")
    show_sma_20 = st.checkbox("SMA 20", value=True)
    show_sma_50 = st.checkbox("SMA 50", value=True)
    show_sma_200 = st.checkbox("SMA 200", value=True)

    analyze = st.button("Analyze", type="primary", use_container_width=True)


def analyze_market(ticker: str, selected_period: str):
    symbol = normalize_ticker(ticker)
    with st.spinner(f"Loading {symbol} market data..."):
        prices = get_price_history(ticker=symbol, period=selected_period)
        analyzed = add_technical_indicators(prices)
        quote = get_latest_quote(analyzed)
        indicator_values = latest_indicator_values(analyzed)
        signal = build_signal(indicator_values)
    return symbol, analyzed, quote, indicator_values, signal


# Persist analysis between Streamlit reruns so form submissions do not blank the dashboard.
if analyze:
    try:
        symbol, analyzed, quote, indicator_values, signal = analyze_market(ticker_input, period)
        st.session_state["analysis"] = {
            "symbol": symbol,
            "analyzed": analyzed,
            "quote": quote,
            "indicators": indicator_values,
            "signal": signal,
            "period": period,
        }
    except Exception as error:  # noqa: BLE001 - surface user-friendly dashboard errors
        st.session_state.pop("analysis", None)
        st.error(f"Could not analyze '{ticker_input.strip().upper()}': {error}")

analysis = st.session_state.get("analysis")

if analysis:
    symbol = analysis["symbol"]
    analyzed = analysis["analyzed"]
    quote = analysis["quote"]
    indicator_values = analysis["indicators"]
    signal = analysis["signal"]

    st.subheader(f"{symbol} overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Latest close", f"{quote['latest_close']:.2f}", f"{quote['change_percent']:.2f}%")
    m2.metric("RSI (14)", f"{indicator_values['rsi_14']:.2f}")
    m3.metric("ATR (14)", f"{indicator_values['atr_14']:.2f}")
    m4.metric("Relative volume", f"{indicator_values['relative_volume']:.2f}x")

    chart_tab, signal_tab, risk_tab, data_tab = st.tabs(
        ["📊 Chart", "🧭 Signal", "🛡️ Risk reference", "📋 Data"]
    )

    with chart_tab:
        figure = go.Figure(
            go.Candlestick(
                x=analyzed["Date"],
                open=analyzed["Open"],
                high=analyzed["High"],
                low=analyzed["Low"],
                close=analyzed["Close"],
                name="Price",
            )
        )
        if show_sma_20:
            figure.add_trace(go.Scatter(x=analyzed["Date"], y=analyzed["SMA_20"], name="SMA 20"))
        if show_sma_50:
            figure.add_trace(go.Scatter(x=analyzed["Date"], y=analyzed["SMA_50"], name="SMA 50"))
        if show_sma_200:
            figure.add_trace(go.Scatter(x=analyzed["Date"], y=analyzed["SMA_200"], name="SMA 200"))
        figure.update_layout(
            height=560,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=30, b=10),
            hovermode="x unified",
        )
        st.plotly_chart(figure, use_container_width=True)

    with signal_tab:
        left, right = st.columns([1, 2])
        with left:
            st.metric("Analysis signal", signal.label)
            st.metric("Signal score", signal.score)
        with right:
            st.markdown("**Why this signal?**")
            for reason in signal.reasons:
                st.write(f"• {reason}")
            if signal.risk_notes:
                st.markdown("**Risk notes**")
                for note in signal.risk_notes:
                    st.write(f"• {note}")

    with risk_tab:
        stop_reference = atr_stop_reference(quote["latest_close"], indicator_values["atr_14"])
        st.info(f"Educational 1.5 × ATR long-stop reference: **{stop_reference:.2f}**")
        st.caption("This is a risk-calculation reference for paper trading, not a trading instruction.")

        with st.form("position_sizing_form"):
            c1, c2 = st.columns(2)
            with c1:
                account_value = st.number_input(
                    "Paper account value",
                    min_value=1.0,
                    value=10000.0,
                    step=100.0,
                )
                risk_percent = st.number_input(
                    "Risk per paper trade (%)",
                    min_value=0.1,
                    max_value=10.0,
                    value=1.0,
                    step=0.1,
                )
            with c2:
                entry_price = st.number_input(
                    "Reference entry price",
                    min_value=0.01,
                    value=float(quote["latest_close"]),
                    step=0.01,
                )
                stop_price = st.number_input(
                    "Reference stop price",
                    min_value=0.01,
                    value=float(max(0.01, quote["latest_close"] - indicator_values["atr_14"] * 1.5)),
                    step=0.01,
                )
            submitted = st.form_submit_button("Calculate reference", use_container_width=True)

        if submitted:
            risk_amount = calculate_risk_amount(account_value, risk_percent)
            shares = calculate_position_size(account_value, risk_percent, entry_price, stop_price)
            r1, r2 = st.columns(2)
            r1.metric("Maximum paper-trade risk", f"{risk_amount:.2f}")
            r2.metric("Whole-share reference size", f"{shares}")

    with data_tab:
        st.caption(f"Showing the latest 10 analyzed rows from the selected {analysis['period']} history.")
        st.dataframe(analyzed.tail(10), use_container_width=True, hide_index=True)
else:
    st.info("Enter a ticker in the sidebar and click **Analyze** to begin.")
    st.subheader("What this dashboard covers")
    overview = st.columns(3)
    overview[0].markdown("**Market data**\n\nHistorical OHLCV prices via `yfinance`.")
    overview[1].markdown("**Technical analysis**\n\nSMA, EMA, RSI, MACD, Bollinger Bands, ATR and relative volume.")
    overview[2].markdown("**Risk references**\n\nExplainable signals and educational paper-trading position sizing.")
