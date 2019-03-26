import config
import common

def process_payload(app_name, hook_path, data):
    """
    Reads Ansible Tower JSON payload and converts it into Mattermost friendly
    message attachement format
    """
    
    # Setup vars
    text_out = ""
    attachment_text = ""
    attach_extra = ""
    color = config.success_color
    app_url = config.settings["applications"][app_name]["url"]

    # Check if a Job
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
            if status != "successful":
                color = config.error_color

        elif data["friendly_name"] == "Workflow Job":
            status = data["status"]
            name = data["name"]
            started = data["started"]
            created_by = data["created_by"]
            url = data["url"]
            # Assemble
            result = "[" + status + "](" + url + ")"
            attach_extra = "**name**: " + name + "\n" + \
                        "**started**: " + started + "\n" \
                        "**created_by**: " + created_by + "\n"
            if status != "successful":
                color = config.error_color

        else:
            result = "** UNKNOWN NOTIFICATION TYPE **: " + data["friendly_name"]

    # Try Others
    elif "body" in data:
        result = data["body"]

    # Unknown type, send raw
    else:
        result = "** UNKNOWN NOTIFICATION TYPE **: " + str(data)

    # Assemble the final attachment text to return and passit-repo
    # to the send_webhook function
    attachment_text = "**Result**: " + result

    ## Check if attachment, format properly
    if len(attach_extra) > 0:
        attachment_text += "\n" + attach_extra

    # Send to the WebHook meathod
    return common.send_webhook(app_name, hook_path, text_out, attachment_text, color)

def hook(app_name, hook_path, request):
    """
    Gets called from base.py call_hooks, this is what starts the process
    """

    if len(request.get_json()) > 0:
        data = request.get_json()
        response = process_payload(app_name, hook_path, data)
        
        # If Debugging show the payload
        if (config.application_debug):
            print(data)

    return ""