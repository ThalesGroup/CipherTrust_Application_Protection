#!/usr/bin/python
#################################################################################
#                                                                               #
# Deokenize a given token using the token group and token template specified.   #
# The token group and token template must already accessible to the server and  #
# operational. If the operation succeeds the plain text is returned or, if a    #
# failure occurred, an error will be returned.                                  #
#                                                                               #
# Thales E-security Copyright (c) 2020                                          #
#################################################################################
import os
import sys
import requests
import json
import base64
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

############ Help function ##############################


def usage(msg=None):
    if msg:
        print(msg)
    print("Usage:")
    print("\t" + sys.argv[0] + "  [-h] | [-d] [-u user:pwd] [-l url] [-p <ptext>] [-I <infile>] [-O <outfile] [-tg <tokengroup>] [-tt <tokentemplate>] ")
    print("\n\t-u\t\tUsername:Password access VTS.")
    print("\t-l\t\tURL of VTS")
    print("\t-p\t\tThe token to be detokenize.")
    print("\t-I\t\tToken file name to be detokenize.")
    print("\t-O\t\tOutput file name.")
    print("\t-tg\t\tToken group")
    print("\t-tt\t\tToken template")
    print("\t-d\t\tTurn on debug, print output information in json format.")
    print("\t-h\t\tHelp usage.")
    sys.exit(250)


# Declare the variable
p11debug = False
p11url = None
p11user = None
p11input = None
p11output = None
p11tokgroup = None
p11toktemplate = None
p11token = None
p11auth = None

args = sys.argv[1:]

# Check the switch entries from command line
if (len(args) == 0):
    usage()

# Loop through the option, set value to variable
while len(args) > 0:
    if args[0] == "-d":  # Check if debug on
        p11debug = True
        args = args[1:]
    elif args[0] == "-u":  # check if option user/password define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing username and password.\n")
        p11user = args[1]
        args = args[2:]
    elif args[0] == "-l":  # check if option URL define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing VTS url.\n")
        p11url = args[1]
        args = args[2:]
    elif args[0] == "-tg":  # check if option tokengroup define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing tokengroup.\n")
        p11tokgroup = args[1]
        args = args[2:]
    elif args[0] == "-tt":  # check if option tokentemplate define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing tokentemplate.\n")
        p11toktemplate = args[1]
        args = args[2:]
    elif args[0] == "-I":  # check if option input filename define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing input file.\n")
        p11input = args[1]
        args = args[2:]
    elif args[0] == "-O":  # check if option output filename define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing output file.\n")
        p11output = args[1]
        args = args[2:]
    elif args[0] == "-p":  # check if option plaintext define
        if ((len(args) == 1) or (args[1].startswith("-"))):
            usage("\nMissing plaintext.\n")
        p11token = args[1]
        args = args[2:]
    elif args[0] == "-h":
        usage()
    elif args[0].startswith("-"):  # check if invalide option define
        usage("\nInvalid option: " + args[0])
    else:
        break

# Check URL if exist in system environment or not
if (("P11_URL" in os.environ) and (p11url == None)):
    p11url = os.environ["P11_URL"]
elif (p11url == None):
    usage("\nURL not define or missing P11_URL environment variable: https://<vts-server/vts.\n")
p11url = "https://" + p11url + "/vts"
# Check username and password if exist in system environment or not
if (("P11_UNAME_PWD" in os.environ) and (p11user == None)):
    p11user = os.environ["P11_UNAME_PWD"]
elif (p11user == None):
    usage("\nUser and password not define or missing P11_USER environment variable: assuming no user login.\n")

# split the p11user variable to check username/password missing
p11auth = tuple(p11user.split(":", 1))
if not len(p11auth) == 2:
    usage("\nUsername missing password.\n")
if ((p11auth[0] == "") or (p11auth[1] == "")):
    usage("\nMissing username or password.\n")

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
    print(err)
    sys.exit(200)
except requests.exceptions.ConnectionError as errc:
    print("\nError Connecting:", errc)
    print(err)
    sys.exit(200)
except requests.exceptions.Timeout as errt:
    print("\nTimeout Error:", errt)
    print(err)
    sys.exit(200)

################################################################################

result = None

# Check to see if -p and -I option call together
if p11token and p11input:
    usage("\n-p and -I can not be called together.\n")

# Check if need to open input file for read data
if not p11token:
    if not p11input:
        p11input = "-"
    if p11input == "-":
        p11token = sys.stdin.read()
    else:
        st = os.stat(p11input)
        ifd = open(p11input, "r")
        p11token = ifd.read(st.st_size)
        ifd.close()

# Prepare data to post the request
data = {"tokengroup" :  p11tokgroup, "tokentemplate" : p11toktemplate}
data["token"] = p11token
u = p11url + "/rest/v2.0/detokenize"

# Post the request
r = requests.post(u, headers=hdrs, auth=p11auth, verify=False, json=data)

# Check if debug flag is true print format json
if (p11debug):
    print("\nHeader: %s" % r.request.headers)
    print("URL: %s" % r.request.url)
    print("Data: %s\n" % json.dumps(data))

# Check if return status code is 404
if r.status_code == 404:
    if (p11debug):
        print("\n%s\n" % r.text)
    errs += 1

# Check the return code not 200 print out the error messages
elif r.status_code != 200:
    if (p11debug):
        print("\n%s\n" % r.text)
    else:
        rError = json.dumps(r.text)
        print("error: %s" % rError["error"])
        print("message: %s\n" % rError["message"])
    errs += 1
else:
    result = json.loads(r.text)

# Check if result have data
if result:
        # Print it out to the file
    if p11output:
        file = open(p11output, "w")
        file.write(result['data'])
        print(result['data'])
        file.close()
        print("\nCompleted write text to file name %s.\n" % p11output)
    else:
                # if debug is true print out in json
        if (p11debug):
            print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=1))
        else:
            print("\n Token : %s\n" % result['token'])

sys.exit(errs)
