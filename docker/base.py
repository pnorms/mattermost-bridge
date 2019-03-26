from flask import Flask
from flask import request
import json
import requests
import helpers
import config

def getApplications():    
    """
    Gets the applications and their imports from configuration settings
    """
    for app in config.settings["applications"]:
        c_script = (config.settings["applications"][app]["include_script"])
        c_shortname = c_script[:-3]
        globals()[c_shortname] = __import__(c_shortname, locals(), globals())

# Do the imports on applications
getApplications()

# Setup Flask app and it's paths
app = Flask(__name__)

@app.route( '/', methods = [ 'GET' ] )
def health():
    return "listening"

@app.route( '/<app_name>/<hook_path>', methods = [ 'POST' ] )
def call_hooks(app_name,hook_path):
    """
    Wrapper to call the appropriate include hook function
    """
    c_hook = getattr(globals()[app_name], 'hook')
    return c_hook(app_name, hook_path, request)

# Start listening
if __name__ == '__main__':
   app.run(host = config.application_host, port = config.application_port, debug = config.application_debug)