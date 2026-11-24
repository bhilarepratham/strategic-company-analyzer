"""Collect/refresh company data for every industry without the Streamlit UI.

Usage:
    python collect_all.py          # collect missing companies, refresh existing ones
    python collect_all.py --full   # re-collect everything from scratch
    python collect_all.py --sp500  # also add up to 100 new S&P 500 companies per run
"""
import sqlite3
import sys
import time

from data_collector import CompanyDataCollector
from database_manager import DatabaseManager

INDUSTRIES = ["technology", "finance", "healthcare", "retail", "energy", "automotive"]
DELAY = 0.5  # seconds between companies, to be gentle with Yahoo Finance
SP500_BATCH = 100  # new S&P 500 companies added per run (keeps runs short)


def collect_full(collector, db, symbol):
    data = collector.get_company_basic_info(symbol)
    if not data:
        return False
    db.insert_company_data(data)
    for fetch, store in (
        (collector.get_executives, db.insert_executives),
        (collector.get_financial_ratios, db.insert_financial_ratios),
    ):
        try:
            result = fetch(symbol)
            if result:
                store(symbol, result)
        except Exception as e:
            print(f"  [WARN] {symbol}: {e}")
    try:
        hist = collector.get_stock_history(symbol)
        if not hist.empty:
            db.insert_stock_history(symbol, hist)
    except Exception as e:
        print(f"  [WARN] {symbol} history: {e}")
    return True


def refresh_existing(collector, db, symbol):
    fresh = collector.refresh_company_data(symbol)
    if not fresh:
        return False
    conn = sqlite3.connect(db.db_path)
    conn.execute(
        """UPDATE companies
           SET current_price=?, previous_close=?, volume=?, avg_volume=?,
               market_cap=?, pe_ratio=?, pb_ratio=?, dividend_yield=?, last_updated=?
           WHERE symbol=?""",
        (fresh["current_price"], fresh["previous_close"], fresh["volume"],
         fresh["avg_volume"], fresh["market_cap"], fresh["pe_ratio"],
         fresh["pb_ratio"], fresh["dividend_yield"], fresh["last_updated"],
         fresh["symbol"]),
    )
    conn.commit()
    conn.close()
    try:
        hist = collector.get_stock_history(symbol)
        if not hist.empty:
            db.insert_stock_history(symbol, hist)
    except Exception as e:
        print(f"  [WARN] {symbol} history: {e}")
    return True


def main():
    full = "--full" in sys.argv
    collector = CompanyDataCollector()
    db = DatabaseManager()
    have = set(db.get_all_companies()["symbol"].tolist())

    ok, failed = 0, []
    for industry in INDUSTRIES:
        print(f"\n=== {industry.upper()} ===")
        for symbol in collector.search_companies_by_industry(industry):
            if full or symbol not in have:
                success = collect_full(collector, db, symbol)
            else:
                success = refresh_existing(collector, db, symbol)
            if success:
                ok += 1
            else:
                failed.append(symbol)
            time.sleep(DELAY)

    if "--sp500" in sys.argv:
        sp = collector.get_sp500_constituents()
        have = set(db.get_all_companies()["symbol"].tolist())
        todo = [s for s in sp["symbol"].tolist() if s not in have][:SP500_BATCH]
        print(f"\n=== S&P 500 (adding up to {SP500_BATCH} new companies; {len(todo)} queued) ===")
        for symbol in todo:
            if collect_full(collector, db, symbol):
                ok += 1
            else:
                failed.append(symbol)
            time.sleep(DELAY)

    total = db.get_company_count()
    print(f"\nDone. Succeeded: {ok} | Failed: {len(failed)} | Companies in DB: {total}")
    if failed:
        print("Failed tickers:", ", ".join(failed))
    sys.exit(0 if ok > 0 else 1)  # only fail the run if nothing worked


if __name__ == "__main__":
    main()
