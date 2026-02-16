import subprocess
import whois
import dns.resolver
import ssl
import OpenSSL.crypto
import requests
from datetime import datetime


def perform_whois_lookup(data):
    """
    Perform WHOIS lookup and return structured data.
    Returns a list of dictionaries for structured Excel output.
    """
    results = []
    for domain in data:
        result = {
            'domain': domain,
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'name_servers': None,
            'status': 'error',
            'error_message': None
        }
        
        try:
            w = whois.whois(domain)
            
            # Extract registrar
            if hasattr(w, 'registrar') and w.registrar:
                result['registrar'] = w.registrar if isinstance(w.registrar, str) else w.registrar[0]
            
            # Extract creation date
            if hasattr(w, 'creation_date') and w.creation_date:
                date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                result['creation_date'] = date.strftime('%Y-%m-%d') if date else None
            
            # Extract expiration date
            if hasattr(w, 'expiration_date') and w.expiration_date:
                date = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
                result['expiration_date'] = date.strftime('%Y-%m-%d') if date else None
            
            # Extract name servers
            if hasattr(w, 'name_servers') and w.name_servers:
                result['name_servers'] = ', '.join(w.name_servers)
            
            result['status'] = 'success'
            
        except Exception as e:
            result['error_message'] = str(e)
        
        results.append(result)
    
    return results


def perform_nslookup(data):
    """
    Perform NSLookup and return structured data.
    """
    results = []
    for domain in data:
        result = {
            'domain': domain,
            'name_servers': None,
            'status': 'error',
            'error_message': None
        }
        
        try:
            answers = dns.resolver.resolve(domain, "NS")
            name_servers = [str(rdata) for rdata in answers]
            result['name_servers'] = ', '.join(name_servers)
            result['status'] = 'success'
            
        except Exception as e:
            result['error_message'] = str(e)
        
        results.append(result)
    
    return results


def perform_dns_lookup(data):
    """
    Perform DNS lookup and return structured data.
    """
    results = []
    for domain in data:
        result = {
            'domain': domain,
            'dns_records': None,
            'status': 'error',
            'error_message': None
        }
        
        try:
            answers = dns.resolver.resolve(domain)
            records = [str(rdata) for rdata in answers]
            result['dns_records'] = ', '.join(records)
            result['status'] = 'success'
            
        except Exception as e:
            result['error_message'] = str(e)
        
        results.append(result)
    
    return results


def perform_reverse_dns_lookup(data):
    """
    Perform reverse DNS lookup and return structured data.
    """
    results = []
    for ip_address in data:
        result = {
            'ip_address': ip_address,
            'hostnames': None,
            'status': 'error',
            'error_message': None
        }
        
        try:
            answers = dns.resolver.resolve_address(ip_address)
            hostnames = [str(rdata) for rdata in answers]
            result['hostnames'] = ', '.join(hostnames)
            result['status'] = 'success'
            
        except Exception as e:
            result['error_message'] = str(e)
        
        results.append(result)
    
    return results


def perform_ssl_cert_lookup(data):
    """
    Perform SSL certificate lookup and return structured data.
    """
    results = []
    for domain in data:
        result = {
            'domain': domain,
            'expiration_date': None,
            'ssl_scan': None,
            'status': 'error',
            'error_message': None
        }
        
        try:
            cert = ssl.get_server_certificate((domain, 443))
            x509 = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cert
            )
            expiration_date = x509.get_notAfter().decode()
            result['expiration_date'] = expiration_date

            # Optional: Include SSL scan if sslscan is available
            try:
                cmd = f"sslscan {domain}"
                sslscan_output = subprocess.check_output(
                    cmd, shell=True, universal_newlines=True, timeout=30
                )
                result['ssl_scan'] = sslscan_output
            except:
                result['ssl_scan'] = 'SSL scan not available'
            
            result['status'] = 'success'
            
        except Exception as e:
            result['error_message'] = str(e)
        
        results.append(result)
    
    return results


def perform_http_headers_lookup(data):
    """
    Perform HTTP headers lookup and return structured data.
    """
    results = []
    for url in data:
        result = {
            'url': url,
            'headers': {},
            'status': 'error',
            'error_message': None
        }
        
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            response = requests.head(url, timeout=10)
            result['headers'] = dict(response.headers)
            result['url'] = url  # Update with normalized URL
            result['status'] = 'success'
            
        except Exception as e:
            result['error_message'] = str(e)
        
        results.append(result)
    
    return results


def format_results_for_text(results, lookup_type):
    """
    Format structured results as readable text for terminal/text file output.
    
    Args:
        results: List of dictionaries from lookup functions
        lookup_type: Type of lookup performed (whois, nslookup, etc.)
    
    Returns:
        List of formatted strings
    """
    formatted = []
    
    for result in results:
        if lookup_type == 'whois':
            if result['status'] == 'success':
                text = f"Domain: {result['domain']}\n"
                text += f"Registrar: {result['registrar']}\n"
                text += f"Creation Date: {result['creation_date']}\n"
                text += f"Expiration Date: {result['expiration_date']}\n"
                text += f"Name Servers: {result['name_servers']}"
            else:
                text = f"WHOIS lookup failed for domain {result['domain']}: {result['error_message']}"
        
        elif lookup_type == 'nslookup':
            if result['status'] == 'success':
                text = f"Domain: {result['domain']}\n"
                text += f"Name Servers: {result['name_servers']}"
            else:
                text = f"NSLookup failed for domain {result['domain']}: {result['error_message']}"
        
        elif lookup_type == 'dns':
            if result['status'] == 'success':
                text = f"Domain: {result['domain']}\n"
                text += f"DNS Records: {result['dns_records']}"
            else:
                text = f"DNS lookup failed for domain {result['domain']}: {result['error_message']}"
        
        elif lookup_type == 'reverse_dns':
            if result['status'] == 'success':
                text = f"IP Address: {result['ip_address']}\n"
                text += f"Hostnames: {result['hostnames']}"
            else:
                text = f"Reverse DNS lookup failed for IP address {result['ip_address']}: {result['error_message']}"
        
        elif lookup_type == 'ssl':
            if result['status'] == 'success':
                text = f"Domain: {result['domain']}\n"
                text += f"Expiration Date: {result['expiration_date']}\n"
                if result['ssl_scan'] and result['ssl_scan'] != 'SSL scan not available':
                    text += f"\nSSL Scan:\n{result['ssl_scan']}"
            else:
                text = f"SSL certificate lookup failed for domain {result['domain']}: {result['error_message']}"
        
        elif lookup_type == 'http_headers':
            if result['status'] == 'success':
                text = f"URL: {result['url']}\n"
                text += "Headers:\n"
                for header, value in result['headers'].items():
                    text += f"\t{header}: {value}\n"
                text = text.rstrip()  # Remove trailing newline
            else:
                text = f"HTTP headers lookup failed for URL {result['url']}: {result['error_message']}"
        
        else:
            text = str(result)
        
        formatted.append(text)
    
    return formatted


def print_output_to_terminal(data_processor):
    print("Output:")
    for item in data_processor.results:
        print(item)
