import yfinance as yf
import pandas as pd
import schedule
import time
import matplotlib.pyplot as plt

# Fetch dividend data for a single stock
def fetch_dividend_data(ticker):
    stock = yf.Ticker(ticker)
    dividend_data = stock.dividends  # Fetch dividends history
    return dividend_data

# Calculate total expected dividend income for a single stock
def calculate_dividend_income(ticker, shares_owned):
    dividends = fetch_dividend_data(ticker)
    if dividends.empty:
        print(f"No dividend data available for {ticker}")
        return 0
    else:
        # Sum up the total dividends paid in the last year
        total_dividends_per_share = dividends.last('365D').sum()  # Dividends in the last 365 days
        total_income = total_dividends_per_share * shares_owned
        return total_income

# Watchlist with the number of shares owned for each stock
portfolio = {
    "AAPL": 50,   # 50 shares of Apple
    "MSFT": 30,   # 30 shares of Microsoft
    "T": 100,     # 100 shares of AT&T
    "JNJ": 25     # 25 shares of Johnson & Johnson
}

# Track expected dividend income for all stocks in the portfolio
def track_dividend_income(portfolio):
    dividend_summary = pd.DataFrame(columns=["Stock", "Shares Owned", "Expected Dividend Income"])

    for stock, shares_owned in portfolio.items():
        income = calculate_dividend_income(stock, shares_owned)
        dividend_summary = pd.concat([dividend_summary, pd.DataFrame({"Stock": [stock], "Shares Owned": [shares_owned], "Expected Dividend Income": [income]})])

    return dividend_summary

# Create a dashboard to visualize expected dividend income for all stocks
def create_dashboard(portfolio):
    income_summary = track_dividend_income(portfolio)

    fig, ax = plt.subplots(figsize=(10, 6))
    income_summary.plot(x="Stock", y="Expected Dividend Income", kind="bar", ax=ax)
    plt.title("Expected Dividend Income from Portfolio")
    plt.xlabel("Stock")
    plt.ylabel("Expected Dividend Income (in USD)")
    plt.show()

# Job to calculate and save dividend income daily
def job():
    print("Updating expected dividend income data...")
    summary = track_dividend_income(portfolio)
    summary.to_csv('dividend_income_tracker.csv', index=False)
    print(summary)

# Schedule to run every day at 10 AM
schedule.every().day.at("10:00").do(job)

# Initial calculation and dashboard creation
create_dashboard(portfolio)

# Start the schedule loop after creating the dashboard
while True:
    schedule.run_pending()
    time.sleep(1)
