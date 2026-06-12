import sqlite3
import pandas as pd
from typing import Dict, List, Optional
import json
from datetime import datetime
import os


class DatabaseManager:

    def __init__(self, db_path: str = "company_data.db"):
        self.db_path = db_path
        self.ensure_valid_database()
        self.init_database()

    def ensure_valid_database(self):
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                conn.close()
                print("✅ Database file is valid")
            except sqlite3.DatabaseError as e:
                print(f"⚠️ Database corrupted: {e}")
                print("🔄 Deleting corrupted database and creating new one...")
                try:
                    os.remove(self.db_path)
                    print("✅ Corrupted database deleted")
                except Exception as del_error:
                    print(f"❌ Could not delete database: {del_error}")

    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    company_name TEXT,
                    sector TEXT,
                    industry TEXT,
                    market_cap REAL,
                    enterprise_value REAL,
                    revenue REAL,
                    employees INTEGER,
                    founded_year INTEGER,
                    headquarters TEXT,
                    website TEXT,
                    description TEXT,
                    current_price REAL,
                    previous_close REAL,
                    volume INTEGER,
                    avg_volume INTEGER,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    dividend_yield REAL,
                    last_updated TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date TEXT,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    name TEXT,
                    title TEXT,
                    age INTEGER,
                    total_pay REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_ratios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    pe_ratio REAL,
                    forward_pe REAL,
                    peg_ratio REAL,
                    price_to_sales REAL,
                    price_to_book REAL,
                    debt_to_equity REAL,
                    roe REAL,
                    roa REAL,
                    profit_margin REAL,
                    operating_margin REAL,
                    current_ratio REAL,
                    quick_ratio REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            if os.path.exists(self.db_path):
                try:
                    os.remove(self.db_path)
                    print("🔄 Deleted problematic database, please restart the app")
                except Exception:
                    pass

    def insert_company_data(self, company_data: Dict) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO companies
                (symbol, company_name, sector, industry, market_cap, enterprise_value, revenue,
                 employees, founded_year, headquarters, website, description, current_price,
                 previous_close, volume, avg_volume, pe_ratio, pb_ratio, dividend_yield, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_data.get('symbol'),
                company_data.get('company_name'),
                company_data.get('sector'),
                company_data.get('industry'),
                company_data.get('market_cap', 0),
                company_data.get('enterprise_value', 0),
                company_data.get('revenue', 0),
                company_data.get('employees', 0),
                company_data.get('founded_year', 0),
                company_data.get('headquarters', ''),
                company_data.get('website', ''),
                company_data.get('description', ''),
                company_data.get('current_price', 0),
                company_data.get('previous_close', 0),
                company_data.get('volume', 0),
                company_data.get('avg_volume', 0),
                company_data.get('pe_ratio', 0),
                company_data.get('pb_ratio', 0),
                company_data.get('dividend_yield', 0),
                company_data.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting company data: {str(e)}")
            return False

    def insert_stock_history(self, symbol: str, stock_df: pd.DataFrame) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM stock_history WHERE symbol = ?', (symbol,))
            for date, row in stock_df.iterrows():
                cursor.execute('''
                    INSERT INTO stock_history
                    (symbol, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    date.strftime('%Y-%m-%d'),
                    float(row.get('Open', 0)),
                    float(row.get('High', 0)),
                    float(row.get('Low', 0)),
                    float(row.get('Close', 0)),
                    int(row.get('Volume', 0))
                ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting stock history: {str(e)}")
            return False

    def insert_executives(self, symbol: str, executives: List[Dict]) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM executives WHERE symbol = ?', (symbol,))
            for exec_data in executives:
                cursor.execute('''
                    INSERT INTO executives (symbol, name, title, age, total_pay)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    exec_data.get('name', ''),
                    exec_data.get('title', ''),
                    exec_data.get('age', 0),
                    exec_data.get('total_pay', 0)
                ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting executives: {str(e)}")
            return False

    def insert_financial_ratios(self, symbol: str, ratios: Dict) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM financial_ratios WHERE symbol = ?', (symbol,))
            cursor.execute('''
                INSERT INTO financial_ratios
                (symbol, pe_ratio, forward_pe, peg_ratio, price_to_sales, price_to_book,
                 debt_to_equity, roe, roa, profit_margin, operating_margin, current_ratio, quick_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                ratios.get('pe_ratio', 0),
                ratios.get('forward_pe', 0),
                ratios.get('peg_ratio', 0),
                ratios.get('price_to_sales', 0),
                ratios.get('price_to_book', 0),
                ratios.get('debt_to_equity', 0),
                ratios.get('roe', 0),
                ratios.get('roa', 0),
                ratios.get('profit_margin', 0),
                ratios.get('operating_margin', 0),
                ratios.get('current_ratio', 0),
                ratios.get('quick_ratio', 0)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting ratios: {str(e)}")
            return False

    def get_companies_by_industry(self, industry: str) -> pd.DataFrame:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                'SELECT * FROM companies WHERE industry LIKE ? OR sector LIKE ? ORDER BY market_cap DESC',
                conn, params=[f'%{industry}%', f'%{industry}%']
            )
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting companies by industry: {str(e)}")
            return pd.DataFrame()

    def get_all_companies(self) -> pd.DataFrame:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('SELECT * FROM companies ORDER BY market_cap DESC', conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting all companies: {str(e)}")
            return pd.DataFrame()

    def get_stock_history_by_symbol(self, symbol: str) -> pd.DataFrame:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                'SELECT * FROM stock_history WHERE symbol = ? ORDER BY date',
                conn, params=[symbol]
            )
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting stock history: {str(e)}")
            return pd.DataFrame()

    # ── NEW: fetch executives for a given symbol ──────────────────────────────
    def get_executives_by_symbol(self, symbol: str) -> pd.DataFrame:
        """Return executives for a company as a DataFrame, or empty if none."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                'SELECT name, title, age, total_pay FROM executives WHERE symbol = ? ORDER BY total_pay DESC',
                conn, params=[symbol]
            )
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting executives for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_company_count(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM companies')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting company count: {str(e)}")
            return 0
