import file_operations
import network_operations

class DataProcessor:
    def __init__(self):
        self.data = []
        self.file_type = ""
        self.results = []  # Store the results
        self.current_lookup_type = None  # Track what type of lookup was performed

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
        print(f"Processing {len(self.data)} domains for WHOIS lookup...")
        self.results = network_operations.perform_whois_lookup(self.data)
        self.current_lookup_type = 'whois'
        print(f"✓ Completed WHOIS lookup for {len(self.results)} domains")

    def perform_nslookup(self):
        print(f"Processing {len(self.data)} domains for NSLookup...")
        self.results = network_operations.perform_nslookup(self.data)
        self.current_lookup_type = 'nslookup'
        print(f"✓ Completed NSLookup for {len(self.results)} domains")

    def perform_dns_lookup(self):
        print(f"Processing {len(self.data)} domains for DNS lookup...")
        self.results = network_operations.perform_dns_lookup(self.data)
        self.current_lookup_type = 'dns'
        print(f"✓ Completed DNS lookup for {len(self.results)} domains")

    def perform_reverse_dns_lookup(self):
        print(f"Processing {len(self.data)} IP addresses for reverse DNS lookup...")
        self.results = network_operations.perform_reverse_dns_lookup(self.data)
        self.current_lookup_type = 'reverse_dns'
        print(f"✓ Completed reverse DNS lookup for {len(self.results)} IP addresses")

    def perform_ssl_cert_lookup(self):
        print(f"Processing {len(self.data)} domains for SSL certificate lookup...")
        self.results = network_operations.perform_ssl_cert_lookup(self.data)
        self.current_lookup_type = 'ssl'
        print(f"✓ Completed SSL certificate lookup for {len(self.results)} domains")

    def perform_http_headers_lookup(self):
        print(f"Processing {len(self.data)} URLs for HTTP headers lookup...")
        self.results = network_operations.perform_http_headers_lookup(self.data)
        self.current_lookup_type = 'http_headers'
        print(f"✓ Completed HTTP headers lookup for {len(self.results)} URLs")
    
    def clear_data(self):
        self.data = []  # Clear the data by assigning an empty list
