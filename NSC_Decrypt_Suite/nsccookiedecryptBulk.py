import re
import string
from string import ascii_letters
import argparse
import sys

def parseCookie(cookie):
    """Parse Citrix NetScaler cookie
    @param cookie: Citrix NetScaler cookie
    @return: Returns ServiceName, ServerIP and ServerPort"""

    s = re.search(
        'NSC_([a-zA-Z0-9\-\_\.]*)=[0-9a-f]{8}([0-9a-f]{8}).*([0-9a-f]{4})$', cookie)
    if s is not None:
        servicename = s.group(1)  # first group is name ([a-z\-]*)
        serverip = int(s.group(2), 16)
        serverport = int(s.group(3), 16)
    else:
        raise Exception('Could not parse cookie')
    return servicename, serverip, serverport


def decryptServiceName(servicename):
    """Decrypts the Caesar Subsitution Cipher Encryption used on the Netscaler Cookie Name
    @param cookie Citrix NetScaler cookie
    @type cookie: String
    @return: service name"""

    # This decrypts the Caesar Subsitution Cipher Encryption used on the Netscaler Cookie Name
    trans = str.maketrans('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
                          'zabcdefghijklmnopqrstuvwxyZABCDEFGHIJKLMNOPQRSTUVWXY')
    realname = servicename.translate(trans)
    return realname


def decryptServerIP(serverip):
    """Decrypts the XOR encryption used for the Netscaler Server IP
    @param cookie Citrix NetScaler cookie
    @type cookie: String
    @return: XORed server IP based on ipkey"""

    ipkey = 0x03081e11
    decodedip = hex(serverip ^ ipkey)
    t = decodedip[2:10].zfill(8)
    realip = '.'.join(str(int(i, 16))
                      for i in ([t[i:i+2] for i in range(0, len(t), 2)]))
    return realip


def decryptServerPort(serverport):
    """Decrypts the XOR encryption used on the Netscaler Server Port
    @param cookie Citrix NetScaler cookie
    @type cookie: String
    @return: XORed server port"""

    portkey = 0x3630
    decodedport = serverport ^ portkey
    realport = str(decodedport)
    return realport


def decryptCookie(cookie):
    """Make entire decryption of Citrix NetScaler cookie
    @param cookie: Citrix NetScaler cookie
    @return: Returns RealName, RealIP and RealPort"""

    servicename, serverip, serverport = parseCookie(cookie)
    realname = decryptServiceName(servicename)
    realip = decryptServerIP(serverip)
    realport = decryptServerPort(serverport)
    return realname, realip, realport


def validate_input_file(file_name):
    """Validates the input file"""
    try:
        with open(file_name, 'r') as f:
            f.readlines()
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"Input file {file_name} not found.")
    except:
        raise argparse.ArgumentTypeError(f"Error reading input file {file_name}.")
    return file_name


def validate_output_file(file_name):
    """Validates the output file"""
    try:
        with open(file_name, 'w') as f:
            pass
    except:
        raise argparse.ArgumentTypeError(f"Error writing to output file {file_name}")

def main():
    parser = argparse.ArgumentParser(description='Decrypt Citrix NetScaler cookies')
    parser.add_argument('input_file', type=validate_input_file, help='Input file')
    parser.add_argument('output_file', type=validate_output_file, help='Output file')
    args = parser.parse_args()

    with open(args.input_file, 'r') as input_file:
        with open(args.output_file, 'w') as output_file:
            for line in input_file:
                line = line.strip()
                if line.startswith('NSC_'):
                    try:
                        realname, realip, realport = decryptCookie(line)
                        output_file.write(f'{realname},{realip},{realport}\n')
                    except Exception as e:
                        print(f'Error processing line "{line}": {e}', file=sys.stderr)

if __name__ == '__main__':
    main()