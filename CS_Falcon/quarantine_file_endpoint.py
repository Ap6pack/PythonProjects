import falconpy

# Initialize the API client
client = falconpy.API()

# Define your plugin functionality
def quarantine_file(device_id, file_path):
    client.devices.put_quarantine_file(device_id=device_id, body={"file_path": file_path})
    pass

# Register your plugin with CrowdStrike Falcon
client.register_plugin("put_quarantine_file_name", put_quarantine_filen_function)
