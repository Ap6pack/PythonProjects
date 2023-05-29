import file_operations
import network_operations

class DataProcessor:
    def __init__(self):
        self.data = []
        self.file_type = ""
        self.results = []  # Add an empty list to store the results

    def load_data_from_excel(self, file_path):
        self.data = file_operations.load_data_from_excel(file_path)

    def load_data_from_xml(self, file_path):
        self.data = file_operations.load_data_from_xml(file_path)

    def load_data_from_text(self, file_path):
        self.data = file_operations.load_data_from_text(file_path)

    def load_data_from_terminal(self, file_path):
        self.data = file_operations.load_data_from_terminal(file_path)

    def save_output_to_excel(self, file_path):
        file_operations.save_output_as_excel(file_path, self.results)

    def save_output_to_xml(self, file_path):
        file_operations.save_output_as_xml(file_path, self.results)

    def save_output_to_terminal(self, file_path):
        file_operations.save_output_as_text(file_path, self.results)

    def perform_whois_lookup(self):
        self.results = network_operations.perform_whois_lookup(self.data)

    def perform_nslookup(self):
        self.results = network_operations.perform_nslookup(self.data)

    def perform_dns_lookup(self):
        self.results = network_operations.perform_dns_lookup(self.data)

    def perform_reverse_dns_lookup(self):
        self.results = network_operations.perform_reverse_dns_lookup(self.data)

    def perform_ssl_cert_lookup(self):
        self.results = network_operations.perform_ssl_cert_lookup(self.data)

    def perform_http_headers_lookup(self):
        self.results = network_operations.perform_http_headers_lookup(self.data)
    
    def clear_data(self):
        self.data = []  # Clear the data by assigning an empty list
