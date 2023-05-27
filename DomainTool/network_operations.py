import subprocess
import whois
import dns.resolver
import ssl
import OpenSSL.crypto
import requests


def perform_whois_lookup(data):
    results = []
    for domain in data:
        try:
            w = whois.whois(domain)
            result = f"Domain: {domain}\nRegistrar: {w.registrar}\nName Servers: {', '.join(w.name_servers)}"
        except Exception as e:
            result = f"Whois lookup failed for domain {domain}: {str(e)}"
        results.append(result)
    return results

def perform_nslookup(data):
    results = []
    for domain in data:
        try:
            answers = dns.resolver.resolve(domain, "NS")
            name_servers = [str(rdata) for rdata in answers]
            result = f"Domain: {domain}\nName Servers: {', '.join(name_servers)}"
        except Exception as e:
            result = f"NSLookup failed for domain {domain}: {str(e)}"
        results.append(result)
    return results

def perform_dns_lookup(data):
    results = []
    for domain in data:
        try:
            answers = dns.resolver.resolve(domain)
            records = [str(rdata) for rdata in answers]
            result = f"Domain: {domain}\nDNS Records: {', '.join(records)}"
        except Exception as e:
            result = f"DNS lookup failed for domain {domain}: {str(e)}"
        results.append(result)
    return results

def perform_reverse_dns_lookup(data):
    results = []
    for ip_address in data:
        try:
            answers = dns.resolver.resolve_address(ip_address)
            hostnames = [str(rdata) for rdata in answers]
            result = f"IP Address: {ip_address}\nHostnames: {', '.join(hostnames)}"
        except Exception as e:
            result = f"Reverse DNS lookup failed for IP address {ip_address}: {str(e)}"
        results.append(result)
    return results

def perform_ssl_cert_lookup(data):
    results = []
    for domain in data:
        try:
            cert = ssl.get_server_certificate((domain, 443))
            x509 = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cert
            )
            expiration_date = x509.get_notAfter().decode()
            result = f"Domain: {domain}\nExpiration Date: {expiration_date}"

            cmd = f"sslscan {domain}"
            sslscan_output = subprocess.check_output(
                cmd, shell=True, universal_newlines=True
            )
            result += f"\n\nSSL Scan:\n{sslscan_output}"
        except Exception as e:
            result = f"SSL certificate lookup failed for domain {domain}: {str(e)}"
        results.append(result)
    return results

def perform_http_headers_lookup(data):
    results = []
    for url in data:
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            response = requests.head(url)
            headers = response.headers
            result = f"URL: {url}\nHeaders:"
            
            for header, value in headers.items():
                result += f"\n\t{header}: {value}"

            results.append(result)
        except Exception as e:
            result = f"HTTP headers lookup failed for URL {url}: {str(e)}"
            results.append(result)
    return results

def print_output_to_terminal(data_processor):
    print("Output:")
    for item in data_processor.results:
        print(item)