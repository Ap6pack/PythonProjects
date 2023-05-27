import sys
import tkinter as tk
from tkinter import Tk, filedialog
import network_operations
import file_operations

def main_menu(dp):
    while True:
        print("\nPlease select an option:")
        print("1. Load data from Excel")
        print("2. Load data from XML")
        print("3. Load data from Text")
        print("4. Load data from Terminal")
        print("5. Exit")

        option = input("Enter option number: ")

        if option == "1":
            Tk().withdraw()  # Hide the root window
            file_path = filedialog.askopenfilename(
                title="Select Excel file",
                filetypes=[("Excel files", "*.xlsx"), ("All Files", "*.*")],
            )
            if file_path:
                if dp.load_data_from_excel(file_path):
                    dp.file_type = "Excel"
            else:
                print("No file selected.")
                continue
        elif option == "2":
            Tk().withdraw()
            file_path = filedialog.askopenfilename(
                title="Select XML file",
                filetypes=[("XML files", "*.xml"), ("All Files", "*.*")],
            )
            if file_path:
                if dp.load_data_from_xml(file_path):
                    dp.file_type = "XML"
            else:
                print("No file selected.")
                continue
        elif option == "3":
            Tk().withdraw()
            file_path = filedialog.askopenfilename(title="Select text file")
            dp.load_data_from_text(file_path)
        elif option == "4":
            file_operations.load_data_from_terminal(dp)
        elif option == "5":
            sys.exit()
        else:
            print("Invalid option. Please choose a valid option.")
            continue

        function_menu(dp)

def function_menu(dp):
    while True:
        print("\nPlease select an option:")
        print("1. Perform WHOIS lookup")
        print("2. Perform NSLookup")
        print("3. Perform DNS lookup")
        print("4. Perform reverse DNS lookup")
        print("5. Perform SSL certificate lookup")
        print("6. Perform HTTP headers lookup")
        print("7. Return to Main Menu")
        print("8. Exit")

        option = input("Enter option number(s) (comma-separated): ")
        options = option.split(",")

        if "7" in options:
            break
        elif "8" in options:
            sys.exit()

        valid_options = ["1", "2", "3", "4", "5", "6"]
        selected_options = []
        invalid_options = []

        for opt in options:
            opt = opt.strip()
            if opt in valid_options:
                selected_options.append(opt)
            else:
                invalid_options.append(opt)

        if invalid_options:
            print(f"Invalid option(s): {', '.join(invalid_options)}. Please choose a valid option.")
            continue

        for opt in options:
            if opt == "1":
                network_operations.perform_whois_lookup(dp)
            elif opt == "2":
                network_operations.perform_nslookup(dp)
            elif opt == "3":
                network_operations.perform_dns_lookup(dp)
            elif opt == "4":
                network_operations.perform_reverse_dns_lookup(dp)
            elif opt == "5":
                network_operations.perform_ssl_cert_lookup(dp)
            elif opt == "6":
                network_operations.perform_http_headers_lookup(dp)
            else:
                print(f"Invalid option '{opt}'. Please choose a valid option.")

        save_menu(dp)


def save_menu(dp):
    while True:
        print("\nPlease select an option:")
        print("1. Save output as Excel")
        print("2. Save output as XML")
        print("3. Save output as Text")
        print("4. Print output to Terminal")
        print("5. Return to Main Menu")
        print("6. Exit")

        option = input("Enter option number: ")

        if option == "1":
            file_operations.save_output_as_excel(dp)
        elif option == "2":
            file_operations.save_output_as_xml(dp)
        elif option == "3":
            file_operations.save_output_as_text(dp)
        elif option == "4":
            file_operations.print_output_to_terminal(dp)
        elif option == "5":
            main_menu(dp)
        elif option == "6":
            sys.exit()
        else:
            print("Invalid option. Please choose a valid option.")
            continue
