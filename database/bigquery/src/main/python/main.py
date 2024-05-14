import os
import sys
import requests
import json
from flask import jsonify
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

HTTP_SUCCESS = 200
HTTP_FAILURE = 400
CTSNBRTOKENGRP = "nbr"
CTSNBRTOKENTEMP = "nbr"
CTSCHARDIGITTOKENTEMP = "chardigits"
CTSCHARALPHATOKENTEMP = "charalpha"
CTSCHARALPHATOKENGRP = "char"
# The following are enviroment variables.

ctsuser = os.environ.get('CTSUSER', 'cts-user')
ctspwd =  os.environ.get('CTSPWD','yourpwd')
ctsip = os.environ.get('CTSIP', 'yourctsip')

p11debug = False
p11user = ctsuser + ":" + ctspwd
p11url = os.environ.get('CTSIP', 'yourctsip')
p11tokgroup = "tg1"
p11toktemplate = "tt1"
p11auth = None
rows = [1]
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
def tokenization(request):
    try:
        # The list of rows to return.
        return_value = []
        result = None
        payload = request.get_json()
        print("\npayload:", payload)
        user_defined_contexts = payload["userDefinedContext"]
        mode = None
        datatype = None
        rows = []
        for user_defined_context in user_defined_contexts:
           if user_defined_context == "mode":
            mode =  user_defined_contexts["mode"]
            #print(user_defined_contexts["mode"])
           elif user_defined_context == "datatype":
            datatype = user_defined_contexts["datatype"]
        if datatype == "chardigits":
            p11tokgroup = CTSCHARALPHATOKENGRP
            p11toktemplate = CTSCHARDIGITTOKENTEMP
        elif datatype == "charalpha":
            p11tokgroup = CTSCHARALPHATOKENGRP
            p11toktemplate = CTSCHARALPHATOKENTEMP
        elif datatype == "nbr":
            p11tokgroup = CTSNBRTOKENGRP
            p11toktemplate = CTSNBRTOKENTEMP

        rows = payload["calls"]
        u = None
        if mode == "tokenize": 
          u = p11url + "/rest/v2.0/tokenize"
        elif mode == "detokenize":
          u = p11url + "/rest/v2.0/detokenize"
        elif mode == "encrypt":
          u = p11url + "/vts/crypto/v1/encrypt"
        elif mode == "decrypt":
          u = p11url + "/vts/crypto/v1/decrypt" 
        googleuser = payload["sessionUser"]
        #print("\nuser making request:", googleuser)
        #Can have special logic to prevent dba from access.
        #print("nbr of rows", len(rows))
        # For each input row
        for row in rows:
            row_value = row[0]
            #print("\nrow value:", row_value)
            data = {"tokengroup" :  p11tokgroup, "tokentemplate" : p11toktemplate}
            ## Now only handling tokenize and detokenize
            if mode == "tokenize":
              data["data"] = row_value
            else:
              data["token"] = row_value
            # Post the request
            r = requests.post(u, headers=hdrs, auth=p11auth, verify=False, json=data)
            result = json.loads(r.text)
            if mode == "tokenize":
              if datatype == "nbr":
                #intvalue = int(result['token'])
                ##row_to_return = [intvalue]
                 row_to_return = result['token']
              else:
                row_to_return = result['token']
            else:
              if datatype == "nbr":
                ##intvalue = int(result['data'])
                ##row_to_return = [intvalue]
                 row_to_return = result['data']
              else:
                row_to_return = result['data']

            return_value.append(row_to_return)
 
        json_compatible_string_to_return = jsonify( { "replies" : return_value } )
        #print("\njson_compatible_string_to_return:", json_compatible_string_to_return)
        return (json_compatible_string_to_return, HTTP_SUCCESS)

    except:
        print("\nrows:", rows)
        return(rows, HTTP_FAILURE)

