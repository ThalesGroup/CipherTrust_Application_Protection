package com.example;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonPrimitive;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.util.HashMap;
import java.util.Map;

/* This is a Thales CRDP UDF for Snowflake.  
 * It is an example of how to use Thales CipherTrust REST Application Dataprotection (CRDP)
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.  
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.14 and CRDP 1.0
*  For more information on CRDP see link below. 
https://thalesdocs.com/ctp/con/crdp/latest/index.html
*  For more information on Snowflake External Functions see link below. 
https://docs.snowflake.com/en/sql-reference/external-functions-creating-gcp
 * 
 *@author  mwarner
 * 
 */
public class ThalesGCPSnowCRDPFPE implements HttpFunction {
//  @Override

	private static final Gson gson = new Gson();
	private static final String BADDATATAG = new String("9999999999999999");
	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	public void service(HttpRequest request, HttpResponse response) throws Exception {
		Map<Integer, String> snowErrorMap = new HashMap<Integer, String>();
		String encdata = "";
		String snowflakereturnstring = null;
		int statusCode = 200;
		JsonObject result = new JsonObject();
		JsonArray replies = new JsonArray();
		JsonArray rownbranddata = new JsonArray();

		String keyName = "testfaas";
		String crdpip = System.getenv("CRDPIP");
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");

		// returnciphertextforuserwithnokeyaccess = is a environment variable to express how data should be returned
		// when the user above does not have access to the key and if doing a
		// lookup in the userset and the user does not exist. If returnciphertextforuserwithnokeyaccess = no
		// then an error will be returned to the query, else the results set will provide ciphertext.
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		// yes,no
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");
		// usersetlookup = should a userset lookup be done on the user from Cloud DB
		// yes,no
		String usersetlookup = System.getenv("usersetlookup");
		// usersetidincm = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it is the userset in CM but could be
		// a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");
		String keymetadatalocation = System.getenv("keymetadatalocation");
		String external_version_from_ext_source = System.getenv("keymetadata");
		String protection_profile = System.getenv("protection_profile");
		String mode = System.getenv("mode");
		String datatype = System.getenv("datatype");

		String dataKey = null;

		boolean bad_data = false;
		String jsonTagForProtectReveal = null;

		String showrevealkey = "yes";

		if (mode.equals("protect")) {
			dataKey = "data";
			jsonTagForProtectReveal = PROTECTRETURNTAG;
			if (keymetadatalocation.equalsIgnoreCase("internal")) {
				showrevealkey = System.getenv("showrevealinternalkey");
				if (showrevealkey == null)
					showrevealkey = "yes";
			}
		} else {
			dataKey = "protected_data";
			jsonTagForProtectReveal = REVEALRETURNTAG;
		}
		boolean showrevealkeybool = showrevealkey.equalsIgnoreCase("yes");

		String snowflakeuser = "snowflakeuser";
		JsonArray snowflakedata = null;

		try {

			// This code is only to be used when input data contains user info.
			/*
			 * if (usersetlookupbool) { // make sure cmuser is in Application Data Protection Clients Group
			 * 
			 * boolean founduserinuserset = findUserInUserSet(bigquerysessionUser, userName, password, usersetID,
			 * userSetLookupIP); // System.out.println("Found User " + founduserinuserset); if (!founduserinuserset)
			 * throw new CustomException("1001, User Not in User Set", 1001);
			 * 
			 * } else { usersetlookupbool = false; }
			 */

			try {
				JsonElement requestParsed = gson.fromJson(request.getReader(), JsonElement.class);
				JsonObject requestJson = null;

				if (requestParsed != null && requestParsed.isJsonObject()) {
					requestJson = requestParsed.getAsJsonObject();
				}

				if (requestJson != null && requestJson.has("data")) {
					snowflakedata = requestJson.getAsJsonArray("data");

				}

			} catch (JsonParseException e) {
				System.out.println("Error parsing JSON: " + e.getMessage());

			}

			int row_number = 0;

			String protectedData = null;
			String externalkeymetadata = null;
			String crdpjsonBody = null;
			// String external_version_from_ext_source = "1004001";
			// String external_version_from_ext_source = "1001001";

			JsonObject crdp_payload = new JsonObject();

			crdp_payload.addProperty("protection_policy_name", protection_profile);

			String sensitive = null;
			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");
			String urlStr = "http://" + crdpip + ":8090/v1/" + mode;

			// encrypt data
			for (int i = 0; i < snowflakedata.size(); i++) {
				JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

				for (int j = 0; j < snowflakerow.size(); j++) {

					if (j == 1) {
						// String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
						// FPE example
						sensitive = checkValid(snowflakerow);
						if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								if (sensitive.contains("notvalid")) {
									sensitive = sensitive.replace("notvalid", "");
								} else
									sensitive = BADDATATAG;

							} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {

							} else if (sensitive.contains("notvalid")) {
								sensitive = sensitive.replace("notvalid", "");

							}
							encdata = sensitive;

						} else {

							crdp_payload.addProperty(dataKey, sensitive);
							if (mode.equals("reveal")) {
								crdp_payload.addProperty("username", snowflakeuser);
								if (keymetadatalocation.equalsIgnoreCase("external")) {
									crdp_payload.addProperty("external_version", external_version_from_ext_source);
								}
							}
							crdpjsonBody = crdp_payload.toString();
							// System.out.println(crdpjsonBody);
							RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

							Request crdp_request = new Request.Builder().url(urlStr).method("POST", body)
									.addHeader("Content-Type", "application/json").build();
							Response crdp_response = client.newCall(crdp_request).execute();

							if (crdp_response.isSuccessful()) {

								// Parse JSON response
								String responseBody = crdp_response.body().string();
								Gson gson = new Gson();
								JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);

								if (jsonObject.has(jsonTagForProtectReveal)) {
									protectedData = jsonObject.get(jsonTagForProtectReveal).getAsString();
									if (keymetadatalocation.equalsIgnoreCase("external")
											&& mode.equalsIgnoreCase("protect")) {
										externalkeymetadata = jsonObject.get("external_version").getAsString();
										// System.out.println("Protected Data ext key metadata need to store this: "
										// + externalkeymetadata);
									}

									if (keymetadatalocation.equalsIgnoreCase("internal")
											&& mode.equalsIgnoreCase("protect") && !showrevealkeybool) {
										if (protectedData.length() > 7)
											protectedData = protectedData.substring(7);
									}

								} else if (jsonObject.has("error_message")) {
									String errorMessage = jsonObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									snowErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");
							} else {
								System.err.println("Request failed with status code: " + crdp_response.code());
							}

							crdp_response.close();

							encdata = protectedData;

						}

						rownbranddata.add(encdata);
						replies.add(rownbranddata);
						rownbranddata = new JsonArray();

					} else {
						JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
						row_number = snowflakecolumn.getAsInt();
						rownbranddata.add(row_number);

					}

				}

			}

			result.add("data", replies);
			snowflakereturnstring = result.toString();

		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());
			snowflakereturnstring = "exception ";
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

					result = new JsonObject();
					replies = new JsonArray();
					rownbranddata = new JsonArray();

					for (int i = 0; i < snowflakedata.size(); i++) {

						JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

						for (int j = 0; j < snowflakerow.size(); j++) {
							if (j == 1) {
								// String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
								// FPE example
								String sensitive = checkValid(snowflakerow);

								if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
									if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
										if (sensitive.contains("notvalid")) {
											// System.out.println("adding null not charint or nbr");
											sensitive = sensitive.replace("notvalid", "");
										} else
											sensitive = BADDATATAG;

									} else if (sensitive.equalsIgnoreCase("null")
											|| sensitive.equalsIgnoreCase("notvalid")) {

									} else if (sensitive.contains("notvalid")) {
										sensitive = sensitive.replace("notvalid", "");

									}
									encdata = sensitive;

								} else {
									// System.out.println("normal number data" + sensitive);
								}
								rownbranddata.add(sensitive);
								replies.add(rownbranddata);
								rownbranddata = new JsonArray();

							} else {
								JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
								int row_number = snowflakecolumn.getAsInt();
								rownbranddata.add(row_number);
							}
						}
					}

					result.add("data", replies);
					JsonObject inputJsonObject = new JsonObject();
					String bodyString = result.toString();
					inputJsonObject.addProperty("statusCode", 200);
					inputJsonObject.addProperty("body", bodyString);

					snowflakereturnstring = inputJsonObject.toString();
					// System.out.println(" new data " + snowflakereturnstring);

				} else {
					statusCode = 400;
					snowflakereturnstring = formatReturnValue(statusCode);
					e.printStackTrace(System.out);
				}
			} else {
				statusCode = 400;
				snowflakereturnstring = formatReturnValue(statusCode);
				e.printStackTrace(System.out);
			}

		} finally {

		}
		// System.out.println(snowflakereturnstring);
		response.getWriter().write(snowflakereturnstring);

	}

	public String formatReturnValue(int statusCode)

	{
		StringBuffer snowflakereturndatasb = new StringBuffer();

		snowflakereturndatasb.append("{ \"statusCode\":");
		snowflakereturndatasb.append(statusCode);
		snowflakereturndatasb.append(",");
		snowflakereturndatasb.append(" \"body\": {");
		snowflakereturndatasb.append(" \"data\": [");
		snowflakereturndatasb.append("] }}");
		System.out.println("in exception with ");
		return snowflakereturndatasb.toString();
	}

	public String checkValid(JsonArray snowrow) {
		String inputdata = null;
		String notvalid = "notvalid";
		if (snowrow != null && snowrow.size() > 0) {
			JsonElement element = snowrow.get(1);
			if (element != null && !element.isJsonNull()) {
				inputdata = element.getAsString();
				if (inputdata.isEmpty() || inputdata.length() < 2) {
					inputdata = notvalid + inputdata;
				}
			} else {
				// System.out.println("Sensitive data is null or empty.");
				inputdata = notvalid + inputdata;
			}
		} else {
			// System.out.println("bigquerytrow is null or empty.");
			inputdata = notvalid + inputdata;
		}

		return inputdata;

	}

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

	}

}