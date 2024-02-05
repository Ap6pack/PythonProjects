class StockMenu:
    @staticmethod
    def display_menu():
        print("\nStock Analysis Tool Menu:")
        print("1. Fetch Historical Stock Data")
        print("2. Plot Closing Prices")
        print("3. Display Moving Averages")
        print("4. Visualize Relative Strength Index (RSI)")
        print("5. Exit")

    @staticmethod
    def get_user_choice():
        return input("Enter your choice (1-5): ")