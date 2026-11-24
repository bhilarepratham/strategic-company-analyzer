# 📊 Strategic Company Data Analyzer

A Python-based financial intelligence platform that automatically collects, stores, and visualizes strategic company data across major industries. Built with Streamlit, it turns raw market data into an interactive, filterable dashboard.

---

## 🖥️ App Pages

### 🏠 Dashboard
- Live metrics: total companies tracked, unique sectors, average market cap
- Market leaders bar chart and industry distribution pie chart
- Sector & industry sidebar filters — all charts and the company table update instantly
- CSV export of the current view (filtered or full dataset)

### 📥 Data Collection
- Collect up to **25 companies per sector** across 6 industries (150 total)
- Custom symbol input for any publicly traded ticker
- **🔄 Refresh Prices** button — re-fetches current price, volume, market cap, and P/E for stale companies without a full re-collect
- Stale-data warning banner shows how many companies haven't been updated in 24+ hours
- Detailed per-symbol progress with expandable error log
- **🗂️ Collection Coverage** table shows, per industry, how many of its 25 tickers are already in the database
- **🌐 Discover More Companies** — go beyond the built-in lists: browse the full **S&P 500 by sector** and collect companies in small batches, or **search any listed company by name or ticker** and add it. Custom additions get full data (executives, ratios, 1-year price history)
- **"Only collect companies not already in the database"** (on by default) skips existing companies, so re-running an industry only fetches what's missing and never wastes API calls; untick it to force a full re-collect

### 📊 Visualizations
- Market Cap Analysis, Industry Analysis, and Performance Dashboard views
- Respects the same sidebar sector/industry filters as the Dashboard
- Market Cap vs Revenue scatter plot, P/E ratio distribution histogram

### 🔍 Company Analysis
- Hero banner with sector, industry, and last-updated timestamp
- Key metrics: Market Cap, Revenue, Employees, P/E Ratio
- **📖 About** — business description pulled from Yahoo Finance
- **📈 Stock Price History** — interactive line or candlestick chart with 1M / 3M / 6M / All time range selector, plus a trading volume bar chart below
- **👔 Executive Leadership** — name, title, age, and total compensation for top executives, with a table view option
- CSV export of the selected company's full price history
- Financial metrics panel: current price, volume, P/B ratio, dividend yield

---

## 🗂️ Project Structure

```
strategic-company-analyzer/
├── app.py                  # Streamlit UI — all 4 pages
├── data_collector.py       # Yahoo Finance data fetching + refresh logic
├── database_manager.py     # SQLite read/write for all 4 tables
├── visualizations.py       # Plotly chart helpers
├── config.py               # Configuration
├── company_data.db         # SQLite database (auto-created; commit to publish data)
├── .gitignore              # Excludes __pycache__, venvs, secrets
└── requirements.txt
```

### Database Tables
| Table | Contents |
|---|---|
| `companies` | Core company info, financials, last_updated timestamp |
| `stock_history` | Daily OHLCV price data (1 year per company) |
| `executives` | Name, title, age, total pay for top 5 officers |
| `financial_ratios` | PE, PB, PEG, ROE, ROA, margins, and more |

---

## 🏭 Supported Industries (25 companies each)

| Industry | Example Tickers |
|---|---|
| 🖥️ Technology | AAPL, MSFT, NVDA, GOOGL, META, CRWD, SNOW, PLTR … |
| 💼 Finance | JPM, GS, V, MA, BLK, PYPL, SPGI, CME … |
| 🏥 Healthcare | JNJ, LLY, UNH, PFE, ISRG, VRTX, REGN … |
| 🛒 Retail | WMT, COST, HD, MCD, NKE, ABNB, DASH … |
| ⚡ Energy | XOM, CVX, NEE, COP, SLB, DUK, SRE … |
| 🚗 Automotive | TSLA, GM, F, RIVN, NIO, RACE, APTV … |

---

## ⚙️ Installation

```bash
git clone https://github.com/bhilarepratham/strategic-company-analyzer.git
cd strategic-company-analyzer
pip install -r requirements.txt
streamlit run app.py
```

### Deployment (Streamlit Community Cloud)
The app is deployed from this repo. Streamlit Cloud's filesystem is not persistent, so the SQLite file committed to the repo (`company_data.db`) is what the live app starts with. To publish fresh data: run the app locally, use **Collect** and **Refresh Prices**, then commit the updated `company_data.db` and push.

### Automated data updates (GitHub Actions)
`.github/workflows/update-data.yml` runs `collect_all.py --sp500` on weekdays (or on demand from the Actions tab). Each run refreshes prices for every company already tracked and adds up to 100 new S&P 500 companies, so the database grows toward the full index over time. The updated `company_data.db` is committed automatically.

### Requirements
```
streamlit
yfinance
pandas
plotly
requests
beautifulsoup4
lxml
```

---

## 🔄 Data Flow

```
Yahoo Finance API
      │
      ▼
data_collector.py  ──►  database_manager.py (SQLite)
                                │
                                ▼
                           app.py (Streamlit UI)
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               Dashboard  Visualizations  Company Analysis
```

1. **Collect** — `data_collector.py` fetches company info, stock history, executives, and financial ratios from Yahoo Finance
2. **Store** — `database_manager.py` writes to SQLite with upsert logic (no duplicates)
3. **Cache** — Streamlit's `@st.cache_data(ttl=300)` prevents redundant DB queries on page navigation
4. **Refresh** — lightweight refresh re-fetches only price/volume fields for companies older than 24 hours
5. **Visualize** — Plotly charts render inline; all views respect sidebar filters

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|---|---|
| **Python** | Core language |
| **Streamlit** | Web UI framework |
| **yfinance** | Yahoo Finance API wrapper |
| **Plotly** | Interactive charts |
| **SQLite** | Local data persistence |
| **BeautifulSoup** | Supplemental web scraping |
| **Pandas** | Data manipulation |
| **Claude (AI Assistant)** | Code generation, debugging, and optimization |

---

## 📌 Skills Demonstrated

- End-to-end data pipeline: collection → storage → visualization
- REST API integration (Yahoo Finance)
- Relational database design (SQLite, 4 normalized tables)
- Interactive web application development (Streamlit)
- Financial data analysis and charting (Plotly candlestick, OHLCV)
- Performance optimization (query caching, lightweight refresh)
- UI/UX design (sidebar filters, responsive layout, CSV export)

*Suitable for roles in data analysis, business analytics, financial technology, and market intelligence.*
