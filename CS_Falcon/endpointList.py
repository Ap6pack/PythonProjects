import falconpy

# Initialize the API client
client = falconpy.API()

# Define your plugin functionality
def get_endpoints():
    endpoints = client.devices.get_devices()
    for endpoint in endpoints['resources']:
        print(f"Endpoint name: {endpoint['hostname']}, status: {endpoint['status']}")

        # Register your plugin with CrowdStrike Falcon
client.register_plugin("get_endpoints_name", get_endpoints_function)
