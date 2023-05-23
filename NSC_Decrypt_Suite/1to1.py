import argparse
import tkinter as tk
from tkinter import filedialog
import openpyxl
import re
import os.path
import string
import requests


def get_excel_file_path():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    return file_path


def extract_source_responses(excel_file_path, output_file_path, cookies_file_path=None):
    # Open the Excel sheet
    try:
        workbook = openpyxl.load_workbook(excel_file_path)
    except FileNotFoundError:
        print(f"Error: Excel file '{excel_file_path}' not found")
        return
    except openpyxl.utils.exceptions.InvalidFileException:
        print(f"Error: '{excel_file_path}' is not a valid Excel file")
        return

    # Select the sheet you want to read
    sheet = workbook.active

    # Find the index of the column with the header 'Source response'
    source_response_col = None
    for cell in sheet[1]:
        if cell.value == 'Source response':
            source_response_col = cell.column

    if source_response_col is not None:
        # Open the text file for writing
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                # Loop through the cells in the 'Source response' column
                for row in sheet.iter_rows(min_row=2, min_col=source_response_col, max_col=source_response_col, values_only=True):
                    # Remove whitespace from the cell value
                    cell_value = str(row[0]).strip()

                    # Write the cell value to the text file
                    f.write(cell_value + '\n')

            # Show a success message
            print(f"The output file has been saved to {output_file_path}")
        except PermissionError:
            print(f"Error: You do not have permission to write to '{output_file_path}'")
            return
    else:
        # Show an error message
        print("Error: Column 'Source response' not found in worksheet")
        return

    # If a cookies file is specified, find the cookies in the file
    cookies = []
    if cookies_file_path:
        if not os.path.isfile(cookies_file_path):
            print(f"Error: '{cookies_file_path}' does not exist or is not a file.")
            return
        cookies = find_cookies(cookies_file_path)

    # If there are cookies, add them to the HTTP request headers
    headers = {}
    if cookies:
        headers['Cookie'] = '; '.join(cookies)

    # Use headers in HTTP request
    url = 'https://example.com'
    response = requests.get(url, headers=headers)
    # Do something with the response, e.g. extract data from HTML or JSON

def find_cookies(file_name):
    # Check if the file exists
    if not os.path.isfile(file_name):
        print(f'Error: {file_name} does not exist.')
        return []

    # Open the text file
    with open(file_name, 'r') as f:
        # Read the entire file into a string variable
        file_contents = f.read()

    # Create a list to store the NetScaler cookies
    cookies = []

    # Define the regular expression to match the cookie string
    regex = r'NSC_[a-zA-Z0-9\-\_\.]*=[0-9a-f]{8}[0-9a
