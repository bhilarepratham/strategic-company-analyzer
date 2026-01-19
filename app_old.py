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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
    # Main title
    st.markdown('<h1 class="main-header">📊 Strategic Company Data Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📥 Data Collection", "📊 Visualizations", "🔍 Company Analysis"]
    )
    
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
    """Display main dashboard with key metrics and overview"""
    st.header("📊 Dashboard Overview")
    
    # Get current data stats
    total_companies = st.session_state.db_manager.get_company_count()
    all_companies_df = st.session_state.db_manager.get_all_companies()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", total_companies)
    
    with col2:
        if not all_companies_df.empty:
            unique_sectors = all_companies_df['sector'].nunique()
            st.metric("Unique Sectors", unique_sectors)
    
    with col3:
        if not all_companies_df.empty:
            avg_market_cap = all_companies_df['market_cap'].mean() / 1e9
            st.metric("Avg Market Cap", f"${avg_market_cap:.1f}B")
    
    with col4:
        if not all_companies_df.empty:
            last_update = all_companies_df['last_updated'].max()
            st.metric("Last Updated", last_update.split()[0] if last_update else "No data")
    
    st.markdown("---")
    
    if not all_companies_df.empty:
        # Quick visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Top companies by market cap
            top_companies = all_companies_df.nlargest(10, 'market_cap')
            fig = st.session_state.visualizer.create_market_cap_comparison(
                top_companies, "Top 10 Companies by Market Cap"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Industry distribution
            if len(all_companies_df) > 0:
                fig = st.session_state.visualizer.create_industry_distribution(all_companies_df)
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent companies table
        st.subheader("Recently Added Companies")
        recent_companies = all_companies_df.head(10)[['symbol', 'company_name', 'sector', 'market_cap', 'current_price']]
        recent_companies['market_cap'] = recent_companies['market_cap'].apply(
            lambda x: f"${x/1e9:.1f}B" if x > 0 else "N/A"
        )
        st.dataframe(recent_companies, use_container_width=True)
    
    else:
        st.info("📝 No data available yet. Go to the Data Collection page to start gathering company data!")

def show_data_collection():
    """Data collection interface"""
    st.header("📥 Data Collection")
    
    st.markdown("""
    Collect strategic data on companies in specific industries. The system will gather:
    - 📊 Financial metrics (Market Cap, Revenue, Stock Price)
    - 🏢 Company information (Employees, Founded Year, Headquarters)
    - 📈 Financial ratios and performance metrics
    """)
    
    # Industry selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        industry = st.selectbox(
            "Select Industry to Analyze:",
            ["technology", "finance", "healthcare", "retail", "energy", "automotive"],
            help="Choose an industry to collect data for companies in that sector"
        )
    
    with col2:
        st.metric("Available Industries", "6")
    
    # Custom company addition
    st.subheader("Add Custom Companies")
    custom_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        placeholder="AAPL, MSFT, GOOGL",
        help="Enter stock symbols separated by commas"
    )
    
    # Data collection controls
    col1, col2 = st.columns(2)
    
    with col1:
        collect_industry_btn = st.button(
            f"🚀 Collect {industry.title()} Data",
            type="primary",
            help=f"Collect data for all companies in {industry} industry"
        )
    
    with col2:
        collect_custom_btn = st.button(
            "📊 Collect Custom Data",
            help="Collect data for the custom symbols entered"
        )
    
    # Data collection process
    if collect_industry_btn:
        collect_industry_data(industry)
    
    if collect_custom_btn and custom_symbols:
        symbols = [s.strip().upper() for s in custom_symbols.split(',')]
        collect_custom_data(symbols)

def collect_industry_data(industry: str):
    """Collect data for all companies in an industry"""
    companies = st.session_state.data_collector.search_companies_by_industry(industry)
    
    if not companies:
        st.error(f"No companies found for industry: {industry}")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(companies):
        progress = (i + 1) / len(companies)
        progress_bar.progress(progress)
        status_text.text(f"Collecting data for {symbol}... ({i+1}/{len(companies)})")
        
        try:
            # Get company data
            company_data = st.session_state.data_collector.get_company_basic_info(symbol)
            
            if company_data:
                # Save to database
                st.session_state.db_manager.insert_company_data(company_data)
                successful += 1
                st.session_state.data_collector.rate_limit_wait(0.5)
            else:
                failed += 1
                
        except Exception as e:
            st.error(f"Error collecting data for {symbol}: {str(e)}")
            failed += 1
    
    # Show results
    progress_bar.progress(1.0)
    status_text.text("✅ Data collection completed!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Successfully collected: {successful}")
    with col2:
        if failed > 0:
            st.warning(f"⚠️ Failed: {failed}")

def collect_custom_data(symbols: list):
    """Collect data for custom list of symbols"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(symbols):
        progress = (i + 1) / len(symbols)
        progress_bar.progress(progress)
        status_text.text(f"Collecting data for {symbol}...")
        
        try:
            company_data = st.session_state.data_collector.get_company_basic_info(symbol)
            
            if company_data:
                st.session_state.db_manager.insert_company_data(company_data)
                successful += 1
            else:
                failed += 1
                
            st.session_state.data_collector.rate_limit_wait(0.5)
            
        except Exception as e:
            st.error(f"Error collecting data for {symbol}: {str(e)}")
            failed += 1
    
    progress_bar.progress(1.0)
    status_text.text("✅ Custom data collection completed!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Successfully collected: {successful}")
    with col2:
        if failed > 0:
            st.warning(f"⚠️ Failed: {failed}")

def show_visualizations():
    """Display various data visualizations"""
    st.header("📊 Data Visualizations")
    
    df = st.session_state.db_manager.get_all_companies()
    
    if df.empty:
        st.warning("📝 No data available for visualization. Please collect some data first!")
        return
    
    # Visualization options
    viz_type = st.selectbox(
        "Choose Visualization Type:",
        [
            "Market Cap Analysis",
            "Industry Analysis",
            "Performance Dashboard"
        ]
    )
    
    if viz_type == "Market Cap Analysis":
        show_market_cap_analysis(df)
    elif viz_type == "Industry Analysis":
        show_industry_analysis(df)
    elif viz_type == "Performance Dashboard":
        show_performance_dashboard(df)

def show_market_cap_analysis(df):
    """Show market cap related visualizations"""
    st.subheader("💰 Market Cap Analysis")
    
    # Market cap comparison chart
    fig = st.session_state.visualizer.create_market_cap_comparison(df, "Market Cap Comparison")
    st.plotly_chart(fig, use_container_width=True)
    
    # Revenue vs Employees scatter
    fig = st.session_state.visualizer.create_revenue_vs_employees_scatter(df, "Revenue vs Employees")
    st.plotly_chart(fig, use_container_width=True)

def show_industry_analysis(df):
    """Show industry-based analysis"""
    st.subheader("🏭 Industry Analysis")
    
    # Industry distribution
    fig = st.session_state.visualizer.create_industry_distribution(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Industry performance metrics
    industry_metrics = df.groupby('industry').agg({
        'market_cap': ['count', 'mean', 'sum'],
        'revenue': 'mean',
        'employees': 'mean',
        'pe_ratio': 'mean'
    }).round(2)
    
    st.subheader("📊 Industry Performance Metrics")
    st.dataframe(industry_metrics, use_container_width=True)

def show_performance_dashboard(df):
    """Show comprehensive performance dashboard"""
    st.subheader("🎯 Performance Dashboard")
    
    # Create dashboard charts
    figures = st.session_state.visualizer.create_company_metrics_dashboard(df)
    
    for fig in figures:
        st.plotly_chart(fig, use_container_width=True)

def show_company_analysis():
    """Detailed company analysis page"""
    st.header("🔍 Individual Company Analysis")
    
    df = st.session_state.db_manager.get_all_companies()
    
    if df.empty:
        st.warning("📝 No company data available. Please collect some data first!")
        return
    
    # Company selection
    selected_company = st.selectbox(
        "Select a company for detailed analysis:",
        df['symbol'].tolist(),
        format_func=lambda x: f"{x} - {df[df['symbol']==x]['company_name'].iloc[0]}"
    )
    
    if selected_company:
        company_data = df[df['symbol'] == selected_company].iloc[0]
        
        # Company header
        st.subheader(f"📊 {company_data['company_name']} ({selected_company})")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            market_cap_formatted = f"${company_data['market_cap']/1e9:.1f}B" if company_data['market_cap'] > 0 else "N/A"
            st.metric("Market Cap", market_cap_formatted)
        
        with col2:
            revenue_formatted = f"${company_data['revenue']/1e9:.1f}B" if company_data['revenue'] > 0 else "N/A"
            st.metric("Revenue", revenue_formatted)
        
        with col3:
            st.metric("Employees", f"{company_data['employees']:,}" if company_data['employees'] > 0 else "N/A")
        
        with col4:
            st.metric("P/E Ratio", f"{company_data['pe_ratio']:.2f}" if company_data['pe_ratio'] > 0 else "N/A")
        
        # Company details
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Company Information")
            st.write(f"**Sector:** {company_data['sector']}")
            st.write(f"**Industry:** {company_data['industry']}")
            st.write(f"**Founded:** {company_data['founded_year'] if company_data['founded_year'] > 0 else 'N/A'}")
            st.write(f"**Headquarters:** {company_data['headquarters']}")
            st.write(f"**Website:** {company_data['website']}")
        with col2:
            st.subheader("Financial Metrics")
            st.write(f"**Current Price:** ${company_data['current_price']:.2f}" if company_data['current_price'] > 0 else "N/A")
            st.write(f"**Previous Close:** ${company_data['previous_close']:.2f}" if company_data['previous_close'] > 0 else "N/A")
            st.write(f"**Volume:** {company_data['volume']:,}" if company_data['volume'] > 0 else "N/A")
            st.write(f"**P/B Ratio:** {company_data['pb_ratio']:.2f}" if company_data['pb_ratio'] > 0 else "N/A")
            st.write(f"**Dividend Yield:** {company_data['dividend_yield']:.2%}" if company_data['dividend_yield'] > 0 else "N/A")
        
        # Company description
        if company_data['description'] != 'N/A':
            st.subheader("Company Description")
            st.write(company_data['description'])

if __name__ == "__main__":
    main()
    