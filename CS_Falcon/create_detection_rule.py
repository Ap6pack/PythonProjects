import falconpy

# Initialize the API client
client = falconpy.API()

# Define your plugin functionality
def create_detection_rule(name, description, platform, criteria):
    body = {
        "name": name,
        "description": description,
        "platform_name": platform,
        "criteria": criteria,
        "action": {"type": "detect"}
    }
    client.detections.create_custom_detection_rule(body=body)
    pass

# Register your plugin with CrowdStrike Falcon
client.register_plugin("create_detection_rule_name", create_detection_rule_function)
