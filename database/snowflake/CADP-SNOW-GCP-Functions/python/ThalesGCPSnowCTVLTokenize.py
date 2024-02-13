# This sample GCP Function is used to implement a Snowflake Database User Defined Function(UDF).  It uses CT-VL
# to protect sensitive data in a column.  This example will tokenize the data.
#  
#  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
#  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
#  Was tested with CM 2.11 & CT-VL 2.6 or higher.
#  For more information on Snowflake External Functions see link below. 
# https://docs.snowflake.com/en/sql-reference/external-functions-creating-gcp
# 
# @author  mwarner
# 
#


import sys
import requests
import json
import os
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)


HTTP_SUCCESS = 200
HTTP_FAILURE = 400
# Declare the variable

p11ptext = None
p11auth = None

p11debug = True
p11user = os.environ.get('P11USER')
p11url = os.environ.get('P11URL')
p11tokgroup = "tg1"
p11toktemplate = "tt1"
p11ptext = "thisistestdata"
# Loop through the option, set value to variable

p11url = "https://" + p11url + "/vts"
# Check username and password if exist in system environment or not

# split the p11user variable to check username/password missing
p11auth = tuple(p11user.split(":", 1))

errs = 0

# Set the header application
hdrs = {'Content-Type': 'application/json'}
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

############ Check connect to VTS before continue #######################
try:
    r = requests.get(p11url, verify=False)
    r.raise_for_status()
except requests.exceptions.RequestException as err:
    print("\nEror, something wrong: ")
    print(err)
    sys.exit(200)
except requests.exceptions.HTTPError as errh:
    print("\nHttp Error:", errh)
    sys.exit(200)
except requests.exceptions.ConnectionError as errc:
    print("\nError Connecting:", errc)
    sys.exit(200)
except requests.exceptions.Timeout as errt:
    print("\nTimeout Error:", errt)
    sys.exit(200)

################################################################################

def thales_cts_tokenize(request):

    try:
        # The list of rows to return.
        return_value = []
        result = None
        payload = request.get_json()

        rows = payload["data"]
        u = p11url + "/rest/v2.0/tokenize"
        # For each input row
        for row in rows:
            # Include the row number.
            row_number = row[0]
            row_value = row[1]
            data = {"tokengroup" :  p11tokgroup, "tokentemplate" : p11toktemplate}
            data["data"] = row_value
            # Post the request
            r = requests.post(u, headers=hdrs, auth=p11auth, verify=False, json=data)
            result = json.loads(r.text)
            row_to_return = [row_number, result['token']]
            return_value.append(row_to_return)
        json_compatible_string_to_return = json.dumps( { "data" : return_value } )
        return (json_compatible_string_to_return, HTTP_SUCCESS)

    except:

        return(request.data, HTTP_FAILURE)