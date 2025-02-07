import os
import sys
import requests
import json
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

HTTP_SUCCESS = 200
HTTP_FAILURE = 400
CTSNBRTOKENGRP = "nbr"
CTSNBRTOKENTEMP = "nbr"
CTSCHARDIGITTOKENTEMP = "chardigit"
CTSCHARALPHATOKENTEMP = "charalpha"
CTSCHARALPHATOKENGRP = "char"
# The following are enviroment variables.

ctsuser = os.environ.get('CTSUSER', 'cts-user')
ctspwd =  os.environ.get('CTSPWD','Yourpwd')
ctsip = os.environ.get('CTSIP', 'YourCTSIP')

p11debug = False
p11user = ctsuser + ":" + ctspwd
p11url = os.environ.get('CTSIP', 'YourCTSIP')
p11tokgroup = CTSCHARALPHATOKENGRP
p11toktemplate = CTSCHARALPHATOKENTEMP
p11auth = None

p11url = "https://" + p11url + "/vts"
# split the p11user variable to check username/password missing
p11auth = tuple(p11user.split(":", 1))

errs = 0

# Set the header application
hdrs = {'Content-Type': 'application/json'}

############ Check connect to VTS before continue #######################
try:
    r = requests.get(p11url, verify=False)
    r.raise_for_status()
except requests.exceptions.RequestException as err:
    print("\nEror, something wrong: ")
    print(err)
    sys.exit(HTTP_FAILURE)
except requests.exceptions.HTTPError as errh:
    print("\nHttp Error:", errh)
    sys.exit(HTTP_FAILURE)
except requests.exceptions.ConnectionError as errc:
    print("\nError Connecting:", errc)
    sys.exit(HTTP_FAILURE)
except requests.exceptions.Timeout as errt:
    print("\nTimeout Error:", errt)
    sys.exit(HTTP_FAILURE)

################################################################################

def lambda_handler(event, context):
    ret = dict()
    res = []

    try:
        # The list of rows to return.

        result = None

        rows = event["arguments"]
        print("number of rows")
        print(len(rows))
        u = p11url + "/rest/v2.0/tokenize"
        # For each input row
        for row in rows:
            # Include the row number.
            #row_number = row[0]
            row_value = row[0]
            #print(row_value)
            data = {"tokengroup" :  p11tokgroup, "tokentemplate" : p11toktemplate}
            data["data"] = row_value
            # Post the request
            r = requests.post(u, headers=hdrs, auth=p11auth, verify=False, json=data)
            result = json.loads(r.text)
            encvalue = result['token']
            res.append(encvalue)
        ret['success'] = True
        ret["num_records"] = len(rows)
        ret['results'] = res       
        #json_compatible_string_to_return = json.dumps( return_value )
        return json.dumps(ret)

    except:
        ret['success'] = False
        ret["error_msg"] = "my function isn't working"
        ret["num_records"] = len(rows)
        ret['results'] = event["arguments"] 
        return json.dumps(ret)