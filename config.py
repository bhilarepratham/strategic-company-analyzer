import os
from typing import Dict, Any

class AppConfig:
    """Application configuration settings"""
    
    # Database settings
    DATABASE_PATH = "company_data.db"
    
    # API settings
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", None)
    
    # Rate limiting settings
    API_RATE_LIMIT_DELAY = 0.5  # seconds between API calls
    MAX_COMPANIES_PER_BATCH = 50
    
    # Data collection settings
    DEFAULT_STOCK_PERIOD = "1y"  # 1 year of stock history
    MAX_EXECUTIVES = 10
    
    # UI settings
    PAGE_TITLE = "Strategic Company Data Analyzer"
    PAGE_ICON = "📊"
    LAYOUT = "wide"
    
    # Industry mappings
    SUPPORTED_INDUSTRIES = {
        'technology': {
            'name': 'Technology',
            'companies': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NFLX', 'NVDA', 'ORCL', 'CRM']
        },
        'finance': {
            'name': 'Financial Services',
            'companies': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB']
        },
        'healthcare': {
            'name': 'Healthcare',
            'companies': ['JNJ', 'PFE', 'UNH', 'ABT', 'TMO', 'MRK', 'CVS', 'DHR', 'BMY', 'MDT']
        },
        'retail': {
            'name': 'Retail & Consumer',
            'companies': ['WMT', 'HD', 'COST', 'TGT', 'LOW', 'TJX', 'SBUX', 'NKE', 'MCD', 'DIS']
        },
        'energy': {
            'name': 'Energy',
            'companies': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'KMI']
        },
        'automotive': {
            'name': 'Automotive',
            'companies': ['TSLA', 'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'HMC', 'TM']
        }
    }
    
    # Chart settings
    CHART_COLOR_PALETTE = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    # Data validation settings
    MIN_MARKET_CAP = 0
    MAX_PE_RATIO = 1000
    MIN_EMPLOYEES = 0
    
    @classmethod
    def get_industry_companies(cls, industry: str) -> list:
        """Get list of companies for a specific industry"""
        return cls.SUPPORTED_INDUSTRIES.get(industry.lower(), {}).get('companies', [])
    
    @classmethod
    def get_all_industries(cls) -> list:
        """Get list of all supported industries"""
        return list(cls.SUPPORTED_INDUSTRIES.keys())