import file_operations
import network_operations
import dns.resolver
import openpyxl
import OpenSSL.crypto
import requests
import ssl
import whois
import xml.etree.ElementTree as ET
from tkinter import filedialog
import menu_logic
import file_operations
import network_operations


class DataProcessor:
    def __init__(self):
        self.data = []
        self.results = []
        self.file_type = None

    def perform_functions(self, function_options):
        self.results = []  # Clear the results list
        function_options = function_options.strip().split()
        for option in function_options:
            option = option.strip()
            if option == "a":
                network_operations.perform_whois_lookup()
            elif option == "b":
                network_operations.perform_nslookup()
            elif option == "c":
                network_operations.perform_dns_lookup()
            elif option == "d":
                network_operations.perform_reverse_dns_lookup()
            elif option == "e":
                network_operations.perform_ssl_cert_lookup()
            elif option == "f":
                network_operations.perform_http_headers_lookup()
            elif option == "g":
                main(self)  # Call the show_menu() function from menu_logic.py
            elif option == "h":
                file_operations.save_output_as_excel(self.results)
            elif option == "i":
                file_operations.save_output_as_xml(self.results)
            elif option == "j":
                file_operations.save_output_as_text(self.results)
            elif option == "k":
                file_operations.print_output_to_terminal()
            elif option == "l":
                return  # Exit the function
            else:
                print(f"Invalid option: {option}")

        def load_data_from_excel(self, file_path):
            file_operations.load_data_from_excel(file_path)

        def load_data_from_xml(self, file_path):
            file_operations.load_data_from_xml(file_path)

        def load_data_from_text(self, file_path):
            file_operations.load_data_from_text(file_path)

        def load_data_from_terminal(self):
            file_operations.load_data_from_terminal

        def print_output_to_excel(self):
            file_operations.print_output_to_excel(self.results)

        def print_output_to_xml(self):
            file_operations.print_output_to_xml(self.results)

        def print_output_to_terminal(self):
            file_operations.print_output_to_text(self.results)

        def perform_whois_lookup(self):
            network_operations.perform_whois_lookup(self.data)

        def perform_nslookup(self):
            network_operations.perform_nslookup(self.data)

        def perform_dns_lookup(self):
            network_operations.perform_dns_lookup(self.data)

        def perform_reverse_dns_lookup(self):
            network_operations.perform_reverse_dns_lookup(self.data)

        def perform_ssl_cert_lookup(self):
            network_operations.perform_ssl_cert_lookup(self.data)

        def perform_http_headers_lookup(self):
            network_operations.perform_http_headers_lookup(self.data)

def main():
    print("Data Processor")
    print("-" * 40)
    data_processor = DataProcessor()
    while True:
        print("Select data source:")
        print("1. Excel file")
        print("2. XML file")
        print("3. Text file")
        print("4. Enter data in the terminal")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            file_path = file_operations.get_file_path("Excel Files", "*.xlsx")
            data_processor.load_data_from_excel(file_path)
        elif choice == "2":
            file_path = file_operations.get_file_path("XML Files", "*.xml")
            data_processor.load_data_from_xml(file_path)
        elif choice == "3":
            file_path = file_operations.get_file_path("Text Files", "*.txt")
            data_processor.load_data_from_text(file_path)
        elif choice == "4":
            data_processor.load_data_from_terminal()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")
    main(data_processor)

if __name__ == "__main__":
    main()
