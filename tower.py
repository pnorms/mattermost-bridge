from flask import Flask
from flask import request
import json
import requests

def readConfig():
    """
    Reads config.json to get configuration settings
    """
    d = json.load(open('config.json'))

    global application_host, application_port, application_debug
    application_host = d["application"]["host"]
    application_port = d["application"]["port"]
    application_debug = d["application"]["debug"]

    global error_color, alert_color, success_color
    error_color = d["colors"]["error"]
    alert_color = d["colors"]["alert"]
    success_color = d["colors"]["success"]

    global mattermost_url, mattermost_user, mattermost_icon
    mattermost_url = d["mattermost"]["server_url"]
    mattermost_user = d["mattermost"]["post_user_name"]
    mattermost_icon = d["mattermost"]["post_user_icon"]

    global tower_url
    tower_url = d["tower"]["server_url"]

def process_payload(hook_path, data):
    """
    Reads Ansible Tower JSON payload and converts it into Mattermost friendly
    message attachement format
    """

    text_out = ""
    attachment_text = ""
    attach_extra = ""

    # Jobs
    if "friendly_name" in data:
        if data["friendly_name"] == "Job":
            status = data["status"]
            name = data["name"]
            project = data["project"]
            playbook = data["playbook"]
            inventory = data["inventory"]
            started = data["started"]
            credential = data["credential"]
            created_by = data["created_by"]
            url = data["url"]
            # Assemble
            result = "[" + status + "](" + url + ")"
            attach_extra = "**name**: " + name + "\n" + \
                           "**project**: " + project + "\n" \
                           "**playbook**: " + playbook + "\n" \
                           "**inventory**: " + inventory + "\n" \
                           "**started**: " + started + "\n" \
                           "**credential**: " + credential + "\n" \
                           "**created_by**: " + created_by + "\n"
        else:
            result = "** UNKNOWN NOTIFICATION TYPE **: " + data["friendly_name"]

    # Try Others
    elif "body" in data:
        result = data["body"]

    # Try Others
    else:
        result = "** UNKNOWN NOTIFICATION TYPE **: " + str(data)

    # Assemble the final attachment text to return and passit-repo
    # to the send_webhook function
    attachment_text = "**Result**: " + result

    if len(attach_extra) > 0:
        attachment_text += "\n" + attach_extra

    return send_webhook(hook_path, text_out, attachment_text, success_color)


def send_webhook(hook_path, text_out, attachment_text, attachment_color):
    """
    Assembles incoming text, creates JSON object for the response, and
    sends it on to the Mattermost server and hook configured
    """
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

    response = requests.post(
        mattermost_url + "hooks/" + hook_path,
        data = json.dumps(data),
        headers = {'Content-Type': 'application/json'}
    )
    return response


"""
------------------------------------------------------------------------------------------
Flask application below
"""
readConfig()

app = Flask(__name__)

@app.route( '/hooks/<hook_path>', methods = [ 'POST' ] )
def hooks(hook_path):
    if len(request.get_json()) > 0:
        data = request.get_json()
        response = process_payload(hook_path, data)

    return ""

if __name__ == '__main__':
   app.run(host = application_host, port = application_port,
           debug = application_debug)
