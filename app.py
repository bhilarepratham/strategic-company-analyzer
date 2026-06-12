import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import sqlite3

from data_collector import CompanyDataCollector
from database_manager import DatabaseManager
from visualizations import DataVisualizer

st.set_page_config(
    page_title="Strategic Company Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    margin: 0.5rem;
}
.metric-value { font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem; }
.metric-label { font-size: 0.9rem; opacity: 0.8; }
.stButton > button {
    background: linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);
    color: white; border: none; border-radius: 25px;
    padding: 0.75rem 2rem; font-weight: bold; transition: all 0.3s ease;
}
.info-box {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    padding: 1.5rem; border-radius: 10px; color: white; margin: 1rem 0;
}
.success-box {
    background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
    padding: 1rem; border-radius: 10px; color: white; margin: 0.5rem 0;
}
.error-box {
    background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
    padding: 1rem; border-radius: 10px; color: white; margin: 0.5rem 0;
}
.description-box {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-left: 4px solid #667eea;
    padding: 1.2rem 1.5rem; border-radius: 0 10px 10px 0;
    color: #333; margin: 1rem 0; font-size: 0.95rem; line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'data_collector' not in st.session_state:
    st.session_state.data_collector = CompanyDataCollector()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = DataVisualizer()


# =============================================================================
# CACHING — wraps DB calls so Streamlit skips the query on re-renders.
# ttl=300 means data is considered fresh for 5 minutes.
# Call bust_cache() after any write so the next render fetches fresh data.
# =============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def cached_get_all_companies():
    return st.session_state.db_manager.get_all_companies()

@st.cache_data(ttl=300, show_spinner=False)
def cached_get_stock_history(symbol: str):
    return st.session_state.db_manager.get_stock_history_by_symbol(symbol)

@st.cache_data(ttl=300, show_spinner=False)
def cached_get_company_count():
    return st.session_state.db_manager.get_company_count()

def bust_cache():
    st.cache_data.clear()


# =============================================================================
# MAIN
# =============================================================================
def main():
    st.markdown('''
    <div class="main-header">📊 Strategic Company Data Analyzer</div>
    <div style="text-align:center; margin-bottom:2rem; color:#666;">
        <i>Professional Financial Data Analysis &amp; Visualization Platform</i>
    </div>''', unsafe_allow_html=True)

    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📥 Data Collection", "📊 Visualizations", "🔍 Company Analysis"]
    )

    total_companies = cached_get_company_count()
    st.sidebar.markdown(f"""
    <div class="info-box">
        <h4>📊 Quick Stats</h4>
        <p>Total Companies: <strong>{total_companies}</strong></p>
        <p>Status: <strong>Active</strong></p>
    </div>""", unsafe_allow_html=True)

    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📥 Data Collection":
        show_data_collection()
    elif page == "📊 Visualizations":
        show_visualizations()
    elif page == "🔍 Company Analysis":
        show_company_analysis()


# =============================================================================
# DASHBOARD
# =============================================================================
def show_dashboard():
    st.markdown("## 🏠 Executive Dashboard")

    all_companies_df = cached_get_all_companies()
    total_companies  = len(all_companies_df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-container">
            <div style="font-size:2rem;">🏢</div>
            <div class="metric-value">{total_companies}</div>
            <div class="metric-label">Total Companies</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        sectors = all_companies_df['sector'].nunique() if not all_companies_df.empty else 0
        st.markdown(f"""<div class="metric-container">
            <div style="font-size:2rem;">🏭</div>
            <div class="metric-value">{sectors}</div>
            <div class="metric-label">Unique Sectors</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        avg_cap = f"${all_companies_df['market_cap'].mean()/1e9:.1f}B" if not all_companies_df.empty else "N/A"
        st.markdown(f"""<div class="metric-container">
            <div style="font-size:2rem;">💰</div>
            <div class="metric-value">{avg_cap}</div>
            <div class="metric-label">Avg Market Cap</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="metric-container">
            <div style="font-size:2rem;">✅</div>
            <div class="metric-value">Online</div>
            <div class="metric-label">System Status</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if not all_companies_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📈 Market Leaders")
            st.plotly_chart(create_market_cap_chart(all_companies_df.head(10)), use_container_width=True)
        with col2:
            st.markdown("### 🎯 Industry Distribution")
            st.plotly_chart(create_pie_chart(all_companies_df), use_container_width=True)

        st.markdown("### 📋 Company Overview")
        display_data_table(all_companies_df)

        # --- CSV export (all companies) ---
        st.markdown("### 💾 Export Data")
        export_df = all_companies_df.copy()
        export_df['market_cap_B'] = (export_df['market_cap'] / 1e9).round(2)
        export_df['revenue_B']    = (export_df['revenue']    / 1e9).round(2)
        export_cols = [
            'symbol', 'company_name', 'sector', 'industry', 'headquarters',
            'market_cap_B', 'revenue_B', 'employees', 'current_price',
            'pe_ratio', 'pb_ratio', 'dividend_yield', 'website', 'last_updated',
        ]
        export_cols = [c for c in export_cols if c in export_df.columns]
        st.download_button(
            label="⬇️ Download All Companies as CSV",
            data=export_df[export_cols].to_csv(index=False),
            file_name=f"companies_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.markdown("""<div class="info-box">
            <h3>🚀 Welcome to Your Analytics Platform!</h3>
            <p>Head over to <strong>Data Collection</strong> to gather your first dataset.</p>
            <p>✨ <i>Pro tip: Start with the Technology sector for rich data!</i></p>
        </div>""", unsafe_allow_html=True)


# =============================================================================
# DATA COLLECTION
# =============================================================================
def show_data_collection():
    st.markdown("## 📥 Data Collection Center")

    total_companies    = cached_get_company_count()
    target             = 150   # 6 sectors x 25 companies
    progress_pct       = min((total_companies / target) * 100, 100)

    st.markdown(f"""<div class="info-box">
        <h4>📊 Collection Progress: {progress_pct:.1f}%</h4>
        <div style="background:rgba(255,255,255,0.3); border-radius:10px; overflow:hidden;">
            <div style="width:{progress_pct}%; height:20px;
                        background:linear-gradient(90deg,#00b894,#00a085);"></div>
        </div>
        <p style="margin-top:10px;">Target: {target} companies | Current: {total_companies} companies</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🏭 Select Target Industry")
        industries = {
            "technology": "🖥️ Technology (AI, Software, Hardware) — 25 companies",
            "finance":    "💼 Finance (Banks, Investment) — 25 companies",
            "healthcare": "🏥 Healthcare (Pharma, Medical) — 25 companies",
            "retail":     "🛒 Retail (E-commerce, Consumer) — 25 companies",
            "energy":     "⚡ Energy (Oil, Gas, Renewable) — 25 companies",
            "automotive": "🚗 Automotive (Auto, EV, Parts) — 25 companies",
        }
        industry = st.selectbox("Choose industry:", list(industries.keys()),
                                format_func=lambda x: industries[x])
    with col2:
        st.markdown("### 📊 Quick Stats")
        st.info("**Available:** 25 companies")
        st.info("**Data Points:** 20+")
        st.info("**Update:** Real-time")

    st.markdown("### 🎯 Custom Company Analysis")
    custom_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        placeholder="AAPL, MSFT, GOOGL, TSLA",
    )

    st.markdown("### 🚀 Data Collection Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"📊 Collect {industry.title()} Data", type="primary", use_container_width=True):
            collect_industry_data(industry)
    with col2:
        if st.button("🎯 Collect Custom Data", disabled=not custom_symbols, use_container_width=True):
            collect_custom_data([s.strip().upper() for s in custom_symbols.split(',')])
    with col3:
        if st.button("🔄 Refresh Prices",
                     help="Re-fetch current price & market data for stale companies",
                     use_container_width=True):
            refresh_prices()

    df_existing = cached_get_all_companies()
    if not df_existing.empty:
        stale_count = df_existing["last_updated"].apply(
            lambda ts: st.session_state.data_collector.needs_refresh(ts, hours=24)
        ).sum()
        if stale_count > 0:
            st.warning(f"⚠️ {stale_count} companies have data older than 24 hours. "
                       "Click **🔄 Refresh Prices** to update them.")


def refresh_prices():
    df = cached_get_all_companies()
    if df.empty:
        st.warning("No companies in the database yet.")
        return

    stale = df[df["last_updated"].apply(
        lambda ts: st.session_state.data_collector.needs_refresh(ts, hours=24)
    )]

    if stale.empty:
        st.success("✅ All data is up-to-date (refreshed within the last 24 hours).")
        return

    st.info(f"🔄 Refreshing {len(stale)} stale companies…")
    progress  = st.progress(0)
    status    = st.empty()
    refreshed = 0

    for i, row in enumerate(stale.itertuples(), 1):
        progress.progress(i / len(stale))
        status.text(f"Refreshing {row.symbol}… ({i}/{len(stale)})")

        fresh = st.session_state.data_collector.refresh_company_data(row.symbol)
        if fresh:
            conn = sqlite3.connect(st.session_state.db_manager.db_path)
            conn.execute(
                """UPDATE companies
                   SET current_price=?, previous_close=?, volume=?, avg_volume=?,
                       market_cap=?, pe_ratio=?, pb_ratio=?, dividend_yield=?, last_updated=?
                   WHERE symbol=?""",
                (fresh["current_price"], fresh["previous_close"],
                 fresh["volume"],        fresh["avg_volume"],
                 fresh["market_cap"],    fresh["pe_ratio"],
                 fresh["pb_ratio"],      fresh["dividend_yield"],
                 fresh["last_updated"],  fresh["symbol"]),
            )
            conn.commit()
            conn.close()
            try:
                hist = st.session_state.data_collector.get_stock_history(row.symbol)
                if not hist.empty:
                    st.session_state.db_manager.insert_stock_history(row.symbol, hist)
            except Exception:
                pass
            refreshed += 1
        time.sleep(0.3)

    progress.progress(1.0)
    status.empty()
    bust_cache()
    st.success(f"✅ Refreshed {refreshed} / {len(stale)} companies.")


def collect_industry_data(industry):
    companies = st.session_state.data_collector.search_companies_by_industry(industry)
    if not companies:
        st.error("No companies found!")
        return

    st.markdown(f"""<div class="info-box">
        <h4>🌐 Data Collection in Progress</h4>
        <p>Collecting from: Yahoo Finance API + Web Scraping</p>
        <p>Companies to process: {len(companies)}</p>
    </div>""", unsafe_allow_html=True)

    progress_bar   = st.progress(0)
    status_text    = st.empty()
    col1, col2, col3 = st.columns(3)
    success_metric = col1.empty()
    failed_metric  = col2.empty()
    current_metric = col3.empty()
    details        = st.expander("📋 Collection Details", expanded=False)

    successful, failed, failed_companies = 0, 0, []

    for i, symbol in enumerate(companies):
        progress_bar.progress((i + 1) / len(companies))
        status_text.markdown(f"""
        <div style="text-align:center; padding:1rem; background:rgba(255,255,255,0.1); border-radius:10px;">
            <h4>🔄 Processing: {symbol}</h4>
            <p>Company {i+1} of {len(companies)}</p>
        </div>""", unsafe_allow_html=True)
        success_metric.metric("✅ Success", successful)
        failed_metric.metric("❌ Failed", failed)
        current_metric.metric("📊 Progress", f"{i+1}/{len(companies)}")

        try:
            company_data = st.session_state.data_collector.get_company_basic_info(symbol)
            if company_data:
                st.session_state.db_manager.insert_company_data(company_data)
                try:
                    execs = st.session_state.data_collector.get_executives(symbol)
                    if execs:
                        st.session_state.db_manager.insert_executives(symbol, execs)
                except Exception as e:
                    with details: st.warning(f"Executives skipped for {symbol}: {e}")
                try:
                    ratios = st.session_state.data_collector.get_financial_ratios(symbol)
                    if ratios:
                        st.session_state.db_manager.insert_financial_ratios(symbol, ratios)
                except Exception as e:
                    with details: st.warning(f"Ratios skipped for {symbol}: {e}")
                try:
                    hist = st.session_state.data_collector.get_stock_history(symbol)
                    if not hist.empty:
                        st.session_state.db_manager.insert_stock_history(symbol, hist)
                except Exception as e:
                    with details: st.warning(f"Stock history skipped for {symbol}: {e}")
                successful += 1
                with details: st.success(f"✅ {symbol} — collected successfully")
            else:
                failed += 1
                failed_companies.append(symbol)
                with details: st.warning(f"⚠️ {symbol} — no data returned")
            time.sleep(0.5)
        except Exception as e:
            failed += 1
            failed_companies.append(symbol)
            with details: st.error(f"❌ {symbol} — {str(e)}")

    progress_bar.progress(1.0)
    bust_cache()

    if successful > 0:
        status_text.markdown(f"""<div class="success-box">
            <h3>✅ Collection Complete!</h3>
            <p>Successfully collected: {successful} companies | Failed: {failed}</p>
        </div>""", unsafe_allow_html=True)
    else:
        status_text.markdown("""<div class="error-box">
            <h3>❌ Collection Failed</h3>
            <p>No data could be collected. Please check your internet connection.</p>
        </div>""", unsafe_allow_html=True)

    if failed_companies:
        with details: st.warning(f"Failed: {', '.join(failed_companies)}")

    success_metric.metric("✅ Success", successful)
    failed_metric.metric("❌ Failed", failed)
    current_metric.metric("📊 Complete", "100%")


def collect_custom_data(symbols):
    progress_bar = st.progress(0)
    status_text  = st.empty()
    successful, failed = 0, 0

    for i, symbol in enumerate(symbols):
        progress_bar.progress((i + 1) / len(symbols))
        status_text.text(f"Processing {symbol}… ({i+1}/{len(symbols)})")
        try:
            data = st.session_state.data_collector.get_company_basic_info(symbol)
            if data:
                st.session_state.db_manager.insert_company_data(data)
                successful += 1
            else:
                failed += 1
            time.sleep(0.5)
        except Exception as e:
            failed += 1
            st.warning(f"Error with {symbol}: {str(e)}")

    progress_bar.progress(1.0)
    bust_cache()
    status_text.success(f"✅ Complete! Success: {successful}, Failed: {failed}")


# =============================================================================
# VISUALIZATIONS
# =============================================================================
def show_visualizations():
    st.markdown("## 📊 Data Visualizations")
    df = cached_get_all_companies()

    if df.empty:
        st.markdown("""<div class="info-box">
            <h3>📝 No Data Available</h3>
            <p>Please collect some company data first!</p>
        </div>""", unsafe_allow_html=True)
        return

    viz_type = st.selectbox("Choose Visualization:",
                            ["Market Cap Analysis", "Industry Analysis", "Performance Dashboard"])

    if viz_type == "Market Cap Analysis":
        st.subheader("💰 Market Cap Analysis")
        st.plotly_chart(create_market_cap_chart(df.head(15)), use_container_width=True)

    elif viz_type == "Industry Analysis":
        st.subheader("🏭 Industry Analysis")
        st.plotly_chart(create_pie_chart(df), use_container_width=True)
        st.subheader("📊 Industry Metrics")
        st.dataframe(df.groupby('industry').agg({
            'market_cap': ['count', 'mean'], 'revenue': 'mean', 'employees': 'mean'
        }).round(2), use_container_width=True)

    elif viz_type == "Performance Dashboard":
        st.subheader("🎯 Performance Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💰 Market Cap vs Revenue")
            dv = df.copy()
            dv['market_cap_billions'] = dv['market_cap'] / 1e9
            dv['revenue_billions']    = dv['revenue']    / 1e9
            dv = dv[(dv['market_cap_billions'] > 0) & (dv['revenue_billions'] > 0)]
            if not dv.empty:
                st.plotly_chart(px.scatter(
                    dv, x='revenue_billions', y='market_cap_billions',
                    size='employees', color='sector', hover_name='company_name',
                    title="Market Cap vs Revenue",
                    labels={'revenue_billions': 'Revenue (B USD)', 'market_cap_billions': 'Market Cap (B USD)'}
                ), use_container_width=True)
        with col2:
            st.markdown("#### 📊 P/E Ratio Distribution")
            pe = df[(df['pe_ratio'] > 0) & (df['pe_ratio'] < 100)]
            if not pe.empty:
                st.plotly_chart(px.histogram(pe, x='pe_ratio', nbins=20,
                                             title="P/E Ratio Distribution"), use_container_width=True)


# =============================================================================
# COMPANY ANALYSIS
# =============================================================================
def show_company_analysis():
    st.markdown("## 🔍 Company Analysis")

    df = cached_get_all_companies()
    if df.empty:
        st.info("No companies available. Please collect data first!")
        return

    selected = st.selectbox(
        "Select Company:",
        df["symbol"].tolist(),
        format_func=lambda x: f"{x} – {df[df['symbol']==x]['company_name'].iloc[0]}",
    )
    if not selected:
        return

    cd = df[df["symbol"] == selected].iloc[0]   # company_data shorthand

    # Hero banner with last-updated timestamp
    last_updated = cd.get("last_updated", "Unknown")
    st.markdown(f"""
    <div style="text-align:center; padding:2rem;
                background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                border-radius:15px; color:white; margin-bottom:2rem;">
        <h1>🏢 {cd['company_name']}</h1>
        <h3>({selected})</h3>
        <p>{cd['sector']} | {cd['industry']}</p>
        <p style="opacity:0.7; font-size:0.85rem;">🕒 Data last updated: {last_updated}</p>
    </div>""", unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    for col, (label, value, icon) in zip(
        [col1, col2, col3, col4],
        [
            ("Market Cap", f"${cd['market_cap']/1e9:.1f}B" if cd['market_cap'] > 0 else "N/A", "💰"),
            ("Revenue",    f"${cd['revenue']/1e9:.1f}B"    if cd['revenue']    > 0 else "N/A", "📈"),
            ("Employees",  f"{cd['employees']:,.0f}"        if cd['employees']  > 0 else "N/A", "👥"),
            ("P/E Ratio",  f"{cd['pe_ratio']:.2f}"          if cd['pe_ratio']   > 0 else "N/A", "📊"),
        ]
    ):
        with col:
            st.markdown(f"""<div class="metric-container">
                <div style="font-size:2rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # --- Company description (NEW) ---
    description = cd.get("description", "")
    if description and description not in ("N/A", "", None):
        st.markdown("### 📖 About")
        st.markdown(f'<div class="description-box">{description}</div>', unsafe_allow_html=True)
        st.markdown("---")

    # Stock price chart
    st.markdown("### 📈 Stock Price History")
    history_df = cached_get_stock_history(selected)

    if history_df.empty:
        st.info("No price history in the database yet. Re-run data collection to populate it.")
    else:
        history_df["date"] = pd.to_datetime(history_df["date"])
        history_df = history_df.sort_values("date")

        range_opts = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "All": None}
        sel_range  = st.radio("Time range:", list(range_opts.keys()), horizontal=True, index=2)
        days = range_opts[sel_range]
        if days:
            history_df = history_df[history_df["date"] >= history_df["date"].max() - pd.Timedelta(days=days)]

        start_price = history_df["close_price"].iloc[0]
        end_price   = history_df["close_price"].iloc[-1]
        line_color  = "#00b894" if end_price >= start_price else "#e17055"
        fill_rgb    = "0,184,148" if line_color == "#00b894" else "225,112,85"
        pct_change  = ((end_price - start_price) / start_price) * 100
        sign        = "+" if pct_change >= 0 else ""

        chart_type = st.radio("Chart type:", ["Line", "Candlestick"], horizontal=True)

        if chart_type == "Line":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history_df["date"], y=history_df["close_price"],
                mode="lines", name="Close Price",
                line=dict(color=line_color, width=2),
                fill="tozeroy", fillcolor=f"rgba({fill_rgb},0.08)",
            ))
        else:
            fig = go.Figure(data=[go.Candlestick(
                x=history_df["date"],
                open=history_df["open_price"],  high=history_df["high_price"],
                low=history_df["low_price"],    close=history_df["close_price"],
                name=selected,
            )])

        fig.update_layout(
            title=dict(
                text=f"{cd['company_name']} ({selected})  "
                     f"<span style='color:{line_color}'>{sign}{pct_change:.1f}%</span>",
                font=dict(size=16),
            ),
            xaxis_title="Date", yaxis_title="Price (USD)", height=420,
            hovermode="x unified",
            xaxis_rangeslider_visible=(chart_type == "Candlestick"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Volume chart
        st.markdown("#### 📊 Trading Volume")
        vol_fig = go.Figure(go.Bar(
            x=history_df["date"], y=history_df["volume"],
            marker_color=line_color, opacity=0.6, name="Volume",
        ))
        vol_fig.update_layout(
            height=180, margin=dict(t=10, b=10), xaxis_title="", yaxis_title="Volume",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(vol_fig, use_container_width=True)

        # --- CSV export for this company's price history (NEW) ---
        exp = history_df[["date","open_price","high_price","low_price","close_price","volume"]].copy()
        exp.columns = ["Date","Open","High","Low","Close","Volume"]
        st.download_button(
            label=f"⬇️ Download {selected} Price History as CSV",
            data=exp.to_csv(index=False),
            file_name=f"{selected}_price_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    st.markdown("---")

    # Detailed info
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Company Information")
        st.write(f"**Sector:** {cd['sector']}")
        st.write(f"**Industry:** {cd['industry']}")
        st.write(f"**Headquarters:** {cd['headquarters']}")
        st.write(f"**Website:** {cd['website']}")
    with col2:
        st.subheader("Financial Metrics")
        st.write(f"**Current Price:** ${cd['current_price']:.2f}" if cd["current_price"] > 0 else "**Current Price:** N/A")
        st.write(f"**Volume:** {cd['volume']:,.0f}"               if cd["volume"]        > 0 else "**Volume:** N/A")
        st.write(f"**P/B Ratio:** {cd['pb_ratio']:.2f}"           if cd["pb_ratio"]      > 0 else "**P/B Ratio:** N/A")
        st.write(f"**Dividend Yield:** {cd['dividend_yield']*100:.2f}%" if cd["dividend_yield"] > 0 else "**Dividend Yield:** N/A")


# =============================================================================
# CHART HELPERS
# =============================================================================
def create_market_cap_chart(df):
    dv = df.copy()
    dv['market_cap_billions'] = dv['market_cap'] / 1e9
    dv = dv.sort_values('market_cap_billions', ascending=True).tail(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dv['market_cap_billions'], y=dv['symbol'], orientation='h',
        marker=dict(color=dv['market_cap_billions'], colorscale='Viridis')
    ))
    fig.update_layout(title="Market Cap Leaders", xaxis_title="Market Cap (Billions USD)", height=400)
    return fig


def create_pie_chart(df):
    counts = df['industry'].value_counts().head(8)
    fig = go.Figure(data=[go.Pie(labels=counts.index, values=counts.values, hole=0.4)])
    fig.update_layout(title="Industry Distribution", height=400)
    return fig


def display_data_table(df):
    dv = df.copy()
    if 'market_cap' in dv.columns:
        dv['Market Cap'] = dv['market_cap'].apply(lambda x: f"${x/1e9:.1f}B" if x > 0 else "N/A")
    if 'current_price' in dv.columns:
        dv['Price'] = dv['current_price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
    if 'last_updated' in dv.columns:
        dv['Last Updated'] = dv['last_updated']
    cols = ['symbol', 'company_name', 'sector', 'Market Cap', 'Price', 'Last Updated']
    st.dataframe(dv[[c for c in cols if c in dv.columns]], use_container_width=True, height=400)


if __name__ == "__main__":
    main()
