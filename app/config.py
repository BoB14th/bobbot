import os.path
import json
import os

if os.path.isfile('app/conf.json') is False:
    with open('app/conf.json', 'w') as newconf:
        conf = json.load(newconf)
        conf['dbpassword']  = os.environ['DB_PASSWORD']
        conf['log']  = os.environ['LOG_LVL']
        conf['apikey'] = os.environ['API_KEY']
        conf['vt_api_key'] = os.environ['VT_API_KEY']
        json.dump(conf, newconf, indent=4)

with open('app/conf.json', 'r') as mainconf:
    conf = json.load(mainconf)

VT_BASE_URL = "https://www.virustotal.com/api/v3"