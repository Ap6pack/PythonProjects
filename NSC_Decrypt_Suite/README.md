# Excel to Text Converter
This Python script uses the openpyxl module to read an Excel sheet and extract a specific column containing text. The script then writes the text values to a text file.

## Requirements
This script requires the openpyxl module to be installed. You can install it via pip: pip install openpyxl

## Usage
To use this script, follow these steps:

1. Place the example.xlsx file in the same directory as the excel2text.py script.
2. Run the excel2text.py script.
3. Check the same directory for the output.txt file containing the extracted text.

# NSCCookieParserTxt.py

This Python 3 script, nsccookieparsertxt.py, is designed to parse a text file and extract NetScaler cookies. The extracted cookies are stored in a list and can be written to a file.

## Usage

To use this script, save the file as nsccookieparsertxt.py and place it in the same directory as the text file that you want to parse. Then, in a terminal or command prompt, navigate to the directory and run the following command: python nsccookieparsertxt.py

The script will prompt you to enter the name of the text file that you want to parse. Enter the name of the file (including the file extension) and press Enter. The script will then search the file for NetScaler cookies and extract them into a list. The list is then written to a file named input.txt in the same directory.

## Requirements
This script requires Python 3 to run. No additional libraries or packages are required.


# Citrix NetScaler Cookie Bulk Decryptor

This Python script allows you to bulk decrypt Citrix NetScaler cookies, extracting the service name, server IP, and server port for each cookie.

## Dependencies

This script requires the following dependencies:
- Python 3

## Usage

1. Create a file named `input.txt` in the same directory as the script.
2. Add one or more Citrix NetScaler cookies per line to the `input.txt` file.
3. Run the script using the following command: python nsccookiedercyptBulk.py
4. The decrypted output will be written to a file named `output.txt` in the same directory as the script.

The output for each input cookie will be written to `output.txt` in the following format:
NSC: [input cookie]
vServer Name=[decrypted service name]
vServer IP=[decrypted server IP]
vServer Port=[decrypted server port]

## How it Works

The script works by first parsing each input cookie to extract the service name, server IP, and server port. 
Next, it decrypts the service name using a Caesar substitution cipher encryption. 
Then, it decrypts the server IP and server port using XOR encryption.
Finally, it outputs the decrypted service name, server IP, and server port for each input cookie to a file.

## License

This project is licensed under the [MIT License](https://github.com/Ap6pack/PythonProjects/NSC_Decrypt_Suite/blob/main/LICENSE).

