#!/bin/bash
CT="Content-Type:application/json"
#This script will create tokengroups,tokentemplates,mask and users in the Token Server (VTS or CTS which is the new branded name).
#For best practices and seperation of duties it assumes you have already created keys in the Key Manager. vts-key-n where n = number of keys.
#After running this script you should then proceed to the VTS UI and assign masks to Users and also to to permissions to assign access to tokenize or detoken for the various keys.

URL='youripadddresstovts'


PWD="youpwd!"
CT="Content-Type:application/json"
Credentials='{"username":"vtsroot","password":"'$PWD'"}'
echo $Credentials
AUTH="curl -k -X POST -H $CT -d $Credentials https://$URL/api/api-token-auth/"
RESPONSE=`$AUTH`
TOKEN=$(echo "$RESPONSE" | jq -r '.token')
echo $TOKEN

# create standard tokengroups/tokentemplates

i=0
for i in {1..1}
do
groupname="vtsgroup"$i
keyname="vts-key-"$i
templatename="vtstemplate"$i
Datagroup='{"name":"'$groupname'","key":"'$keyname'"}'
echo $keyname
echo $groupname
echo $templatename
echo $Datagroup
 
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$Datagroup"'' https://$URL/api/tokengroups/)
RESPONSE2= curl "${args[@]}"
echo $RESPONSE2
Datatemplate='{"name":"'$templatename'","tenant":"'$groupname'" ,"format": "FPE", "keepleft" : 0, "keepright": 0, "charset": "All digits", "prefix": "", "startyear": null, "endyear": null, "irreversible": false}'
echo $Datatemplate
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$Datatemplate"'' https://$URL/api/tokentemplates/)
RESPONSETemplate= curl "${args[@]}"
echo $RESPONSETemplate

i=$i+1
done

# create project specific tokengroups 
Datagroup='{"name":"Demo","key":"vts-key-1"}'
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$Datagroup"'' https://$URL/api/tokengroups/)
RESPONSE2= curl "${args[@]}"
echo $RESPONSE2

Datagroup='{"name":"t1","key":"vts-key-1"}'
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$Datagroup"'' https://$URL/api/tokengroups/)
RESPONSE2= curl "${args[@]}"
echo $RESPONSE2

# create project specific tokentemplates 
cctemplate='{"name":"Credit Card","tenant":"t1" ,"format": "FPE", "keepleft" : 0, "keepright": 0, "charset": "All digits", "prefix": "", "startyear": null, "endyear": null, "irreversible": false}'
echo $cctemplate
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$cctemplate"'' https://$URL/api/tokentemplates/)
RESPONSEcc= curl "${args[@]}"
echo $RESPONSEcc

numerictemplate='{"name":"Numeric","tenant":"Demo" ,"format": "FPE", "keepleft" : 0, "keepright": 0, "charset": "All digits", "prefix": "", "startyear": null, "endyear": null, "irreversible": false}'
echo $numerictemplate
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$numerictemplate"'' https://$URL/api/tokentemplates/)
RESPONSEnumeric= curl "${args[@]}"
echo $RESPONSEnumeric

texttemplate='{"name":"Text","tenant":"Demo" ,"format": "FPE", "keepleft" : 0, "keepright": 0, "charset": "Alphanumeric", "prefix": "", "startyear": null, "endyear": null, "irreversible": false}'
echo $texttemplate
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$texttemplate"'' https://$URL/api/tokentemplates/)
RESPONSEtext= curl "${args[@]}"
echo $RESPONSEtext

prefixtemplate='{"name":"prefixexample","tenant":"Demo" ,"format": "FPE", "keepleft" : 0, "keepright": 0, "charset": "Alphanumeric", "prefix": "pre-", "startyear": null, "endyear": null, "irreversible": false}'
echo $prefixtemplate
args=(-k -X POST -H 'Authorization: Bearer '"$TOKEN"'' -H Content-Type:application/json -d ''"$prefixtemplate"'' https://$URL/api/tokentemplates/)
RESPONSEprefix= curl "${args[@]}"
echo $RESPONSEprefix


#create masks
curl -X POST "https://$URL/api/masks/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"name\": \"showleft6\", \"showleft\": 6, \"showright\": 0, \"maskchar\": \"?\"}"
curl -X POST "https://$URL/api/masks/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"name\": \"first2last2\", \"showleft\": 2, \"showright\": 2, \"maskchar\": \"X\"}"
curl -X POST "https://$URL/api/masks/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"name\": \"all\", \"showleft\": 99, \"showright\": 99, \"maskchar\": \"X\"}"
curl -X POST "https://$URL/api/masks/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"name\": \"last4\", \"showleft\": 0, \"showright\": 4, \"maskchar\": \"X\"}"

PWD="Customer123!"
#create users
echo "password" $PWD
curl -X POST "https://$URL/api/users/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"username\": \"fraud\", \"email\":\"fraud@example.com\", \"password\": \"$PWD\", \"is_active\": true, \"is_staff\": true, \"is_superuser\": false}"
curl -X POST "https://$URL/api/users/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"username\": \"custserv1\", \"email\":\"custserv1@example.com\", \"password\": \"$PWD\", \"is_active\": true, \"is_staff\": true, \"is_superuser\": false}"
curl -X POST "https://$URL/api/users/" -H "accept: application/json" -H "Content-Type: application/json" -H 'authorization: Bearer '"$TOKEN"'' -k -d "{ \"username\": \"custserv2\", \"email\":\"custserv2@example.com\", \"password\": \"$PWD\", \"is_active\": true, \"is_staff\": true, \"is_superuser\": false}"
