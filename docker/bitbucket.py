import config
import common
import helpers

def get_event_type(event_key):
    """
    Converts event to friendly output
    """
    try:
        event_out = helpers.bitbucket_events.get(event_key)
    except ValueError:
        event_out = event_key
    
    return event_out


def process_payload(app_name, hook_path, data):
    """
    Reads Bitbucket JSON payload and converts it into Mattermost friendly
    message attachement format
    """
    text_out = ""
    attachment_text = ""
    app_url = config.settings["applications"][app_name]["url"]

    event = get_event_type(data["eventKey"])
    actor = "[" + data["actor"]["name"] + \
            " (" + data["actor"]["emailAddress"] + ")](" + app_url + \
            "users/" + data["actor"]["name"] + ")"

    attach_extra = ""
    # Pull Requests and Pull Request Comments
    if data["eventKey"].startswith('pr:'):
        pr_id = str(data["pullRequest"]["id"])
        pr_title = data["pullRequest"]["title"]
        repo_name = data["pullRequest"]["toRef"]["repository"]["name"]
        proj_key = data["pullRequest"]["toRef"]["repository"]["project"]["key"]
        url = app_url + "projects/" + proj_key + "/repos/" + \
            repo_name + "/pull-requests/" + pr_id

        if data["eventKey"].startswith("pr:comment:"):
            attach_extra = "**Comment**: [" + data["comment"]["text"] + \
                        "](" + url + ")"
        else:
            attach_extra = "[" + pr_id + " : " + pr_title + "](" + url + ")"

    # Commits - Push (Add, Update), Comment, etc.
    if data["eventKey"].startswith('repo:'):
        repo_name = data["repository"]["name"]
        proj_key = data["repository"]["project"]["key"]
        url = app_url + "projects/" + proj_key + "/repos/" + \
            repo_name

        # Comment added, updated, deleted
        if data["eventKey"].startswith("repo:comment:"):
            url += "/commits/" +  data["commit"]
            attach_extra = "**Comment**: [" + data["comment"]["text"] + \
                        "](" + url + ")"

        if data["eventKey"] == "repo:refs_changed":
            specific_event = "**Action**: " + data["changes"][0]["type"] + \
                            " - " + data["changes"][0]["ref"]["displayId"] + \
                            " (" + data["changes"][0]["ref"]["type"] + ")"
            url += "/commits/" +  data["changes"][0]["toHash"]
            attach_extra = specific_event + "\n[Commit: " + \
                        data["changes"][0]["toHash"] + "](" + url + ")"

    # Always add comments
    if "comment" in data:
        attach_extra += "**Comments**: [" + data["comment"]["text"] + "](" + url + ")"


    # Assemble the final attachment text to return and pass
    # to the send_webhook function
    attachment_text = "**" + event + "**\n**Author**: " + actor
    if len(repo_name) > 1:
        attachment_text = "**Repository**: " + repo_name + "\n" + \
                        attachment_text
    if len(attach_extra) > 0:
        attachment_text += "\n" + attach_extra

    return common.send_webhook(app_name, hook_path, text_out, attachment_text, config.success_color)

def hook(app_name, hook_path, request):
    """
    Gets called from base.py call_hooks, this is what starts the process
    """
    # Get BitBuck specific vars from the request
    request_id = request.headers.get('X-Request-Id')
    event = request.headers.get('X-Event-Key')

    # If ping there is no JSON to parse, just handle it here otherwise process the payload
    if event == "diagnostics:ping":
        response = common.send_webhook(app_name, hook_path, "diagnostics:ping", 
                                "Bitbucket is testing the connection " + \
                                "to Mattermost: " + request_id, 
                                config.alert_color)
    else:
        if len(request.get_json()) > 0:
            data = request.get_json()
            response = process_payload(app_name, hook_path, data)

            # If Debugging show the payload
            if (config.application_debug):
                print(data)
    return ""