import yfinance as yf
import matplotlib.pyplot as plt
import talib
from datetime import datetime

from menu import StockMenu
from technical import TechnicalAnalyzer

class StockAnalyzer:
    
    @staticmethod
    def validate_date(date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            print("Invalid date format. Please enter the date in the format YYYY-MM-DD.")
            return False

    @staticmethod
    def fetch_stock_data(symbol, start_date, end_date):
        data = yf.download(symbol, start=start_date, end=end_date)
        data.reset_index(inplace=True)
        return data

    @staticmethod
    def plot_closing_prices(data, symbol):
        plt.subplot(3, 1, 1)
        plt.plot(data['Date'], data['Close'], label='Close Price')
        plt.title(f'Historical Stock Prices for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.legend()

    @staticmethod
    def plot_moving_averages(data):
        plt.subplot(3, 1, 2)
        plt.plot(data['Date'], data['Close'], label='Close Price')
        plt.plot(data['Date'], data['MA20'], label='20-day MA')
        plt.plot(data['Date'], data['MA50'], label='50-day MA')
        plt.title('Historical Stock Prices with Moving Averages')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()

    @staticmethod
    def plot_rsi(data):
        plt.subplot(3, 1, 3)
        plt.plot(data['Date'], data['RSI'], label='RSI')
        plt.title('Relative Strength Index (RSI)')
        plt.xlabel('Date')
        plt.ylabel('RSI Value')
        plt.legend()

    @staticmethod
    def plot_bollinger_bands(data):
        if 'UpperBand' not in data.columns:
            data = TechnicalAnalyzer.calculate_bollinger_bands(data)

        plt.subplot(3, 1, 2)
        plt.plot(data['Date'], data['Close'], label='Close Price')
        plt.plot(data['Date'], data['UpperBand'], label='Upper Band')
        plt.plot(data['Date'], data['MiddleBand'], label='Middle Band')
        plt.plot(data['Date'], data['LowerBand'], label='Lower Band')
        plt.title('Bollinger Bands')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()

    @staticmethod
    def plot_macd(data):
        plt.subplot(3, 1, 3)
        plt.plot(data['Date'], data['MACD'], label='MACD')
        plt.plot(data['Date'], data['SignalLine'], label='Signal Line')
        plt.bar(data['Date'], data['MACD_Histogram'], label='MACD Histogram', color='gray')
        plt.title('Moving Average Convergence Divergence (MACD)')
        plt.xlabel('Date')
        plt.ylabel('MACD Value')
        plt.legend()

    def main(self):
        stock_analyzer = StockAnalyzer()
        stock_menu = StockMenu()

        while True:
            stock_menu.display_menu()
            choice = stock_menu.get_user_choice()

            if choice == '1':
                symbol = input("Enter stock symbol: ")
                while True:
                    start_date = input("Enter start date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(start_date):
                        break

                while True:
                    end_date = input("Enter end date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(end_date):
                        break

                data = stock_analyzer.fetch_stock_data(symbol, start_date, end_date)
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['MA50'] = data['Close'].rolling(window=50).mean()
                data['RSI'] = talib.RSI(data['Close'])
                data = TechnicalAnalyzer.calculate_bollinger_bands(data)  # Updated to use Bollinger Bands function

                plt.figure(figsize=(12, 12))
                StockAnalyzer.plot_closing_prices(data, symbol)
                StockAnalyzer.plot_moving_averages(data)
                StockAnalyzer.plot_rsi(data)
                StockAnalyzer.plot_bollinger_bands(data)  # Added Bollinger Bands plotting
                plt.tight_layout()
                plt.show()

            elif choice == '2':
                symbol = input("Enter stock symbol: ")
                while True:
                    start_date = input("Enter start date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(start_date):
                        break

                while True:
                    end_date = input("Enter end date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(end_date):
                        break

                data = stock_analyzer.fetch_stock_data(symbol, start_date, end_date)
                stock_analyzer.plot_closing_prices(data, symbol)
                plt.tight_layout()
                plt.show()

            elif choice == '3':
                symbol = input("Enter stock symbol: ")
                while True:
                    start_date = input("Enter start date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(start_date):
                        break

                while True:
                    end_date = input("Enter end date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(end_date):
                        break

                data = stock_analyzer.fetch_stock_data(symbol, start_date, end_date)
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['MA50'] = data['Close'].rolling(window=50).mean()
                StockAnalyzer.plot_moving_averages(data)
                StockAnalyzer.plot_bollinger_bands(data)
                plt.tight_layout()
                plt.show()

            elif choice == '4':
                symbol = input("Enter stock symbol: ")
                while True:
                    start_date = input("Enter start date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(start_date):
                        break

                while True:
                    end_date = input("Enter end date (YYYY-MM-DD): ")
                    if stock_analyzer.validate_date(end_date):
                        break

                data = stock_analyzer.fetch_stock_data(symbol, start_date, end_date)
                data['RSI'] = talib.RSI(data['Close'])
                StockAnalyzer.plot_rsi(data)
                plt.tight_layout()
                plt.show()

            elif choice == '5':
                print("Exiting the Stock Analysis Tool. Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    stock_analyzer = StockAnalyzer()
    stock_analyzer.main()
