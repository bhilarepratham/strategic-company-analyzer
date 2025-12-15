import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict

class DataVisualizer:
    def __init__(self):
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def create_market_cap_comparison(self, df: pd.DataFrame, title: str = "Market Cap Comparison") -> go.Figure:
        """Create market cap comparison bar chart"""
        # Convert market cap to billions for better readability
        df_viz = df.copy()
        df_viz['market_cap_billions'] = df_viz['market_cap'] / 1e9
        df_viz = df_viz.sort_values('market_cap_billions', ascending=True).tail(20)
        
        fig = px.bar(
            df_viz, 
            x='market_cap_billions', 
            y='symbol',
            title=title,
            labels={'market_cap_billions': 'Market Cap (Billions USD)', 'symbol': 'Company'},
            color='market_cap_billions',
            color_continuous_scale='Blues',
            hover_data=['company_name', 'sector']
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_font_size=20,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_stock_price_trends(self, stock_data: List[Dict], title: str = "Stock Price Trends") -> go.Figure:
        """Create stock price trend line chart"""
        fig = go.Figure()
        
        for i, stock in enumerate(stock_data):
            df = stock['data']
            symbol = stock['symbol']
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['close_price'],
                mode='lines',
                name=symbol,
                line=dict(color=self.color_palette[i % len(self.color_palette)], width=2),
                hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Stock Price (USD)",
            height=500,
            hovermode='x unified',
            title_font_size=20,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_industry_distribution(self, df: pd.DataFrame, title: str = "Industry Distribution") -> go.Figure:
        """Create pie chart for industry distribution"""
        industry_counts = df['industry'].value_counts().head(10)
        
        fig = px.pie(
            values=industry_counts.values,
            names=industry_counts.index,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            title_font_size=20,
            font=dict(size=12),
            height=500
        )
        
        return fig
    
    def create_revenue_vs_employees_scatter(self, df: pd.DataFrame, title: str = "Revenue vs Employees") -> go.Figure:
        """Create scatter plot of revenue vs employees"""
        df_viz = df.copy()
        df_viz['revenue_billions'] = df_viz['revenue'] / 1e9
        df_viz = df_viz[df_viz['employees'] > 0]  # Filter out companies with no employee data
        
        fig = px.scatter(
            df_viz,
            x='employees',
            y='revenue_billions',
            size='market_cap',
            color='sector',
            hover_name='company_name',
            title=title,
            labels={
                'employees': 'Number of Employees',
                'revenue_billions': 'Revenue (Billions USD)',
                'market_cap': 'Market Cap'
            }
        )
        
        fig.update_layout(
            height=500,
            title_font_size=20,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_pe_ratio_distribution(self, df: pd.DataFrame, title: str = "P/E Ratio Distribution") -> go.Figure:
        """Create histogram of P/E ratios"""
        df_viz = df[df['pe_ratio'] > 0]  # Filter out negative or zero P/E ratios
        df_viz = df_viz[df_viz['pe_ratio'] < 100]  # Filter out extremely high P/E ratios
        
        fig = px.histogram(
            df_viz,
            x='pe_ratio',
            nbins=30,
            title=title,
            labels={'pe_ratio': 'P/E Ratio', 'count': 'Number of Companies'},
            color_discrete_sequence=['#1f77b4']
        )
        
        # Add mean line
        mean_pe = df_viz['pe_ratio'].mean()
        fig.add_vline(
            x=mean_pe,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_pe:.2f}"
        )
        
        fig.update_layout(
            height=400,
            title_font_size=20,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_company_metrics_dashboard(self, df: pd.DataFrame) -> List[go.Figure]:
        """Create a comprehensive dashboard with multiple metrics"""
        figures = []
        
        # 1. Market Cap vs Revenue Scatter
        df_viz = df.copy()
        df_viz['market_cap_billions'] = df_viz['market_cap'] / 1e9
        df_viz['revenue_billions'] = df_viz['revenue'] / 1e9
        df_viz = df_viz[(df_viz['market_cap_billions'] > 0) & (df_viz['revenue_billions'] > 0)]
        
        fig1 = px.scatter(
            df_viz,
            x='revenue_billions',
            y='market_cap_billions',
            color='sector',
            size='employees',
            hover_name='company_name',
            title="Market Cap vs Revenue",
            labels={
                'revenue_billions': 'Revenue (Billions USD)',
                'market_cap_billions': 'Market Cap (Billions USD)'
            }
        )
        figures.append(fig1)
        
        return figures
    
    def format_currency(self, value: float) -> str:
        """Format currency values for better readability"""
        if value >= 1e9:
            return f"${value/1e9:.1f}B"
        elif value >= 1e6:
            return f"${value/1e6:.1f}M"
        elif value >= 1e3:
            return f"${value/1e3:.1f}K"
        else:
            return f"${value:.2f}"