import requests
import config
import json

def send_webhook(app_name, hook_path, text_out, attachment_text, attachment_color):
    """
    Assembles incoming text, creates JSON object for the response, and
    sends it on to the Mattermost server and hook configured
    """
    # Get the user to use from config
    mattermost_user = config.settings["applications"][app_name]["username"]
    mattermost_icon = config.settings["applications"][app_name]["icon"]

    # Check if attachment needs to be sent
    if len(attachment_text) > 0:
        attach_dict = {
            "color": attachment_color,
            "text": attachment_text
        }
        data = {
            'text': text_out,
            'username': mattermost_user,
            'icon_url': mattermost_icon,
            "attachments": [attach_dict]
        }
    else:
        data = {
            'text': text_out,
            'username': mattermost_user,
            'icon_url': mattermost_icon,
        }

    # Send the webhook
    response = requests.post(
        config.mattermost_url + "hooks/" + hook_path,
        data = json.dumps(data),
        headers = {'Content-Type': 'application/json'}
    )

    # Return the POST result
    return response