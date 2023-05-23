import argparse
import tkinter as tk
from tkinter import filedialog
import openpyxl
import re
import os.path


def get_excel_file_path():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    return file_path


def extract_source_responses(excel_file_path, output_file_path):
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
    regex = r'NSC_[a-zA-Z0-9\-\_\.]*=[0-9a-f]{8}[0-9a-f]{8}.*[0-9a-f]{4}'

    # Loop through the lines in the file
    for line in file_contents.splitlines():
        # Look for a string that contains a NetScaler cookie
        if isinstance(line, str):
            line = line.strip().replace('\n', '')  # Strip whitespace and newlines from the line
            match = re.search(regex, line)
            if match:
                if ';' in match.group():
                    # Skip to the next line if the semicolon is found in the cookie string
                    continue
                else:
                    cookies.append(match.group())

    # Return the cookies list
    return cookies


def main():
    parser = argparse.ArgumentParser(description='Extract source responses from an Excel file')
    parser.add_argument('excel_file', help='path to the Excel file to extract data from')
    parser.add_argument('output_file', help='path to the output file to save the extracted data to')
    parser.add_argument('--cookies_file', help='path to the file containing NetScaler cookies')

    # Add input validation for excel_file and output_file arguments
    args = parser.parse_args()
    if not os.path.isfile(args.excel_file):
        print(f"Error: '{args.excel_file}' does not exist or is not a file.")
        parser.print_help()
        return
    if not args.output_file.endswith('.txt'):
        print("Error: The output file must be a text file with a '.txt' extension.")
        parser.print_help()
        return

    # If a cookies file is specified, find the cookies in the file
    cookies = []
    if args.cookies_file:
        if not os.path.isfile(args.cookies_file):
            print(f"Error: '{args.cookies_file}' does not exist or is not a file.")
            parser.print_help()
            return
        cookies = find_cookies(args.cookies_file)

    # If there are cookies, add them to the HTTP request headers
    headers = {}
    if cookies:
        headers['Cookie'] = '; '.join(cookies)

    # Extract the source responses from the Excel file
    extract_source_responses(args.excel_file, args.output_file)

if __name__ == '__main__':
    main()