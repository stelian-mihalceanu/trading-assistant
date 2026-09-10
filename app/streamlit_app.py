"""Streamlit entry point for the educational trading assistant."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.market_data import get_latest_quote, get_price_history
from src.indicators.technical import add_technical_indicators, latest_indicator_values
from src.risk.position_sizing import atr_stop_reference, calculate_position_size, calculate_risk_amount
from src.signals.signal_engine import build_signal

st.set_page_config(page_title="Trading Assistant", page_icon="📈", layout="wide")

st.title("📈 Trading Assistant")
st.caption("Educational market analysis and paper-trading references — not financial advice.")
st.warning(
    "This application is for educational and informational purposes only. It does not provide investment advice "
    "and does not execute real-money trades. Verify data independently before making any financial decision."
)

with st.sidebar:
    st.header("Analysis settings")
    ticker = st.text_input("Ticker", value="SPY", help="Examples: AAPL, MSFT, NVDA, SPY, BTC-USD")
    period = st.selectbox("History period", ["6mo", "1y", "2y", "5y", "10y", "max"], index=1)
    show_sma_20 = st.checkbox("Show SMA 20", value=True)
    show_sma_50 = st.checkbox("Show SMA 50", value=True)
    show_sma_200 = st.checkbox("Show SMA 200", value=True)
    load_data = st.button("Analyze market data", type="primary")

if load_data:
    try:
        with st.spinner("Downloading and analyzing market data..."):
            prices = get_price_history(ticker=ticker, period=period)
            analyzed = add_technical_indicators(prices)
            quote = get_latest_quote(analyzed)
            indicator_values = latest_indicator_values(analyzed)
            signal = build_signal(indicator_values)

        st.subheader(f"{ticker.strip().upper()} overview")
        metric_1, metric_2, metric_3, metric_4 = st.columns(4)
        metric_1.metric("Latest close", f"{quote['latest_close']:.2f}", f"{quote['change_percent']:.2f}%")
        metric_2.metric("RSI (14)", f"{indicator_values['rsi_14']:.2f}")
        metric_3.metric("ATR (14)", f"{indicator_values['atr_14']:.2f}")
        metric_4.metric("Relative volume", f"{indicator_values['relative_volume']:.2f}x")

        st.subheader("Price chart")
        figure = go.Figure()
        figure.add_trace(
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

        figure.update_layout(height=550, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(figure, use_container_width=True)

        left, right = st.columns(2)
        with left:
            st.subheader(f"Analysis signal: {signal.label}")
            st.metric("Signal score", signal.score)
            st.write("**Reasons**")
            for reason in signal.reasons:
                st.write(f"- {reason}")

        with right:
            st.subheader("Risk references")
            for note in signal.risk_notes:
                st.write(f"- {note}")

            if signal.label != "INSUFFICIENT_DATA":
                stop_reference = atr_stop_reference(quote["latest_close"], indicator_values["atr_14"])
                st.write(f"Educational 1.5 × ATR long-stop reference: {stop_reference:.2f}")

        st.subheader("Paper-trading position-size reference")
        with st.form("position_sizing_form"):
            account_value = st.number_input("Paper account value", min_value=1.0, value=10000.0, step=100.0)
            risk_percent = st.number_input("Risk per paper trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
            entry_price = st.number_input("Reference entry price", min_value=0.01, value=float(quote["latest_close"]), step=0.01)
            stop_price = st.number_input("Reference stop price", min_value=0.01, value=float(max(0.01, quote["latest_close"] - indicator_values["atr_14"] * 1.5)), step=0.01)
            submitted = st.form_submit_button("Calculate paper-trade reference")

        if submitted:
            risk_amount = calculate_risk_amount(account_value, risk_percent)
            shares = calculate_position_size(account_value, risk_percent, entry_price, stop_price)
            st.info(
                f"Educational reference only: maximum risk amount = {risk_amount:.2f}; "
                f"whole-share position size = {shares}."
            )

        st.subheader("Latest analyzed rows")
        st.dataframe(analyzed.tail(10), use_container_width=True)

    except Exception as error:
        st.error(f"Could not analyze the requested ticker: {error}")
else:
    st.info("Choose a ticker and click 'Analyze market data' to begin.")
