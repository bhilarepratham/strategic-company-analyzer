import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
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

    # ─────────────────────────────────────────────────────────────────────────
    # Industry → ticker mapping  (expanded: 25 per sector)
    # ─────────────────────────────────────────────────────────────────────────
    INDUSTRY_MAP: Dict[str, List[str]] = {
        "technology": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ORCL", "CRM",
            "ADBE", "INTC", "AMD", "QCOM", "TXN", "AVGO", "AMAT", "MU",
            "NOW", "SNOW", "PLTR", "NET", "DDOG", "ZS", "PANW", "CRWD", "UBER",
        ],
        "finance": [
            "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK", "SCHW", "USB",
            "PNC", "TFC", "COF", "SPGI", "MCO", "ICE", "CME", "CBOE", "V", "MA",
            "PYPL", "FIS", "FISV", "DFS", "SYF",
        ],
        "healthcare": [
            "JNJ", "PFE", "UNH", "ABT", "TMO", "MRK", "CVS", "DHR", "BMY", "LLY",
            "AMGN", "GILD", "BIIB", "REGN", "VRTX", "ISRG", "BSX", "MDT", "SYK",
            "BDX", "HCA", "CI", "HUM", "MCK", "ABC",
        ],
        "retail": [
            "WMT", "HD", "COST", "TGT", "LOW", "SBUX", "NKE", "MCD", "DIS", "BKNG",
            "ETSY", "EBAY", "ROST", "TJX", "DLTR", "DG", "YUM", "CMG",
            "QSR", "DKNG", "ABNB", "EXPE", "LYFT", "DASH", "SNAP",
        ],
        "energy": [
            "XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC", "OXY", "HAL",
            "DVN", "PXD", "FANG", "HES", "MRO", "APA", "BKR", "NOV", "NEE", "DUK",
            "SO", "D", "EXC", "PCG", "SRE",
        ],
        "automotive": [
            "TSLA", "F", "GM", "TM", "HMC", "STLA", "NIO", "RIVN", "LCID", "LI",
            "XPEV", "BWA", "ALV", "LEA", "MGA", "GT", "MOD", "APTV", "DAN", "RACE",
            "VWAGY", "BMWYY", "POAHY", "MBGAF", "NSANY",
        ],
    }

    def search_companies_by_industry(self, industry: str) -> List[str]:
        """Return the ticker list for a given industry."""
        return self.INDUSTRY_MAP.get(industry.lower(), [])

    # ─────────────────────────────────────────────────────────────────────────
    # Core data fetch
    # ─────────────────────────────────────────────────────────────────────────
    def get_company_basic_info(self, symbol: str) -> Optional[Dict]:
        """Get basic company information via yfinance + light scraping."""
        try:
            print(f"  [INFO] Collecting data for {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or len(info) < 5:
                print(f"  [WARN] Limited data available for {symbol}")
                return None

            company_data = {
                "symbol": symbol.upper(),
                "company_name": info.get("longName", info.get("shortName", symbol)),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": self._safe_num(info, "marketCap"),
                "enterprise_value": self._safe_num(info, "enterpriseValue"),
                "revenue": self._safe_num(info, "totalRevenue"),
                "employees": self._safe_num(info, "fullTimeEmployees"),
                "founded_year": 0,
                "headquarters": self._format_location(info),
                "website": info.get("website", "N/A"),
                "description": self._get_description(info),
                "current_price": self._safe_num(info, "currentPrice"),
                "previous_close": self._safe_num(info, "previousClose"),
                "volume": self._safe_num(info, "volume"),
                "avg_volume": self._safe_num(info, "averageVolume"),
                "pe_ratio": self._safe_num(info, "trailingPE"),
                "pb_ratio": self._safe_num(info, "priceToBook"),
                "dividend_yield": self._safe_num(info, "dividendYield"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Light scrape for any gaps
            try:
                scraped = self.scrape_yahoo_finance_safe(symbol)
                for key, value in scraped.items():
                    if value and company_data.get(key) in [0, "N/A", "", None]:
                        company_data[key] = value
            except Exception:
                pass

            print(f"  [SUCCESS] Collected data for {symbol}")
            return company_data

        except Exception as e:
            print(f"  [ERROR] {symbol}: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # REFRESH – update price/volume for companies already in the DB
    # ─────────────────────────────────────────────────────────────────────────
    def refresh_company_data(self, symbol: str) -> Optional[Dict]:
        """
        Lightweight refresh: fetch only the fast-moving fields
        (price, volume, market_cap, pe_ratio) without re-scraping everything.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if not info:
                return None

            return {
                "symbol": symbol.upper(),
                "current_price": self._safe_num(info, "currentPrice"),
                "previous_close": self._safe_num(info, "previousClose"),
                "volume": self._safe_num(info, "volume"),
                "avg_volume": self._safe_num(info, "averageVolume"),
                "market_cap": self._safe_num(info, "marketCap"),
                "pe_ratio": self._safe_num(info, "trailingPE"),
                "pb_ratio": self._safe_num(info, "priceToBook"),
                "dividend_yield": self._safe_num(info, "dividendYield"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            print(f"  [ERROR] Refresh failed for {symbol}: {e}")
            return None

    def needs_refresh(self, last_updated_str: str, hours: int = 24) -> bool:
        """Return True if data is older than `hours` hours."""
        try:
            last = datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S")
            return datetime.now() - last > timedelta(hours=hours)
        except Exception:
            return True  # if we can't parse, treat as stale

    # ─────────────────────────────────────────────────────────────────────────
    # Stock history
    # ─────────────────────────────────────────────────────────────────────────
    def get_stock_history(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        try:
            print(f"  [DATA] Fetching stock history for {symbol}...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                hist["symbol"] = symbol
                print(f"  [SUCCESS] Retrieved {len(hist)} days of stock data")
            else:
                print(f"  [WARN] No stock history available for {symbol}")
            return hist
        except Exception as e:
            print(f"  [ERROR] Stock history for {symbol}: {e}")
            return pd.DataFrame()

    # ─────────────────────────────────────────────────────────────────────────
    # Executives & ratios
    # ─────────────────────────────────────────────────────────────────────────
    def get_executives(self, symbol: str) -> List[Dict]:
        try:
            print(f"  [DATA] Fetching executive data for {symbol}...")
            info = yf.Ticker(symbol).info
            executives = []
            for officer in info.get("companyOfficers", [])[:5]:
                executives.append({
                    "name": officer.get("name", "N/A"),
                    "title": officer.get("title", "N/A"),
                    "age": officer.get("age", 0),
                    "total_pay": officer.get("totalPay", 0),
                })
            print(f"  [SUCCESS] Found {len(executives)} executives")
            return executives
        except Exception as e:
            print(f"  [ERROR] Executives for {symbol}: {e}")
            return []

    def get_financial_ratios(self, symbol: str) -> Dict:
        try:
            print(f"  [DATA] Calculating financial ratios for {symbol}...")
            info = yf.Ticker(symbol).info
            ratios = {
                "pe_ratio": self._safe_num(info, "trailingPE"),
                "forward_pe": self._safe_num(info, "forwardPE"),
                "peg_ratio": self._safe_num(info, "pegRatio"),
                "price_to_sales": self._safe_num(info, "priceToSalesTrailing12Months"),
                "price_to_book": self._safe_num(info, "priceToBook"),
                "debt_to_equity": self._safe_num(info, "debtToEquity"),
                "roe": self._safe_num(info, "returnOnEquity"),
                "roa": self._safe_num(info, "returnOnAssets"),
                "profit_margin": self._safe_num(info, "profitMargins"),
                "operating_margin": self._safe_num(info, "operatingMargins"),
                "current_ratio": self._safe_num(info, "currentRatio"),
                "quick_ratio": self._safe_num(info, "quickRatio"),
            }
            ratio_count = len([r for r in ratios.values() if r > 0])
            print(f"  [SUCCESS] Calculated {ratio_count} financial ratios")
            return ratios
        except Exception as e:
            print(f"  [ERROR] Ratios for {symbol}: {e}")
            return {}

    # ─────────────────────────────────────────────────────────────────────────
    # Web scraping helper
    # ─────────────────────────────────────────────────────────────────────────
    def scrape_yahoo_finance_safe(self, symbol: str) -> Dict:
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = self.session.get(url, timeout=5)
            if response.status_code != 200:
                return {}
            soup = BeautifulSoup(response.content, "html.parser")
            data = {}
            try:
                el = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
                if el and el.text:
                    data["current_price"] = float(el.text.replace(",", ""))
            except Exception:
                pass
            try:
                for el in soup.find_all("td", {"data-test": "MARKET_CAP-value"}):
                    if el.text:
                        data["market_cap"] = self._parse_market_value(el.text)
                        break
            except Exception:
                pass
            print(f"  [WEB] Scraped {len(data)} additional fields from web")
            return data
        except Exception as e:
            print(f"  [WARN] Web scraping skipped for {symbol}: {e}")
            return {}

    # ─────────────────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────────────────
    def _safe_num(self, info: dict, key: str, default: float = 0) -> float:
        try:
            v = info.get(key, default)
            return float(v) if v is not None else default
        except (ValueError, TypeError):
            return default

    # Keep old name for backward compatibility
    def _safe_get_number(self, info, key, default=0):
        return self._safe_num(info, key, default)

    def _format_location(self, info: dict) -> str:
        try:
            parts = [p for p in [info.get("city"), info.get("state"), info.get("country")] if p]
            return ", ".join(parts) or "N/A"
        except Exception:
            return "N/A"

    def _get_description(self, info: dict) -> str:
        try:
            desc = info.get("longBusinessSummary", "")
            if desc:
                return desc[:500] + ("..." if len(desc) > 500 else "")
            return info.get("description", "N/A")
        except Exception:
            return "N/A"

    def _parse_market_value(self, value_str: str) -> float:
        try:
            s = value_str.strip().upper().replace("$", "").replace(",", "")
            if "T" in s:
                return float(s.replace("T", "")) * 1e12
            elif "B" in s:
                return float(s.replace("B", "")) * 1e9
            elif "M" in s:
                return float(s.replace("M", "")) * 1e6
            return float(s)
        except Exception:
            return 0

    def rate_limit_wait(self, seconds: float = 1):
        time.sleep(seconds)
