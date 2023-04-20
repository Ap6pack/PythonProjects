import openpyxl

# Open the Excel sheet
workbook = openpyxl.load_workbook('example.xlsx')

# Select the sheet you want to read
sheet = workbook.active

# Find the index of the column with the header 'Source response'
source_response_col = None
for cell in sheet[1]:
    if cell.value == 'Source response':
        source_response_col = cell.column

if source_response_col is not None:
    # Open a text file for writing
    with open('output.txt', 'w', encoding='utf-8') as f:
    
        # Loop through the cells in the 'Source response' column
        for row in sheet.iter_rows(min_row=2, min_col=source_response_col, max_col=source_response_col, values_only=True):
            # Remove whitespace from the cell value
            cell_value = str(row[0]).strip()
        
            # Write the cell value to the text file
            f.write(cell_value + '\n')
else:
    print("Column 'Source response' not found in worksheet")