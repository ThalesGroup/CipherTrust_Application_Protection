import json
import ssl
import sys
import requests
from urllib3 import disable_warnings, exceptions
from requests.auth import HTTPBasicAuth

BATCH_LIMIT = 5000

def main(args):
    crdp_container_ip = "yourip"
    batch_size = 250
    protect_url = f"http://{crdp_container_ip}:8090/v1/protect"
    debug = False
    protection_profile = "plain-nbr-internal"
    mode_of_operation = "regular"
    
    if args[1] != "null":
        debug = args[1].lower() == "true"
        
    if args[2] != "null":
        mode_of_operation = args[2]
        
    if mode_of_operation.lower() == "bulk":
        protect_url = protect_url + "bulk"
        
    file_path = r"C:\data\emp-id1k.txt"
    total_records = 0
    
    if mode_of_operation.lower() == "regular":
        total_records = protect_from_file(protect_url, debug, file_path, protection_profile)
        nbrofchunks = 1
    else:
        strings = read_strings_from_file(file_path)
        total_number_of_records = len(strings)
        index = 0
        nbrofchunks = 0
        records_left = total_number_of_records
        
        batch_nnn = []
        if batch_size > total_number_of_records:
            batch_size = total_number_of_records
        if batch_size >= BATCH_LIMIT:
            batch_size = BATCH_LIMIT
            
        while index < total_number_of_records:
            for i in range(batch_size):
                if index < total_number_of_records:
                    batch_nnn.append(strings[index])
                    index += 1
                    records_left -= 1
            
            total_records += protect_from_file_bulk(protect_url, debug, batch_nnn, batch_size, index, total_number_of_records, records_left, protection_profile)
            batch_nnn = []
            nbrofchunks += 1

    print(f"Total records = {total_records}")

def protect_from_file_bulk(url, debug, strings, batch_size, index, total_number_of_records, records_left, protection_profile):
    total_nb_of_records = 0
    count = 0
    crdp_payload_array = []
    
    for str_ in strings:
        total_nb_of_records += 1
        crdp_payload_array.append(str_)
        count += 1
        
        if count == batch_size:
            crdp_payload = {"data_array": crdp_payload_array, "protection_policy_name": protection_profile}
            json_body = json.dumps(crdp_payload)
            if debug:
                print("json body:", json_body)
            make_cm_call(json_body, url, debug)
            crdp_payload_array = []
            count = 0
            
    if count > 0:
        crdp_payload = {"data_array": crdp_payload_array, "protection_policy_name": protection_profile}
        json_body = json.dumps(crdp_payload)
        if debug:
            print("json body:", json_body)
        make_cm_call(json_body, url, debug)

    return total_nb_of_records

def protect_from_file(url, debug, file_path, protection_profile):
    total_nb_of_records = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            total_nb_of_records += 1
            crdp_payload = {
                "protection_policy_name": protection_profile,
                "data": line.strip()
            }
            json_body = json.dumps(crdp_payload)
            if debug:
                print("jsonBody", json_body)
            make_cm_call(json_body, url, debug)
    
    return total_nb_of_records

def disable_cert_validation():
    disable_warnings(exceptions.InsecureRequestWarning)
    ssl._create_default_https_context = ssl._create_unverified_context

def make_cm_call(payload, url, debug):
    disable_cert_validation()
    
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, data=payload, headers=headers, verify=False)
    
    if debug:
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    
    return response.status_code

def read_strings_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print( len(sys.argv))
        print("Usage: script.py <debug> <mode_of_operation>")
        sys.exit(1)
    
    # sys.argv[0] is the script name, so pass args starting from index 1
    args = sys.argv[1:]
    print(f"Debug mode: {args[1]}, Mode of operation: {args[2]}")
    main(args)