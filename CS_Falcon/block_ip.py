import falconpy

# Initialize the API client
client = falconpy.API()

# Define your plugin functionality
def block_ip(ip_address):
    client.iocs.put_iocs_v2(body={"indicators": [{"type": "ipv4", "value": ip_address}], "action": "add", "applied_globally": True})
    pass

# Register your plugin with CrowdStrike Falcon
client.register_plugin(" block_ip_name",  block_ip_function)
