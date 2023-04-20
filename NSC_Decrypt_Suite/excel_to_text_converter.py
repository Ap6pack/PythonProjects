import argparse
import tkinter as tk
from tkinter import filedialog
import openpyxl

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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract source responses from an Excel file')
    parser.add_argument('excel_file', help='path to the Excel file to extract data from')
    parser.add_argument('output_file', help='path to the output file to save data to')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        return

    if args.verbose:
        print("Extracting source responses from Excel file...")

    extract_source_responses(args.excel_file, args.output_file)

if __name__ == '__main__':
    main()
