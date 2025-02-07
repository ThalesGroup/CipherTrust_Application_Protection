%python
import requests
import json
from decimal import Decimal, InvalidOperation

# Load properties from a configuration file
properties = {}

with open("udfConfig.properties") as prop_file:
    for line in prop_file:
        name, value = line.partition("=")[::2]
        properties[name.strip()] = value.strip()

def check_valid(databricks_inputdata, datatype):
    encdata = ""
    BADDATATAG = "99999999999"
    # Check for invalid data
    if databricks_inputdata is not None and databricks_inputdata.strip():
        # Check if the length of the input is less than 2
        if len(databricks_inputdata) < 2:
            return BADDATATAG  + databricks_inputdata
        print
        # Check if datatype is not 'char'
        if datatype.lower() != "char":
            lower_bound = -9
            upper_bound = -1
             
            try:
                # Convert the string to an Decimal
                number = Decimal(databricks_inputdata)
                 
                # Check if the number is between -1 and -9
                if lower_bound <= number <= upper_bound:
                    #print("The input is a negative number between -1 and -9.")
                    return BADDATATAG

            except ValueError:
               #print("The input is not a valid number.")
                return BADDATATAG
    else:
        # Return input if it is None or empty
        return BADDATATAG
    
    return databricks_inputdata

def prepare_reveal_input(protected_data, protection_policy_name, key_metadata_location, external_version=None):
    # Base reveal payload structure
    reveal_payload = {
        "protection_policy_name": protection_policy_name,
        "username": "admin",
        "protected_data_array": []
    }

    # Add external version if key_metadata_location is 'external'
    if key_metadata_location == "external" and external_version:
        reveal_payload["protected_data_array"] = [
            {"protected_data": data, "external_version": external_version} for data in protected_data
        ]
    else:
        reveal_payload["protected_data_array"] = [
            {"protected_data": data} for data in protected_data
        ]

    return reveal_payload


def thales_crdp_python_function_bulk(databricks_inputdata, mode, datatype):
    encdata = []

    # Convert input data to string if datatype is not 'char'
    if datatype.lower() != "char":
        databricks_inputdata = [check_valid(str(data),datatype) for data in databricks_inputdata]
    print("databricks_inputdata", databricks_inputdata)
    # Fetch properties
    crdpip = properties.get("CRDPIP")
    if not crdpip:
        raise ValueError("No CRDPIP found for UDF.")

    return_ciphertext_for_user_without_key_access = (
        properties.get("returnciphertextforuserwithnokeyaccess", "no").lower() == "yes"
    )
    key_metadata_location = properties.get("keymetadatalocation")
    external_version_from_ext_source = properties.get("keymetadata")
    protection_profile = properties.get("protection_profile")

    if mode == "protectbulk":
        input_data_key_array = "data_array"
        output_data_key_array = "protected_data_array"
        output_element_key = "protected_data"
    else:
        input_data_key_array = "protected_data_array"
        output_data_key_array = "data_array"
        output_element_key = "data"

    print("mode:", mode)
    try:

        show_reveal_key = (
            properties.get("showrevealinternalkey", "yes").lower() == "yes"
        )

        # Prepare payload for bulk protect/reveal request
        if mode == "protectbulk":
            crdp_payload = {"protection_policy_name": protection_profile,input_data_key_array: databricks_inputdata}
        else:
            if key_metadata_location == "external":
                crdp_payload = prepare_reveal_input(databricks_inputdata, protection_profile,key_metadata_location,external_version_from_ext_source)
            else:
                crdp_payload = prepare_reveal_input(databricks_inputdata, protection_profile,key_metadata_location)
  
        if mode == "revealbulk":
            crdp_payload["username"] = "admin"

        # Construct URL and make the HTTP request
        url_str = f"http://{crdpip}:8090/v1/{mode}"
        headers = {"Content-Type": "application/json"}

        print("Sending request to URL:", url_str)

        data=json.dumps(crdp_payload)
        print("Sending data:", data)
        response = requests.post(
            url_str, headers=headers, data=json.dumps(crdp_payload)
        )
        response_json = response.json()

        if response.ok:
            protected_data_array = response_json.get(output_data_key_array, [])
            encdata = [item[output_element_key] for item in protected_data_array]
            # Handle response for bulk data
            if mode == "protectbulk" and key_metadata_location.lower() == "internal" and not show_reveal_key:
                encdata = [
                    data[7:] if len(data) > 7 else data for data in encdata
                ]
        else:
            raise ValueError(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
        if return_ciphertext_for_user_without_key_access:
            pass
        else:
            raise e

    return encdata

#Test
# Step 1: Fetch data using SQL query
query_result_bal = spark.sql(
    "SELECT c_acctbal FROM samples.tpch.customer where c_acctbal > 1000 LIMIT 5"
)
query_result = spark.sql("SELECT c_name FROM samples.tpch.customer LIMIT 5")

# Step 2: Extract names into a list
names = [row.c_name for row in query_result.collect()]
bals = [row.c_acctbal for row in query_result_bal.collect()]

mode="protectbulk"
key_metadata_location = properties.get("keymetadatalocation")
datatype = "nbr"

# Step 3: Make the call depending on what the mode and datatype is.  Note you must also 
#make sure the udfConfig.property file contains settings that are compatible for the test you
#are running. 


if mode == "protectbulk":
    if datatype == "char":
        encrypted_names = thales_crdp_python_function_bulk(names, mode, datatype)
        print("Encrypted Names:", encrypted_names)
    else:
        encrypted_bals = thales_crdp_python_function_bulk(bals, mode, datatype)
        print("Encrypted Balance nbr:", encrypted_bals)
else:
    if datatype == "char":
        if (key_metadata_location == "external"):
            reveal_data = ['INlGNUmQ#k6ooUjm2A', 'KAE09OFh#eiQhgLgfI', 'RsqD5rr9#B4spSHZvD', 'HXguI0J5#TVXNJgtS5', 'MIt7SMGA#iuikyynnl']
        else:
            reveal_data = ['1001000hhIQGjma#fH5yPPOda', '1001000rXhadmXl#XxRlFW0YU', '1001000BvDFNg8p#NbyCunqpT', '1001000w5U1O9iu#59Ulv2yA8', '1001000CzyGv0KB#mFf9pcKUY']
    else:
        if (key_metadata_location == "external"):
            reveal_data = ['7080.44', '7382.75', '1971.05', '8044.16', '2361.92']
            #reveal_data = ['41', '-53', '343075883524', '22262837758', '208755']
        else:
            reveal_data = ['10020007080.44', '10020007382.75', '10020001971.05', '10020008044.16', '10020002361.92']
            
    # Call the bulk function with the test data
    encrypted_test_data = thales_crdp_python_function_bulk(reveal_data, mode, datatype)        
    print("Results:", encrypted_test_data)