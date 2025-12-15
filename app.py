import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Import our custom modules
from data_collector import CompanyDataCollector
from database_manager import DatabaseManager
from visualizations import DataVisualizer

# Page configuration
st.set_page_config(
    page_title="Strategic Company Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for modern interface
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
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .info-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'data_collector' not in st.session_state:
    st.session_state.data_collector = CompanyDataCollector()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = DataVisualizer()

def main():
    """Main application function"""
    # Enhanced header
    st.markdown('''
    <div class="main-header">
        📊 Strategic Company Data Analyzer
    </div>
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        <i>Professional Financial Data Analysis & Visualization Platform</i>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📥 Data Collection", "📊 Visualizations", "🔍 Company Analysis"]
    )
    
    # Quick stats in sidebar
    total_companies = st.session_state.db_manager.get_company_count()
    st.sidebar.markdown(f"""
    <div class="info-box">
        <h4>📊 Quick Stats</h4>
        <p>Total Companies: <strong>{total_companies}</strong></p>
        <p>Status: <strong>Active</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Route to different pages
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📥 Data Collection":
        show_data_collection()
    elif page == "📊 Visualizations":
        show_visualizations()
    elif page == "🔍 Company Analysis":
        show_company_analysis()

def show_dashboard():
    """Enhanced dashboard"""
    st.markdown("## 🏠 Executive Dashboard")
    
    # Get data
    total_companies = st.session_state.db_manager.get_company_count()
    all_companies_df = st.session_state.db_manager.get_all_companies()
    
    # Enhanced metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2rem;">🏢</div>
            <div class="metric-value">{total_companies}</div>
            <div class="metric-label">Total Companies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sectors = all_companies_df['sector'].nunique() if not all_companies_df.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2rem;">🏭</div>
            <div class="metric-value">{sectors}</div>
            <div class="metric-label">Unique Sectors</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_cap = f"${all_companies_df['market_cap'].mean()/1e9:.1f}B" if not all_companies_df.empty else "N/A"
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2rem;">💰</div>
            <div class="metric-value">{avg_cap}</div>
            <div class="metric-label">Avg Market Cap</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2rem;">✅</div>
            <div class="metric-value">Online</div>
            <div class="metric-label">System Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not all_companies_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Market Leaders")
            top_companies = all_companies_df.nlargest(10, 'market_cap')
            fig = create_market_cap_chart(top_companies)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Industry Distribution")
            fig = create_pie_chart(all_companies_df)
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown("### 📋 Company Overview")
        display_data_table(all_companies_df)
    else:
        st.markdown("""
        <div class="info-box">
            <h3>🚀 Welcome to Your Analytics Platform!</h3>
            <p>Ready to start analyzing? Head over to <strong>Data Collection</strong> to gather your first dataset.</p>
            <p>✨ <i>Pro tip: Start with the Technology sector for rich data!</i></p>
        </div>
        """, unsafe_allow_html=True)

def show_data_collection():
    """Enhanced data collection interface"""
    st.markdown("## 📥 Data Collection Center")
    
    # Progress indicator
    total_companies = st.session_state.db_manager.get_company_count()
    progress_percentage = min((total_companies / 50) * 100, 100)
    
    st.markdown(f"""
    <div class="info-box">
        <h4>📊 Collection Progress: {progress_percentage:.1f}%</h4>
        <div style="background: rgba(255,255,255,0.3); border-radius: 10px; overflow: hidden;">
            <div style="width: {progress_percentage}%; height: 20px; background: linear-gradient(90deg, #00b894, #00a085);"></div>
        </div>
        <p style="margin-top: 10px;">Target: 50 companies | Current: {total_companies} companies</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Industry selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🏭 Select Target Industry")
        industries = {
            "technology": "🖥️ Technology (AI, Software, Hardware)",
            "finance": "💼 Finance (Banks, Investment)",
            "healthcare": "🏥 Healthcare (Pharma, Medical)",
            "retail": "🛒 Retail (E-commerce, Consumer)",
            "energy": "⚡ Energy (Oil, Gas, Renewable)",
            "automotive": "🚗 Automotive (Auto, EV, Parts)"
        }
        
        industry = st.selectbox(
            "Choose industry:",
            list(industries.keys()),
            format_func=lambda x: industries[x]
        )
    
    with col2:
        st.markdown("### 📊 Quick Stats")
        st.info("**Available:** 10 companies")
        st.info("**Data Points:** 20+")
        st.info("**Update:** Real-time")
    
    # Custom companies
    st.markdown("### 🎯 Custom Company Analysis")
    custom_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        placeholder="AAPL, MSFT, GOOGL, TSLA",
        help="Add any publicly traded companies"
    )
    
    # Action buttons
    st.markdown("### 🚀 Data Collection Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📊 Collect {industry.title()} Data", type="primary", use_container_width=True):
            collect_industry_data(industry)
    
    with col2:
        if st.button("🎯 Collect Custom Data", disabled=not custom_symbols, use_container_width=True):
            symbols = [s.strip().upper() for s in custom_symbols.split(',')]
            collect_custom_data(symbols)

def collect_industry_data(industry):
    """Collect data for industry - simplified with better error handling"""
    companies = st.session_state.data_collector.search_companies_by_industry(industry)
    
    if not companies:
        st.error("No companies found!")
        return
    
    st.markdown(f"""
    <div class="info-box">
        <h4>🌐 Data Collection in Progress</h4>
        <p>Collecting from: Yahoo Finance API + Web Scraping</p>
        <p>Companies to process: {len(companies)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    col1, col2, col3 = st.columns(3)
    success_metric = col1.empty()
    failed_metric = col2.empty()
    current_metric = col3.empty()
    
    # Details section
    details = st.expander("📋 Collection Details", expanded=False)
    
    successful = 0
    failed = 0
    failed_companies = []
    
    for i, symbol in enumerate(companies):
        progress = (i + 1) / len(companies)
        progress_bar.progress(progress)
        
        status_text.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
            <h4>🔄 Processing: {symbol}</h4>
            <p>Company {i+1} of {len(companies)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Update metrics
        success_metric.metric("✅ Success", successful)
        failed_metric.metric("❌ Failed", failed)
        current_metric.metric("📊 Progress", f"{i+1}/{len(companies)}")
        
        try:
            with details:
                st.write(f"**Processing {symbol}...**")
            
            # Get basic company data
            company_data = st.session_state.data_collector.get_company_basic_info(symbol)
            
            if company_data:
                # Save to database
                st.session_state.db_manager.insert_company_data(company_data)
                
                # Try to get additional data (non-critical)
                try:
                    executives = st.session_state.data_collector.get_executives(symbol)
                    if executives:
                        st.session_state.db_manager.insert_executives(symbol, executives)
                except:
                    pass
                
                try:
                    ratios = st.session_state.data_collector.get_financial_ratios(symbol)
                    if ratios:
                        st.session_state.db_manager.insert_financial_ratios(symbol, ratios)
                except:
                    pass
                
                try:
                    stock_history = st.session_state.data_collector.get_stock_history(symbol)
                    if not stock_history.empty:
                        st.session_state.db_manager.insert_stock_history(symbol, stock_history)
                except:
                    pass
                
                successful += 1
                with details:
                    st.success(f"✅ {symbol} - Data collected successfully")
            else:
                failed += 1
                failed_companies.append(symbol)
                with details:
                    st.warning(f"⚠️ {symbol} - Could not retrieve data")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            failed += 1
            failed_companies.append(symbol)
            with details:
                st.error(f"❌ {symbol} - Error: {str(e)}")
    
    # Final status
    progress_bar.progress(1.0)
    
    if successful > 0:
        status_text.markdown(f"""
        <div class="success-box">
            <h3>✅ Collection Complete!</h3>
            <p>Successfully collected: {successful} companies</p>
            <p>Failed: {failed} companies</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        status_text.markdown("""
        <div class="error-box">
            <h3>❌ Collection Failed</h3>
            <p>No data could be collected. Please check your internet connection.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show failed companies if any
    if failed_companies:
        with details:
            st.warning(f"Failed companies: {', '.join(failed_companies)}")
    
    # Final metrics
    success_metric.metric("✅ Success", successful)
    failed_metric.metric("❌ Failed", failed)
    current_metric.metric("📊 Complete", "100%")

def collect_custom_data(symbols):
    """Collect custom symbol data"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(symbols):
        progress = (i + 1) / len(symbols)
        progress_bar.progress(progress)
        status_text.text(f"Processing {symbol}... ({i+1}/{len(symbols)})")
        
        try:
            company_data = st.session_state.data_collector.get_company_basic_info(symbol)
            
            if company_data:
                st.session_state.db_manager.insert_company_data(company_data)
                successful += 1
            else:
                failed += 1
                
            time.sleep(0.5)
            
        except Exception as e:
            failed += 1
            st.warning(f"Error with {symbol}: {str(e)}")
    
    progress_bar.progress(1.0)
    status_text.success(f"✅ Complete! Success: {successful}, Failed: {failed}")

def show_visualizations():
    """Visualizations page"""
    st.markdown("## 📊 Data Visualizations")
    
    df = st.session_state.db_manager.get_all_companies()
    
    if df.empty:
        st.markdown("""
        <div class="info-box">
            <h3>📝 No Data Available</h3>
            <p>Please collect some company data first!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    viz_type = st.selectbox(
        "Choose Visualization:",
        ["Market Cap Analysis", "Industry Analysis", "Performance Dashboard"]
    )
    
    if viz_type == "Market Cap Analysis":
        show_market_cap_analysis(df)
    elif viz_type == "Industry Analysis":
        show_industry_analysis(df)
    elif viz_type == "Performance Dashboard":
        show_performance_dashboard(df)

def show_market_cap_analysis(df):
    """Market cap analysis"""
    st.subheader("💰 Market Cap Analysis")
    fig = create_market_cap_chart(df.head(15))
    st.plotly_chart(fig, use_container_width=True)

def show_industry_analysis(df):
    """Industry analysis"""
    st.subheader("🏭 Industry Analysis")
    fig = create_pie_chart(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Industry metrics table
    st.subheader("📊 Industry Metrics")
    industry_metrics = df.groupby('industry').agg({
        'market_cap': ['count', 'mean'],
        'revenue': 'mean',
        'employees': 'mean'
    }).round(2)
    st.dataframe(industry_metrics, use_container_width=True)

def show_performance_dashboard(df):
    """Performance dashboard"""
    st.subheader("🎯 Performance Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Market Cap vs Revenue")
        df_viz = df.copy()
        df_viz['market_cap_billions'] = df_viz['market_cap'] / 1e9
        df_viz['revenue_billions'] = df_viz['revenue'] / 1e9
        df_viz = df_viz[(df_viz['market_cap_billions'] > 0) & (df_viz['revenue_billions'] > 0)]
        
        if not df_viz.empty:
            fig = px.scatter(
                df_viz,
                x='revenue_billions',
                y='market_cap_billions',
                size='employees',
                color='sector',
                hover_name='company_name',
                title="Market Cap vs Revenue",
                labels={
                    'revenue_billions': 'Revenue (Billions USD)',
                    'market_cap_billions': 'Market Cap (Billions USD)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 P/E Ratio Distribution")
        pe_data = df[df['pe_ratio'] > 0]
        pe_data = pe_data[pe_data['pe_ratio'] < 100]
        
        if not pe_data.empty:
            fig = px.histogram(
                pe_data,
                x='pe_ratio',
                nbins=20,
                title="P/E Ratio Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_company_analysis():
    """Company analysis page"""
    st.markdown("## 🔍 Company Analysis")
    
    df = st.session_state.db_manager.get_all_companies()
    
    if df.empty:
        st.info("No companies available. Please collect data first!")
        return
    
    selected_company = st.selectbox(
        "Select Company:",
        df['symbol'].tolist(),
        format_func=lambda x: f"{x} - {df[df['symbol']==x]['company_name'].iloc[0]}"
    )
    
    if selected_company:
        company_data = df[df['symbol'] == selected_company].iloc[0]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; margin-bottom: 2rem;">
            <h1>🏢 {company_data['company_name']}</h1>
            <h3>({selected_company})</h3>
            <p>{company_data['sector']} | {company_data['industry']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Company metrics
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Market Cap", f"${company_data['market_cap']/1e9:.1f}B" if company_data['market_cap'] > 0 else "N/A", "💰"),
            ("Revenue", f"${company_data['revenue']/1e9:.1f}B" if company_data['revenue'] > 0 else "N/A", "📈"),
            ("Employees", f"{company_data['employees']:,}" if company_data['employees'] > 0 else "N/A", "👥"),
            ("P/E Ratio", f"{company_data['pe_ratio']:.2f}" if company_data['pe_ratio'] > 0 else "N/A", "📊")
        ]
        
        for col, (label, value, icon) in zip([col1, col2, col3, col4], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-container">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Company Information")
            st.write(f"**Sector:** {company_data['sector']}")
            st.write(f"**Industry:** {company_data['industry']}")
            st.write(f"**Headquarters:** {company_data['headquarters']}")
            st.write(f"**Website:** {company_data['website']}")
        
        with col2:
            st.subheader("Financial Metrics")
            st.write(f"**Current Price:** ${company_data['current_price']:.2f}" if company_data['current_price'] > 0 else "N/A")
            st.write(f"**Volume:** {company_data['volume']:,}" if company_data['volume'] > 0 else "N/A")
            st.write(f"**P/B Ratio:** {company_data['pb_ratio']:.2f}" if company_data['pb_ratio'] > 0 else "N/A")

def create_market_cap_chart(df):
    """Create market cap chart"""
    df_viz = df.copy()
    df_viz['market_cap_billions'] = df_viz['market_cap'] / 1e9
    df_viz = df_viz.sort_values('market_cap_billions', ascending=True).tail(10)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_viz['market_cap_billions'],
        y=df_viz['symbol'],
        orientation='h',
        marker=dict(
            color=df_viz['market_cap_billions'],
            colorscale='Viridis'
        )
    ))
    
    fig.update_layout(
        title="Market Cap Leaders",
        xaxis_title="Market Cap (Billions USD)",
        height=400
    )
    
    return fig

def create_pie_chart(df):
    """Create industry pie chart"""
    industry_counts = df['industry'].value_counts().head(8)
    
    fig = go.Figure(data=[go.Pie(
        labels=industry_counts.index,
        values=industry_counts.values,
        hole=0.4
    )])
    
    fig.update_layout(
        title="Industry Distribution",
        height=400
    )
    
    return fig

def display_data_table(df):
    """Display data table"""
    display_df = df.head(10).copy()
    
    if 'market_cap' in display_df.columns:
        display_df['Market Cap'] = display_df['market_cap'].apply(
            lambda x: f"${x/1e9:.1f}B" if x > 0 else "N/A"
        )
    
    columns = ['symbol', 'company_name', 'sector', 'Market Cap']
    available_columns = [col for col in columns if col in display_df.columns]
    
    st.dataframe(display_df[available_columns], use_container_width=True, height=400)

if __name__ == "__main__":
    main()