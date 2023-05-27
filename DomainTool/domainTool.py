import sys
from tkinter import Tk, filedialog
from tkinter.filedialog import askopenfilename
from data_processor import DataProcessor
from menu import main_menu

def main():
    dp = DataProcessor()
    main_menu(dp)

if __name__ == "__main__":
    main()