import sys
from data_processor import DataProcessor
from menu_logic import main_menu

if __name__ == "__main__":
    dp = DataProcessor()
    main_menu(dp)
