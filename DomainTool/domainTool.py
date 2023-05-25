import os
import xml.etree.ElementTree as ET
import openpyxl
import whois
import dns.resolver
import ssl
import requests
import OpenSSL.crypto
import subprocess
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


class DataProcessor:
    def __init__(self):
        self.data = None
        self.results = []

    def load_data_from_excel(self, file_path):
        try:
            # Code to read data from Excel file
            wb = openpyxl.load_workbook(file_path)
            # Assume the data is in the first sheet and the first column
            sheet = wb.active
            self.data = [cell.value for cell in sheet["A"]]
            wb.close()
        except Exception as e:
            raise ValueError("Failed to load data from Excel file. Error: " + str(e))

    def load_data_from_xml(self, file_path):
        try:
            # Code to read data from XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            self.data = [elem.text for elem in root.findall(".//data")]
        except Exception as e:
            raise ValueError("Failed to load data from XML file. Error: " + str(e))

    def load_data_from_text(self, file_path):
        try:
            # Code to read data from text file
            with open(file_path, "r") as file:
                self.data = file.read().splitlines()
        except Exception as e:
            raise ValueError("Failed to load data from Text file. Error: " + str(e))

    def load_data_from_terminal(self):
        # Code to read data from user input in the terminal
        print("Enter data (one entry per line, press 'enter' twice to continue):")
        self.data = []
        entry = input()
        while entry:
            self.data.append(entry)
            entry = input()

    def perform_functions(self, function_options):
        for option in function_options:
            if option.strip() == "a":
                # Perform whois lookup
                for domain in self.data:
                    result = self.perform_whois_lookup(domain)
                    self.results.append(result)
            elif option.strip() == "b":
                # Perform nslookup
                for domain in self.data:
                    result = self.perform_nslookup(domain)
                    self.results.append(result)
            elif option.strip() == "c":
                # Perform DNS lookup
                for domain in self.data:
                    result = self.perform_dns_lookup(domain)
                    self.results.append(result)
            elif option.strip() == "d":
                # Perform reverse DNS lookup
                for ip in self.data:
                    result = self.perform_reverse_dns_lookup(ip)
                    self.results.append(result)
            elif option.strip() == "e":
                # Perform SSL cert scan
                for domain in self.data:
                    result = self.perform_ssl_cert_lookup(domain)
                    self.results.append(result)
            elif option.strip() == "f":
                # Perform HTTP headers lookup
                for url in self.data:
                    result = self.perform_http_headers_lookup(url)
                    self.results.append(result)
            elif option.strip() == "g":
                # Perform subdomain lookup
                for domain in self.data:
                    result = self.perform_subdomain_lookup(domain)
                    self.results.append(result)

    def perform_whois_lookup(self, domain):
        try:
            w = whois.whois(domain)
            # Process the whois data and return the result
            result = f"Domain: {domain}\nRegistrar: {w.registrar}\nName Servers: {', '.join(w.name_servers)}"
        except Exception as e:
            result = f"Whois lookup failed for domain {domain}: {str(e)}"
        return result

    def perform_nslookup(self, domain):
        try:
            answers = dns.resolver.resolve(domain, "NS")
            name_servers = [str(rdata) for rdata in answers]
            result = f"Domain: {domain}\nName Servers: {', '.join(name_servers)}"
        except Exception as e:
            result = f"NSLookup failed for domain {domain}: {str(e)}"
        return result

    def perform_dns_lookup(self, domain):
        try:
            answers = dns.resolver.resolve(domain)
            records = [str(rdata) for rdata in answers]
            result = f"Domain: {domain}\nDNS Records: {', '.join(records)}"
        except Exception as e:
            result = f"DNS lookup failed for domain {domain}: {str(e)}"
        return result

    def perform_reverse_dns_lookup(self, ip):
        try:
            answers = dns.resolver.resolve(dns.reversename.from_address(ip), "PTR")
            hostnames = [str(rdata) for rdata in answers]
            result = f"IP Address: {ip}\nHostnames: {', '.join(hostnames)}"
        except Exception as e:
            result = f"Reverse DNS lookup failed for IP {ip}: {str(e)}"
        return result

    def perform_ssl_cert_lookup(self, url):
        try:
            cert = ssl.get_server_certificate((url, 443))
            x509 = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cert.encode("latin-1")
            )
            subject = x509.get_subject()
            ealtnames = []
            for i in range(x509.get_extension_count()):
                ext = x509.get_extension(i)
                if ext.get_short_name() == b'subjectAltName':
                    data = ext.get_data().decode(errors='ignore')
                    altnames = [name.strip() for name in data.split(',')]

            result = f"URL: {url}\n"
            result += f"Subject: {subject.commonName}\n"
            result += f"Altnames: {', '.join(altnames)}"

            # SSL Scan
            cmd = f"sslscan {url}"
            sslscan_output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            result += f"\n\nSSL Scan:\n{sslscan_output}"
        except Exception as e:
            result = f"SSL certificate lookup failed for URL {url}: {str(e)}"
        return result


    def perform_http_headers_lookup(self, url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        try:
            response = requests.head(url)
            headers = response.headers
            result = f"URL: {url}\nHTTP Headers:\n{headers}"
        except Exception as e:
            result = f"HTTP headers lookup failed for URL {url}: {str(e)}"
        return result

    def perform_subdomain_lookup(self, domain):
        # Add code to perform subdomain lookup
        pass

    def save_output_as_excel(self, file_path):
        try:
            # Code to save output as Excel file
            wb = openpyxl.Workbook()
            sheet = wb.active
            for i, result in enumerate(self.results):
                sheet.cell(row=i + 1, column=1, value=result)
            wb.save(file_path)
            wb.close()
        except Exception as e:
            raise ValueError("Failed to save output as Excel file. Error: " + str(e))

    def save_output_as_text(self, file_path):
        try:
            # Code to save output as text file
            with open(file_path, "w") as file:
                file.write("\n".join(self.results))
        except Exception as e:
            raise ValueError("Failed to save output as Text file. Error: " + str(e))

    def save_output_as_xml(self, file_path):
        try:
            # Code to save output as XML file
            root = ET.Element("results")
            for result in self.results:
                elem = ET.SubElement(root, "result")
                elem.text = result
            tree = ET.ElementTree(root)
            tree.write(file_path)
        except Exception as e:
            raise ValueError("Failed to save output as XML file. Error: " + str(e))

    def save_output_to_terminal(self):
        # Code to display output in the terminal
        for result in self.results:
            print(result)


def main():
    dp = DataProcessor()
    should_exit = False

    while True:
        print("\n1. Select how to input data:")
        print("   a. Excel")
        print("   b. XML")
        print("   c. Text")
        print("   d. Terminal")
        print("   e. Exit")
        input_option = input("Choose an option: ")

        if input_option == "a":
            Tk().withdraw()  # Hide the root window
            file_path = askopenfilename(
                title="Select Excel file"
            )  # Show file selection dialog
            dp.load_data_from_excel(file_path)
        elif input_option == "b":
            Tk().withdraw()
            file_path = askopenfilename(title="Select XML file")
            dp.load_data_from_xml(file_path)
        elif input_option == "c":
            Tk().withdraw()
            file_path = askopenfilename(title="Select text file")
            dp.load_data_from_text(file_path)
        elif input_option == "d":
            dp.load_data_from_terminal()
        elif input_option == "e":
            break  # Exit the loop and end the program
        else:
            print("Invalid option. Please choose a valid option.")
            continue

        while True:
            print("\n2. Select functions to perform:")
            print("   a. Whois lookup")
            print("   b. NSLookup")
            print("   c. DNS lookup")
            print("   d. Reverse DNS lookup")
            print("   e. SSL cert scan")
            print("   f. HTTP headers")
            print("   g. Subdomain lookup")
            print("   h. Back to Menu")
            function_options = input("Choose functions (comma-separated): ").split(",")

            if "h" in function_options:
                break  # Go back to the input option selection
            else:
                dp.perform_functions(function_options)

            if "h" in function_options:
                continue  # Go back to the input option selection

            print("\n3. Select how to output the results:")
            print("   a. Excel")
            print("   b. Text")
            print("   c. XML")
            print("   d. Terminal")
            print("   e. Back to Menu")
            output_option = input("Choose an option: ")

            if output_option == "a":
                Tk().withdraw()
                file_path = asksaveasfilename(title="Save Excel file")
                dp.save_output_as_excel(file_path)
            elif output_option == "b":
                Tk().withdraw()
                file_path = asksaveasfilename(title="Save Text file")
                dp.save_output_as_text(file_path)
            elif output_option == "c":
                Tk().withdraw()
                file_path = asksaveasfilename(title="Save XML file")
                dp.save_output_as_xml(file_path)
            elif output_option == "d":
                dp.save_output_to_terminal()
            elif output_option == "e":
                continue  # Go back to the input option selection
            else:
                print("Invalid option. Please choose a valid option.")


if __name__ == "__main__":
    main()
