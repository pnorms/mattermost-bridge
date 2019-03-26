import json

# Get the config from json file
global settings
settings = json.load(open('config.json'))

# Assign the Flask info
global application_host, application_port, application_debug
application_host = settings["application"]["host"]
application_port = settings["application"]["port"]
application_debug = settings["application"]["debug"]

# Assign global colors
global error_color, alert_color, success_color
error_color = settings["colors"]["error"]
alert_color = settings["colors"]["alert"]
success_color = settings["colors"]["success"]

# Assign the MM info
global mattermost_url
mattermost_url = settings["mattermost"]["server_url"]