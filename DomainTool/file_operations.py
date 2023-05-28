import openpyxl
import xml.etree.ElementTree as ET
from tkinter import filedialog
import tkinter as tk

def load_data_from_excel(file_path):
    if not file_path:
        print("No file selected. Exiting...")
        return False
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        data = []
        for row in sheet.iter_rows(values_only=True):
            data.append(row[0])
        print(f"Data loaded from Excel file: {file_path}")
        return data
    except Exception as e:
        raise ValueError(f"Failed to load data from Excel file. Error: {str(e)}")

def load_data_from_xml(file_path):
    if not file_path:
        print("No file selected. Exiting...")
        return False
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        data = [elem.text for elem in root.findall(".//domain")]
        print(f"Data loaded from XML file: {file_path}")
        return data
    except Exception as e:
        raise ValueError("Failed to load data from XML file. Error: " + str(e))

def load_data_from_text(file_path):
    try:
        with open(file_path, "r") as file:
            data = file.read().splitlines()
        return data
    except Exception as e:
        print(f"Failed to load data from Text file. Error: {str(e)}")
        return

def load_data_from_terminal(data_processor):
    print("Enter data (one entry per line, press 'enter' twice to continue):")
    data_processor.clear_data()  # Clear the data before loading new data
    entry = input()
    while entry:
        data_processor.data.append(entry)
        entry = input()

def save_output_as_excel(data_processor):
    try:
        results = data_processor.results
        wb = openpyxl.Workbook()
        sheet = wb.active

        for i, result in enumerate(results, start=1):
            # Replace illegal characters with a placeholder
            result = result.replace("\r", "").replace("\n", " ")
            try:
                sheet.cell(row=i, column=1, value=result)
            except openpyxl.utils.exceptions.IllegalCharacterError:
                # Handle the error by replacing illegal characters with an empty string
                sanitized_result = "".join(c for c in result if c.isprintable())
                sheet.cell(row=i, column=1, value=sanitized_result)

        file_path = get_file_path("xlsx", "save")
        if not file_path:
            print("File selection canceled. Returning to Main Menu.")
            return
        wb.save(file_path)
        wb.close()
        print(f"Output saved as Excel file: {file_path}")
    except Exception as e:
        print("Failed to save output as Excel file. Error: " + str(e))

def save_output_as_xml(results):
    try:
        root = ET.Element("root")
        for result in results:
            result_elem = ET.SubElement(root, "result")

            domain_elem = ET.SubElement(result_elem, "domain")
            domain_text = f"Domain: {result['Domain']}\n"
            domain_text += f"Registrar: {result['Registrar']}\n"
            domain_text += f"Name Servers: {', '.join(result['NameServers'])}"
            domain_elem.text = domain_text.strip()

            registrar_elem = ET.SubElement(result_elem, "registrar")
            registrar_elem.text = ""

            name_servers_elem = ET.SubElement(result_elem, "name_servers")

        tree = ET.ElementTree(root)
        file_path = get_file_path("xml", "save")
        if not file_path:
            print("File selection canceled. Returning to Main Menu.")
            return
        tree.write(file_path, encoding="UTF-8", xml_declaration=True)
        print(f"Output saved as XML file: {file_path}")
    except Exception as e:
        print(f"Failed to save output as XML file. Error: {str(e)}")


def save_output_as_text(results):
    try:
        file_path = get_file_path("txt", "save")
        if not file_path:
            print("File selection canceled. Returning to Main Menu.")
            return
        with open(file_path, "w") as file:
            for result in results:
                file.write(result + "\n\n")
        print(f"Output saved as Text file: {file_path}")
    except Exception as e:
        print(f"Failed to save output as Text file. Error: {str(e)}")


def get_file_path(file_type, action):
    root = tk.Tk()
    root.withdraw()

    if action == "load":
        file_path = filedialog.askopenfilename(filetypes=[(f"{file_type} files", f"*.{file_type.lower()}")])
        if not file_path:
            print("File selection canceled. Returning to Main Menu.")
            return None
    elif action == "save":
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{file_type.lower()}",
            filetypes=[(f"{file_type} files", f"*.{file_type.lower()}")]
        )
        if not file_path:
            print("No file selected. Returning to Main Menu.")
            return None
    else:
        print("Invalid action. Supported actions are 'load' and 'save'.")

    return file_path

def print_output_to_terminal(data_processor):
    print("Output:")
    for item in data_processor.results:
        print(item)