import argparse
import re
import os.path

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
    parser = argparse.ArgumentParser(description='Find NetScaler cookies in a file and write them to another file.')
    parser.add_argument('input_file', metavar='input_file', type=str, help='the name of the input file')
    parser.add_argument('output_file', metavar='output_file', type=str, help='the name of the output file')
    args = parser.parse_args()

    # Find the NetScaler cookies in the input file
    cookies_list = find_cookies(args.input_file)

    if cookies_list:
        # Write the cookies to the output file
        with open(args.output_file, 'w') as f:
            for cookie in cookies_list:
                f.write(cookie + '\n')
        print(f'Success: {len(cookies_list)} cookies found and written to {args.output_file}.')
    else:
        print(f'No NetScaler cookies found in {args.input_file}.')

if __name__ == '__main__':
    main()
