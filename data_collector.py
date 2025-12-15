import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional
import json
import re

class CompanyDataCollector:
    def __init__(self, alpha_vantage_key: str = None):
        self.alpha_vantage_key = alpha_vantage_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_company_basic_info(self, symbol: str) -> Dict:
        """Get basic company information - simplified and reliable"""
        try:
            print(f"🔍 Collecting data for {symbol}...")
            
            # Primary data from yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or len(info) < 5:
                print(f"   ⚠️ Limited data available for {symbol}")
                return None
            
            # Extract and structure the data
            company_data = {
                'symbol': symbol.upper(),
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': self._safe_get_number(info, 'marketCap', 0),
                'enterprise_value': self._safe_get_number(info, 'enterpriseValue', 0),
                'revenue': self._safe_get_number(info, 'totalRevenue', 0),
                'employees': self._safe_get_number(info, 'fullTimeEmployees', 0),
                'founded_year': 0,
                'headquarters': self._format_location(info),
                'website': info.get('website', 'N/A'),
                'description': self._get_description(info),
                'current_price': self._safe_get_number(info, 'currentPrice', 0),
                'previous_close': self._safe_get_number(info, 'previousClose', 0),
                'volume': self._safe_get_number(info, 'volume', 0),
                'avg_volume': self._safe_get_number(info, 'averageVolume', 0),
                'pe_ratio': self._safe_get_number(info, 'trailingPE', 0),
                'pb_ratio': self._safe_get_number(info, 'priceToBook', 0),
                'dividend_yield': self._safe_get_number(info, 'dividendYield', 0),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to scrape additional data (with error handling)
            try:
                scraped = self.scrape_yahoo_finance_safe(symbol)
                if scraped:
                    # Merge scraped data
                    for key, value in scraped.items():
                        if value and (not company_data.get(key) or company_data.get(key) in [0, 'N/A', '']):
                            company_data[key] = value
            except Exception as scrape_error:
                print(f"   ⚠️ Web scraping failed for {symbol}, using API data only")
            
            print(f"   ✅ Successfully collected data for {symbol}")
            return company_data
            
        except Exception as e:
            print(f"   ❌ Error collecting data for {symbol}: {str(e)}")
            return None
    
    def _safe_get_number(self, info: dict, key: str, default=0) -> float:
        """Safely extract numeric values"""
        try:
            value = info.get(key, default)
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _format_location(self, info: dict) -> str:
        """Format company location"""
        try:
            city = info.get('city', '')
            state = info.get('state', '')
            country = info.get('country', '')
            
            parts = [p for p in [city, state, country] if p]
            return ', '.join(parts) if parts else 'N/A'
        except:
            return 'N/A'
    
    def _get_description(self, info: dict) -> str:
        """Get company description"""
        try:
            desc = info.get('longBusinessSummary', '')
            if desc:
                return desc[:500] + '...' if len(desc) > 500 else desc
            return info.get('description', 'N/A')
        except:
            return 'N/A'
    
    def scrape_yahoo_finance_safe(self, symbol: str) -> Dict:
        """Safe web scraping with timeout and error handling"""
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {}
            
            # Try to scrape current price
            try:
                price_element = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
                if price_element and price_element.text:
                    data['current_price'] = float(price_element.text.replace(',', ''))
            except:
                pass
            
            # Try to scrape market cap
            try:
                mc_elements = soup.find_all('td', {'data-test': 'MARKET_CAP-value'})
                for elem in mc_elements:
                    if elem.text:
                        data['market_cap'] = self._parse_market_value(elem.text)
                        break
            except:
                pass
            
            print(f"   🌐 Scraped {len(data)} additional fields from web")
            return data
            
        except Exception as e:
            print(f"   ⚠️ Web scraping skipped: {str(e)}")
            return {}
    
    def _parse_market_value(self, value_str: str) -> float:
        """Parse market value strings like '2.5T', '150.3B'"""
        try:
            value_str = value_str.strip().upper().replace('$', '').replace(',', '')
            
            if 'T' in value_str:
                return float(value_str.replace('T', '')) * 1e12
            elif 'B' in value_str:
                return float(value_str.replace('B', '')) * 1e9
            elif 'M' in value_str:
                return float(value_str.replace('M', '')) * 1e6
            else:
                return float(value_str)
        except:
            return 0
    
    def get_stock_history(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get stock price history"""
        try:
            print(f"   📊 Fetching stock history for {symbol}...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if not hist.empty:
                hist['symbol'] = symbol
                print(f"   ✅ Retrieved {len(hist)} days of stock data")
            else:
                print(f"   ⚠️ No stock history available for {symbol}")
            
            return hist
        except Exception as e:
            print(f"   ❌ Error getting stock history: {str(e)}")
            return pd.DataFrame()
    
    def get_executives(self, symbol: str) -> List[Dict]:
        """Get executive information"""
        try:
            print(f"   👔 Fetching executive data for {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            executives = []
            if 'companyOfficers' in info and info['companyOfficers']:
                for officer in info['companyOfficers'][:5]:
                    executives.append({
                        'name': officer.get('name', 'N/A'),
                        'title': officer.get('title', 'N/A'),
                        'age': officer.get('age', 0),
                        'total_pay': officer.get('totalPay', 0)
                    })
                print(f"   ✅ Found {len(executives)} executives")
            else:
                print(f"   ⚠️ No executive data available")
            
            return executives
            
        except Exception as e:
            print(f"   ❌ Error getting executives: {str(e)}")
            return []
    
    def get_financial_ratios(self, symbol: str) -> Dict:
        """Get key financial ratios"""
        try:
            print(f"   📈 Calculating financial ratios for {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            ratios = {
                'pe_ratio': self._safe_get_number(info, 'trailingPE', 0),
                'forward_pe': self._safe_get_number(info, 'forwardPE', 0),
                'peg_ratio': self._safe_get_number(info, 'pegRatio', 0),
                'price_to_sales': self._safe_get_number(info, 'priceToSalesTrailing12Months', 0),
                'price_to_book': self._safe_get_number(info, 'priceToBook', 0),
                'debt_to_equity': self._safe_get_number(info, 'debtToEquity', 0),
                'roe': self._safe_get_number(info, 'returnOnEquity', 0),
                'roa': self._safe_get_number(info, 'returnOnAssets', 0),
                'profit_margin': self._safe_get_number(info, 'profitMargins', 0),
                'operating_margin': self._safe_get_number(info, 'operatingMargins', 0),
                'current_ratio': self._safe_get_number(info, 'currentRatio', 0),
                'quick_ratio': self._safe_get_number(info, 'quickRatio', 0)
            }
            
            ratio_count = len([r for r in ratios.values() if r > 0])
            print(f"   ✅ Calculated {ratio_count} financial ratios")
            return ratios
            
        except Exception as e:
            print(f"   ❌ Error getting ratios: {str(e)}")
            return {}
    
    def search_companies_by_industry(self, industry: str) -> List[str]:
        """Search for companies in a specific industry"""
        industry_mapping = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'ORCL', 'CRM', 'ADBE', 'INTC'],
            'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABT', 'TMO', 'MRK', 'CVS', 'DHR', 'BMY', 'LLY'],
            'retail': ['WMT', 'HD', 'COST', 'TGT', 'LOW', 'SBUX', 'NKE', 'MCD', 'DIS', 'BKNG'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL'],
            'automotive': ['TSLA', 'F', 'GM', 'TM', 'HMC', 'STLA', 'NIO', 'RIVN', 'LCID', 'LI']
        }
        
        return industry_mapping.get(industry.lower(), [])
    
    def rate_limit_wait(self, seconds: float = 1):
        """Add rate limiting to avoid being blocked"""
        time.sleep(seconds)