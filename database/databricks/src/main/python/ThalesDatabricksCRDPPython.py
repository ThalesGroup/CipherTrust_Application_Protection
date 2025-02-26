import requests
import json
import decimal
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
from pyspark.sql.functions import pandas_udf, lit, udf
from pyspark.sql.types import StringType
from decimal import Decimal, InvalidOperation

# Load properties from a configuration file
properties = {}

with open("udfConfig.properties") as prop_file:
    for line in prop_file:
        name, value = line.partition("=")[::2]
        properties[name.strip()] = value.strip()

REVEALRETURNTAG = "data"
PROTECTRETURNTAG = "protected_data"

def thales_crdp_python_function(databricks_inputdata, mode, datatype):
    encdata = ""

    # Check for invalid data
    if datatype.lower() != "char":
        databricks_inputdata = str(databricks_inputdata)

    # Check for invalid data
    if databricks_inputdata is not None and databricks_inputdata.strip():
        # Check if the length of the input is less than 2
        if len(databricks_inputdata) < 2:
            return databricks_inputdata

        # Check if datatype is not 'char'
        if datatype.lower() != "char":
            lower_bound = -9
            upper_bound = -1

            try:
                # Convert the string to an integer
                number = Decimal(databricks_inputdata)

                # Check if the number is between -1 and -9
                if lower_bound <= number <= upper_bound:
                    print("The input is a negative number between -1 and -9.")
                    return databricks_inputdata

            except ValueError:
                print("The input is not a valid number.")
                return databricks_inputdata

    #else:
        # Return input if it is None or empty
        #return databricks_inputdata

    # Fetch properties
    crdpip = properties.get("CRDPIP")
    if not crdpip:
        raise ValueError("No CRDPIP found for UDF.")

    return_ciphertext_for_user_without_key_access = (
        properties.get("returnciphertextforuserwithnokeyaccess", "no").lower() == "yes"
    )
    user_set_lookup = properties.get("usersetlookup", "no").lower() == "yes"
    key_metadata_location = properties.get("keymetadatalocation")
    external_version_from_ext_source = properties.get("keymetadata")
    protection_profile = properties.get("protection_profile")

    #Print protection profile and key metadata location for debugging
    #print("Protection Profile:", protection_profile)
    #print("Key Metadata Location:", key_metadata_location)

    data_key = "data"
    if mode == "reveal":
        data_key = "protected_data"

    try:
        json_tag_for_protect_reveal = (
            PROTECTRETURNTAG if mode == "protect" else REVEALRETURNTAG
        )
        show_reveal_key = (
            properties.get("showrevealinternalkey", "yes").lower() == "yes"
        )

        sensitive = databricks_inputdata

        # Prepare payload for the protect/reveal request
        crdp_payload = {
            "protection_policy_name": protection_profile,
            data_key: sensitive,
        }

        if mode == "reveal":
            crdp_payload["username"] = "admin"
            if key_metadata_location.lower() == "external":
                crdp_payload["external_version"] = external_version_from_ext_source

        # Construct URL and make the HTTP request
        url_str = f"http://{crdpip}:8090/v1/{mode}"
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            url_str, headers=headers, data=json.dumps(crdp_payload)
        )
        response_json = response.json()

        if response.ok:
            protected_data = response_json.get(json_tag_for_protect_reveal)
            if (
                mode == "protect"
                and key_metadata_location.lower() == "internal"
                and not show_reveal_key
            ):
                protected_data = (
                    protected_data[7:] if len(protected_data) > 7 else protected_data
                )
            encdata = protected_data
        else:
            raise ValueError(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
        if return_ciphertext_for_user_without_key_access:
            pass
        else:
            raise e

    return encdata


# Register the UDF
thales_crdp_python_udf = udf(thales_crdp_python_function, StringType())
spark.udf.register("thales_crdp_python_udf", thales_crdp_python_udf)

#Test

#Simple test
sensitive = "45444555"
singlevalue = thales_crdp_python_function(sensitive, "protect", "nbr")
print(f"sensitive: {sensitive}, Encrypted: {singlevalue}")

# Step 1: Fetch data using SQL query
query_result_bal = spark.sql(
    "SELECT c_acctbal FROM samples.tpch.customer where c_acctbal > 1000 LIMIT 5"
)
query_result = spark.sql("SELECT c_name FROM samples.tpch.customer LIMIT 5")

# Step 2: Extract names into a list
names = [row.c_name for row in query_result.collect()]
bals = [row.c_acctbal for row in query_result_bal.collect()]

mode="protect"
key_metadata_location = properties.get("keymetadatalocation")
datatype = "nbr"

# Step 3: Make the call depending on what the mode and datatype is.  Note you must also 
#make sure the udfConfig.property file contains settings that are compatible for the test you
#are running. 


if mode == "protect":
    if datatype == "char":
        encrypted_names = [thales_crdp_python_function(name, "protect", "char") for name in names]
        for original, encrypted in zip(names, encrypted_names):
            print(f"Original: {original}, Encrypted: {encrypted}")
        # Apply the UDF to the DataFrame
        df_with_encrypted_names = query_result.withColumn("encrypted_name", thales_crdp_python_udf(query_result.c_name, lit("protect"), lit("char")))
        # Show the results
        df_with_encrypted_names.show()
    else:
        encrypted_bals = [thales_crdp_python_function(bal, "protect", "nbr") for bal in bals]
        for original, encrypted in zip(bals, encrypted_bals):
            print(f"Original: {original}, Encrypted: {encrypted}")
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
            
    # Call the function with the test data
    reveal_results = [thales_crdp_python_function(protecteddata, mode, datatype) for protecteddata in reveal_data]       
    print("Results:", reveal_results)
