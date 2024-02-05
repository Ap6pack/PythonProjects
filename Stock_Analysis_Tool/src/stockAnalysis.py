import yfinance as yf
import matplotlib.pyplot as plt
import talib
from datetime import datetime

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        print("Invalid date format. Please enter the date in the format YYYY-MM-DD.")
        return False

def fetch_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

def plot_closing_prices(data, symbol):
    plt.subplot(3, 1, 1)
    plt.plot(data['Date'], data['Close'], label='Close Price')
    plt.title(f'Historical Stock Prices for {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()

def plot_moving_averages(data):
    plt.subplot(3, 1, 2)
    plt.plot(data['Date'], data['Close'], label='Close Price')
    plt.plot(data['Date'], data['MA20'], label='20-day MA')
    plt.plot(data['Date'], data['MA50'], label='50-day MA')
    plt.title('Historical Stock Prices with Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

def plot_rsi(data):
    plt.subplot(3, 1, 3)
    plt.plot(data['Date'], data['RSI'], label='RSI')
    plt.title('Relative Strength Index (RSI)')
    plt.xlabel('Date')
    plt.ylabel('RSI Value')
    plt.legend()

def main():
    symbol = input("Enter stock symbol: ")

    # Validate start date
    while True:
        start_date = input("Enter start date (YYYY-MM-DD): ")
        if validate_date(start_date):
            break

    # Validate end date
    while True:
        end_date = input("Enter end date (YYYY-MM-DD): ")
        if validate_date(end_date):
            break

    data = fetch_stock_data(symbol, start_date, end_date)

    # Calculate 20-day and 50-day moving averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    # Calculate RSI
    data['RSI'] = talib.RSI(data['Close'])

    plt.figure(figsize=(12, 12))

    plot_closing_prices(data, symbol)
    plot_moving_averages(data)
    plot_rsi(data)

    plt.tight_layout()  # Adjust layout to prevent overlapping
    plt.show()

if __name__ == "__main__":
    main()
