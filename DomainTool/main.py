import sys
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from data_processor import DataProcessor
from menu import show_menu

def main():
    dp = DataProcessor()
    show_menu(dp)

if __name__ == "__main__":
    main()
