import re

def find_cookies(file_name):
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

# Call the function and assign the returned list to a variable
cookies_list = find_cookies('example.txt')

# Write the cookies to a file
with open('input.txt', 'w') as f:
    for cookie in cookies_list:
        f.write(cookie + '\n')