import subprocess
import whois
import dns.resolver
import ssl
import OpenSSL.crypto
import requests


def perform_whois_lookup(self):
    for domain in self.data:
        try:
            w = whois.whois(domain)
            result = f"Domain: {domain}\nRegistrar: {w.registrar}\nName Servers: {', '.join(w.name_servers)}"
        except Exception as e:
            result = f"Whois lookup failed for domain {domain}: {str(e)}"
        self.results.append(result)

def perform_nslookup(self):
    for domain in self.data:
        try:
            answers = dns.resolver.resolve(domain, "NS")
            name_servers = [str(rdata) for rdata in answers]
            result = f"Domain: {domain}\nName Servers: {', '.join(name_servers)}"
        except Exception as e:
            result = f"NSLookup failed for domain {domain}: {str(e)}"
        self.results.append(result)

def perform_dns_lookup(self):
    for domain in self.data:
        try:
            answers = dns.resolver.resolve(domain)
            records = [str(rdata) for rdata in answers]
            result = f"Domain: {domain}\nDNS Records: {', '.join(records)}"
        except Exception as e:
            result = f"DNS lookup failed for domain {domain}: {str(e)}"
        self.results.append(result)

def perform_reverse_dns_lookup(self):
    for ip_address in self.data:
        try:
            answers = dns.resolver.resolve_address(ip_address)
            hostnames = [str(rdata) for rdata in answers]
            result = f"IP Address: {ip_address}\nHostnames: {', '.join(hostnames)}"
        except Exception as e:
            result = (
                f"Reverse DNS lookup failed for IP address {ip_address}: {str(e)}"
            )
        self.results.append(result)

def perform_ssl_cert_lookup(self):
    for domain in self.data:
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
        self.results.append(result)

def perform_http_headers_lookup(self):
    for url in self.data:
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            response = requests.head(url)
            headers = response.headers
            result = f"URL: {url}\nHeaders:"
            
            for header, value in headers.items():
                result += f"\n\t{header}: {value}"

            self.results.append(result)
        except Exception as e:
            result = f"HTTP headers lookup failed for URL {url}: {str(e)}"
            self.results.append(result)

