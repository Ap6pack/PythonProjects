import openpyxl
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import FALSE, Tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename, asksaveasfilename

def load_data_from_excel(self, file_path):
    if not file_path:
        print("No file selected. Exiting...")
        return FALSE
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        self.data = []
        for row in sheet.iter_rows(values_only=True):
            self.data.append(row[0])
        print(f"Data loaded from Excel file: {file_path}")
        return True
    except Exception as e:
        raise ValueError(f"Failed to load data from Excel file. Error: {str(e)}")

def load_data_from_xml(self, file_path):
    if not file_path:
        print("No file selected. Exiting...")
        return False
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        self.data = [elem.text for elem in root.findall(".//domain")]
        print(f"Data loaded from XML file: {file_path}")
        return True
    except Exception as e:
        raise ValueError("Failed to load data from XML file. Error: " + str(e))

def load_data_from_text(self, file_path):
    try:
        with open(file_path, "r") as file:
            self.data = file.read().splitlines()
    except Exception as e:
        raise ValueError("Failed to load data from Text file. Error: " + str(e))

def load_data_from_terminal(self):
    print("Enter data (one entry per line, press 'enter' twice to continue):")
    self.data = []
    entry = input()
    while entry:
        self.data.append(entry)
        entry = input()

def save_output_as_excel(self):
    try:
        wb = openpyxl.Workbook()
        sheet = wb.active

        for i, result in enumerate(self.results, start=1):
            # Replace illegal characters with a placeholder
            result = result.replace("\r", "").replace("\n", " ")
            try:
                sheet.cell(row=i, column=1, value=result)
            except openpyxl.utils.exceptions.IllegalCharacterError:
                # Handle the error by replacing illegal characters with an empty string
                sanitized_result = "".join(c for c in result if c.isprintable())
                sheet.cell(row=i, column=1, value=sanitized_result)

        file_path = self.get_save_file_path("xlsx")
        wb.save(file_path)
        wb.close()
        print(f"Output saved as Excel file: {file_path}")
    except Exception as e:
        raise ValueError("Failed to save output as Excel file. Error: " + str(e))

def save_output_as_xml(self):
    try:
        root = ET.Element("root")
        for result in self.results:
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
        file_path = self.get_save_file_path("xml")
        tree.write(file_path, encoding="UTF-8", xml_declaration=True)
        print(f"Output saved as XML file: {file_path}")
    except Exception as e:
        raise ValueError("Failed to save output as XML file. Error: " + str(e))

def save_output_as_text(self):
    try:
        file_path = self.get_save_file_path("txt")
        with open(file_path, "w") as file:
            for result in self.results:
                file.write(result + "\n\n")
        print(f"Output saved as Text file: {file_path}")
    except Exception as e:
        raise ValueError("Failed to save output as Text file. Error: " + str(e))



def get_save_file_path(self, file_type):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=f".{file_type.lower()}",
        filetypes=[(f"{file_type} files", f"*.{file_type.lower()}")],
    )
    return file_path

def print_output_to_terminal(self):
    print("Output:")
    for item in self.results:
        print(item)

