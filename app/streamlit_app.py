"""Professional multi-market Streamlit dashboard for the Trading Assistant."""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.catalog import EXCHANGES, POPULAR_TICKERS
from src.data.company import get_analyst_consensus, get_company_snapshot
from src.data.market_data import get_latest_quote, get_price_history, normalize_ticker
from src.indicators.technical import add_technical_indicators, latest_indicator_values
from src.ml.composite import composite_ai_score
from src.risk.leverage import leverage_plan
from src.signals.signal_engine import build_signal

st.set_page_config(page_title="Trading Assistant", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.1rem;padding-bottom:3rem}
.hero{padding:.4rem 0 1rem}.hero h1{font-size:2.45rem;margin:0}.hero p{opacity:.68;margin:.2rem 0 0}
[data-testid="stMetricValue"]{font-size:1.45rem}
.card{border:1px solid rgba(128,128,128,.22);border-radius:14px;padding:16px;background:rgba(128,128,128,.035)}
.pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;border:1px solid rgba(128,128,128,.28);margin-right:.35rem;font-size:.8rem}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>📈 Trading Assistant</h1><p>Multi-market research · fundamentals · analyst consensus · technicals · AI-style scoring · leverage scenarios</p></div>', unsafe_allow_html=True)
st.caption("Educational research tool only. Not investment advice. Market data may be delayed, incomplete, or unavailable for some listings.")

with st.sidebar:
    st.header("🌍 Market")
    exchange = st.selectbox("Trading exchange", list(EXCHANGES), format_func=lambda x: f"{EXCHANGES[x].name} · {EXCHANGES[x].country}")
    favorites = POPULAR_TICKERS.get(exchange, {})
    company_choice = st.selectbox("Company", ["Custom ticker"] + list(favorites))
    default = favorites.get(company_choice, "CRWD" if exchange == "NYSE" else "")
    ticker_input = st.text_input("Ticker", value=default, max_chars=20, help="Examples: CRWD, AZN.L, SAP.DE, ITX.MC, MC.PA")
    period = st.selectbox("History", ["6mo", "1y", "2y", "5y", "10y", "max"], index=1)
    analyze = st.button("🔎 Analyze company", type="primary", use_container_width=True)
    st.divider()
    st.subheader("Chart overlays")
    show_sma20 = st.checkbox("SMA 20", True)
    show_sma50 = st.checkbox("SMA 50", True)
    show_sma200 = st.checkbox("SMA 200", True)
    st.divider()
    st.caption("Supported markets")
    for item in EXCHANGES.values():
        st.write(f"• {item.name}")


def analyze_market(symbol: str, selected_period: str):
    symbol = normalize_ticker(symbol)
    prices = get_price_history(symbol, period=selected_period)
    analyzed = add_technical_indicators(prices)
    quote = get_latest_quote(analyzed)
    indicators = latest_indicator_values(analyzed)
    signal = build_signal(indicators)
    company = get_company_snapshot(symbol)
    analyst = get_analyst_consensus(symbol)
    ai = composite_ai_score(indicators, company, analyst)
    try:
        balance = yf.Ticker(symbol).balance_sheet
    except Exception:
        balance = pd.DataFrame()
    return symbol, analyzed, quote, indicators, signal, company, analyst, ai, balance


if analyze:
    try:
        result = analyze_market(ticker_input, period)
        st.session_state["analysis"] = dict(zip(["symbol","analyzed","quote","indicators","signal","company","analyst","ai","balance"], result))
    except Exception as exc:  # noqa: BLE001
        st.session_state.pop("analysis", None)
        st.error(f"Nu am putut analiza {ticker_input.strip().upper()}: {exc}")

analysis = st.session_state.get("analysis")
if not analysis:
    st.info("Alege bursa, compania și apasă **Analyze company**.")
    a,b,c,d,e = st.columns(5)
    a.metric("Exchanges", "5")
    b.metric("Companies", "25+")
    c.metric("Research", "Multi-factor")
    d.metric("Analysts", "Buy/Hold/Sell")
    e.metric("Risk", "Long / Short")
    st.markdown("### Ce poți face")
    st.markdown("Selectezi **NYSE → CrowdStrike (CRWD)** sau o companie din LSE, Germania, Spania ori Franța și primești într-un singur loc prețul, indicatorii tehnici, evaluarea companiei, date de bilanț, consensul analiștilor și un simulator de leverage.")
    st.stop()

symbol=analysis["symbol"]; analyzed=analysis["analyzed"]; quote=analysis["quote"]; indicators=analysis["indicators"]
signal=analysis["signal"]; company=analysis["company"]; analyst=analysis["analyst"]; ai=analysis["ai"]; balance=analysis["balance"]

st.markdown(f'<span class="pill">{symbol}</span><span class="pill">{company.get("sector") or "Sector —"}</span><span class="pill">{company.get("industry") or "Industry —"}</span>', unsafe_allow_html=True)
st.subheader(company.get("name", symbol))

m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Latest close", f"{quote['latest_close']:.2f}", f"{quote['change_percent']:.2f}%")
m2.metric("Research score", f"{ai['score']:.0f}/100", ai["label"])
m3.metric("P/E", f"{company['pe']:.1f}" if company.get("pe") is not None else "—")
m4.metric("Forward P/E", f"{company['forward_pe']:.1f}" if company.get("forward_pe") is not None else "—")
m5.metric("Analyst views", str(analyst.get("total",0)) if analyst.get("total") else "—")

chart_tab, company_tab, analyst_tab, risk_tab, data_tab = st.tabs(["📊 Price & technicals","🏢 Company & balance sheet","👥 Analyst consensus","⚡ Leverage simulator","📋 Raw data"])

with chart_tab:
    fig = go.Figure(go.Candlestick(x=analyzed["Date"], open=analyzed["Open"], high=analyzed["High"], low=analyzed["Low"], close=analyzed["Close"], name="Price"))
    for enabled, col, name in [(show_sma20,"SMA_20","SMA 20"),(show_sma50,"SMA_50","SMA 50"),(show_sma200,"SMA_200","SMA 200")]:
        if enabled: fig.add_trace(go.Scatter(x=analyzed["Date"], y=analyzed[col], name=name, mode="lines"))
    fig.update_layout(height=560, xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=25,b=10), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    a,b,c,d = st.columns(4)
    a.metric("RSI 14", f"{indicators['rsi_14']:.1f}" if indicators.get("rsi_14") == indicators.get("rsi_14") else "—")
    b.metric("ATR 14", f"{indicators['atr_14']:.2f}" if indicators.get("atr_14") == indicators.get("atr_14") else "—")
    c.metric("Relative volume", f"{indicators['relative_volume']:.2f}x" if indicators.get("relative_volume") == indicators.get("relative_volume") else "—")
    d.metric("Technical signal", signal.label)
    with st.expander("Why this signal?"):
        for reason in signal.reasons: st.write(f"• {reason}")
        for note in signal.risk_notes: st.caption(note)
    st.caption(f"Score components — Technical {ai['technical']:.0f} · Fundamental {ai['fundamental']:.0f} · Analyst {ai['analyst']:.0f}")

with company_tab:
    left,right=st.columns([1.3,1])
    with left:
        st.markdown(company.get("description", ""))
        st.write(f"**Sector:** {company.get('sector') or '—'} · **Industry:** {company.get('industry') or '—'} · **Country:** {company.get('country') or '—'}")
        rows={"Market cap":company.get("market_cap"),"Profit margin":company.get("profit_margin"),"Operating margin":company.get("operating_margin"),"ROE":company.get("roe"),"Revenue growth":company.get("revenue_growth"),"Earnings growth":company.get("earnings_growth"),"Debt / equity":company.get("debt_to_equity"),"Current ratio":company.get("current_ratio"),"Free cash flow":company.get("free_cash_flow")}
        display=[]
        for label,value in rows.items():
            if isinstance(value,(int,float)):
                if label in {"Profit margin","Operating margin","ROE","Revenue growth","Earnings growth"}: value=f"{value:.1%}"
                elif label in {"Market cap","Free cash flow"}: value=f"{value:,.0f}"
                else: value=f"{value:.2f}"
            display.append({"Metric":label,"Value":value if value is not None else "—"})
        st.dataframe(pd.DataFrame(display),hide_index=True,use_container_width=True)
    with right:
        st.markdown("### Valuation")
        for label,key in [("P/E","pe"),("Forward P/E","forward_pe"),("PEG","peg"),("Price / Book","price_to_book"),("Dividend yield","dividend_yield")]:
            value=company.get(key)
            if key=="dividend_yield" and isinstance(value,(int,float)): text=f"{value:.2%}"
            else: text=f"{value:.2f}" if isinstance(value,(int,float)) else "—"
            st.metric(label,text)
        st.markdown("### Balance sheet")
        if not balance.empty:
            bs=balance.iloc[:8].copy()
            bs.index=[str(x) for x in bs.index]
            st.dataframe(bs,use_container_width=True)
        else:
            st.info("Balance-sheet data is not available for this listing/provider response.")

with analyst_tab:
    counts=analyst["counts"]
    cols=st.columns(5)
    for col,label,key in zip(cols,["Strong Buy","Buy","Hold","Sell","Strong Sell"],["strong_buy","buy","hold","sell","strong_sell"]): col.metric(label,counts.get(key,0))
    st.progress(max(0,min(1,(analyst.get("consensus_score",0)+2)/4)),text=f"Consensus: {analyst.get('label','Neutral')} · score {analyst.get('consensus_score',0):+.2f}")
    st.markdown("### Price targets")
    cols=st.columns(5)
    for col,label,key in zip(cols,["Low","Mean","Median","High","Current"],["low","mean","median","high","current"]):
        value=analyst.get(key); col.metric(label,f"{value:.2f}" if isinstance(value,(int,float)) else "—")
    st.caption("Analyst coverage varies by company and listing. Consensus is an external input, not a guarantee.")

with risk_tab:
    st.warning("Leverage magnifies gains and losses. This calculator is an educational paper-trading scenario and excludes fees, financing, slippage, liquidation and broker-specific margin rules.")
    c1,c2,c3=st.columns(3)
    side=c1.selectbox("Position",["LONG","SHORT"]); capital=c1.number_input("Capital",min_value=1.0,value=10000.0,step=500.0)
    entry=c2.number_input("Entry price",min_value=0.01,value=float(quote["latest_close"]),step=max(.01,float(quote["latest_close"])/100)); leverage=c2.slider("Leverage",1.0,20.0,3.0,.5)
    stop=c3.number_input("Stop loss (%)",min_value=.1,value=3.0,step=.5); target=c3.number_input("Take profit (%)",min_value=.1,value=6.0,step=.5)
    plan=leverage_plan(side,entry,leverage,stop,target,capital)
    p1,p2,p3,p4,p5=st.columns(5)
    p1.metric("Notional",f"{plan['notional']:,.2f}"); p2.metric("Units",f"{plan['units']:,.3f}"); p3.metric("Stop",f"{plan['stop']:.2f}"); p4.metric("Target",f"{plan['target']:.2f}"); p5.metric("Reward / risk",f"{plan['reward_risk']:.2f}x")
    x,y=st.columns(2); x.metric("Approx. loss at SL",f"-{plan['max_loss']:,.2f}"); y.metric("Approx. profit at TP",f"+{plan['potential_profit']:,.2f}")

with data_tab:
    st.dataframe(analyzed.tail(50),use_container_width=True,hide_index=True)
