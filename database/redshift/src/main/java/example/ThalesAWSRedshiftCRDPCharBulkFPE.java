package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.io.IOUtils;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

/*
 * This test app to test the logic for a AWS Redshift Database User Defined
 * Function(UDF). It is an example of how to use Thales Cipher REST Data Protection (CRDP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns.
 * 
 * This uses the protectbulk and revealbulk api's.
 * Note: This source code is only to be used for testing and proof of concepts.
 * Not production ready code. Was tested with CM 2.14 &
 * CRDP 1.0 tech preview For more information on CRDP see link below.
 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
 * 
 * @author mwarner
 * 
 */

public class ThalesAWSRedshiftCRDPCharBulkFPE implements RequestStreamHandler {

	private static final Gson gson = new Gson();

	private static int BATCHLIMIT = 10000;

	/**
	 * Returns an String that will be the encrypted value
	 * <p>
	 */

	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {

		String input = IOUtils.toString(inputStream, "UTF-8");
		JsonParser parser = new JsonParser();
		int statusCode = 200;
		boolean status = true;
		String redshiftreturnstring = null;
		StringBuffer redshiftreturndata = new StringBuffer();

		int numberofchunks = 0;
		JsonObject redshiftinput = null;
		JsonElement rootNode = parser.parse(input);
		JsonArray redshiftdata = null;
		String redshiftuserstr = null;

		Map<Integer, String> reshift_ErrorMap = new HashMap<Integer, String>();
		// https://www.baeldung.com/java-aws-lambda

		StringBuffer redshiftreturndatasb = new StringBuffer();
		StringBuffer redshiftreturndatasc = new StringBuffer();
		StringBuffer protection_policy_buff = new StringBuffer();

		if (rootNode.isJsonObject()) {
			redshiftinput = rootNode.getAsJsonObject();
			if (redshiftinput != null) {
				redshiftdata = redshiftinput.getAsJsonArray("arguments");
				JsonPrimitive userjson = redshiftinput.getAsJsonPrimitive("user");
				redshiftuserstr = userjson.getAsJsonPrimitive().toString();
				redshiftuserstr = redshiftuserstr.replace("\"", "");
			} else {
				System.out.println("Root node not found.");
			}
		} else {
			System.out.println("Bad data from snowflake.");
		}

		JsonPrimitive nbr_of_rows_json = redshiftinput.getAsJsonPrimitive("num_records");
		String nbr_of_rows_json_str = nbr_of_rows_json.getAsJsonPrimitive().toString();
		int nbr_of_rows_json_int = Integer.parseInt(nbr_of_rows_json_str);

		String crdpip = System.getenv("CRDPIP");
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");

		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");

		String usersetlookup = System.getenv("usersetlookup");
		String usersetID = System.getenv("usersetidincm");
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");
		String keymetadatalocation = System.getenv("keymetadatalocation");
		String external_version_from_ext_source = System.getenv("keymetadata");
		String protection_profile = System.getenv("protection_profile");
		String mode = System.getenv("mode");
		String inputDataKey = null;
		String outputDataKey = null;
		String protectedData = null;
		String externalkeymetadata = null;
		boolean bad_data = false;
		String notvalid = "notvalid";
		String jsonBody = null;

		int error_count = 0;

		// String external_version_from_ext_source = "1004001";
		// String external_version_from_ext_source = "1001001";

		JsonObject crdp_payload = new JsonObject();

		if (mode.equals("protectbulk")) {
			inputDataKey = "data_array";
			outputDataKey = "protected_data_array";
		} else {
			inputDataKey = "protected_data_array";
			outputDataKey = "data_array";

		}

		int totalNbrofRows = redshiftdata.size();
		int totalRowsLeft = totalNbrofRows;
		int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
		if (batchsize > totalNbrofRows)
			batchsize = totalNbrofRows;
		if (batchsize >= BATCHLIMIT)
			batchsize = BATCHLIMIT;

		try {

			// Serialization
			redshiftreturndatasb.append("{ \"success\":");
			redshiftreturndatasb.append(status);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"num_records\":");
			redshiftreturndatasb.append(nbr_of_rows_json_int);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"results\": [");

			if (usersetlookupbool) {
			// make sure cmuser is in Application Data Protection Clients Group

				boolean founduserinuserset = findUserInUserSet(redshiftuserstr, userName, password, usersetID,
						userSetLookupIP);
				// System.out.println("Found User " + founduserinuserset);
				if (!founduserinuserset)
					throw new CustomException("1001, User Not in User Set", 1001);

			} else {
				usersetlookupbool = false;
			}


			int i = 0;
			int count = 0;
			boolean newchunk = true;
			JsonArray crdp_payload_array = new JsonArray();

			while (i < redshiftdata.size()) {

				if (newchunk) {
					crdp_payload_array = new JsonArray();
					protection_policy_buff = new StringBuffer();
					newchunk = false;
					count = 0;
				}

				String sensitive = null;
				JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

				sensitive = checkValid(redshiftrow);
				
				protection_profile = protection_profile.trim();
				// Format the output
				String formattedElement = String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
				protection_policy_buff.append(formattedElement);
				protection_policy_buff.append(",");

				if (mode.equals("protectbulk")) {
					crdp_payload_array.add(sensitive);
				} else {
					JsonObject protectedDataObject = new JsonObject();
					protectedDataObject.addProperty("protected_data", sensitive);
					if (keymetadatalocation.equalsIgnoreCase("external")) {
						protectedDataObject.addProperty("external_version", external_version_from_ext_source);
					}
					crdp_payload_array.add(protectedDataObject);
				//	System.out.println(gson.toJson(crdp_payload_array));
				}
				if (count == batchsize - 1) {

					crdp_payload.add(inputDataKey, crdp_payload_array);
					String inputdataarray = null;
					if (mode.equals("revealbulk")) {
						crdp_payload.addProperty("username", redshiftuserstr);
						inputdataarray = crdp_payload.toString();
						protection_policy_buff.append(inputdataarray);
						jsonBody = protection_policy_buff.toString();
						jsonBody = jsonBody.replaceFirst("\\{", " ");

					} else {
						inputdataarray = crdp_payload.toString();
						protection_policy_buff.append(inputdataarray);
						inputdataarray = protection_policy_buff.toString();
						jsonBody = inputdataarray.replace("{", " ");
					}
					jsonBody = "{" + jsonBody;

					OkHttpClient client = new OkHttpClient().newBuilder().build();
					MediaType mediaType = MediaType.parse("application/json");

					//System.out.println(jsonBody);
					RequestBody body = RequestBody.create(mediaType, jsonBody);
					String urlStr = "http://" + crdpip + ":8090/v1/" + mode;
					// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
					//System.out.println(urlStr);
					Request crdp_request = new Request.Builder()
							// .url("http://192.168.159.143:8090/v1/protect").method("POST", body)
							.url(urlStr).method("POST", body).addHeader("Content-Type", "application/json").build();
					Response crdp_response = client.newCall(crdp_request).execute();
					String crdpreturnstr = null;
					if (crdp_response.isSuccessful()) {
						// Parse JSON response
						String responseBody = crdp_response.body().string();
						JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
						JsonArray protectedDataArray = jsonObject.getAsJsonArray(outputDataKey);

						String status_res = jsonObject.get("status").getAsString();
						int success_count = jsonObject.get("success_count").getAsInt();
						error_count = jsonObject.get("error_count").getAsInt();
						System.out.println("errors " + error_count);

						if (mode.equals("protectbulk")) {

							for (JsonElement element : protectedDataArray) {
								JsonObject protectedDataObject = element.getAsJsonObject();
								if (protectedDataObject.has("protected_data")) {

									protectedData = protectedDataObject.get("protected_data").getAsString();
									//System.out.println(protectedData);
									// add to
									protectedData = "\"" + protectedData + "\"";
									redshiftreturndatasc.append(new String(protectedData));
									redshiftreturndatasc.append(",");
									if (keymetadatalocation.equalsIgnoreCase("external")) {
										externalkeymetadata = protectedDataObject.get("external_version").getAsString();
									//	System.out.println("Protected Data ext key metadata need to store this: "
									//			+ externalkeymetadata);

									}
								} else if (protectedDataObject.has("error_message")) {
									String errorMessage = protectedDataObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									reshift_ErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");

							}
						} else {
							// reveal logic

							for (JsonElement element : protectedDataArray) {
								JsonObject protectedDataObject = element.getAsJsonObject();
								if (protectedDataObject.has("data")) {
									protectedData = protectedDataObject.get("data").getAsString();
									protectedData = "\"" + protectedData + "\"";
									//System.out.println(protectedData);
									redshiftreturndatasc.append(new String(protectedData));
									redshiftreturndatasc.append(",");
								} else if (protectedDataObject.has("error_message")) {
									String errorMessage = protectedDataObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									reshift_ErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");

							}
						}

						crdp_response.close();

						numberofchunks++;
						newchunk = true;
						count = 0;

					} else {
						System.err.println("Request failed with status code: " + crdp_response.code());
					}

				}
				else
				{
					count++;
				}
				
				totalRowsLeft--;
				i++;
 
			}

			if (count > 0) {
				// if (count == batchsize - 1 || (totalRowsLeft <= totalcount)) {
				crdp_payload.add(inputDataKey, crdp_payload_array);
				String inputdataarray = null;
				if (mode.equals("revealbulk")) {
					crdp_payload.addProperty("username", redshiftuserstr);
					inputdataarray = crdp_payload.toString();
					protection_policy_buff.append(inputdataarray);
					jsonBody = protection_policy_buff.toString();
					jsonBody = jsonBody.replaceFirst("\\{", " ");

				} else {
					inputdataarray = crdp_payload.toString();
					protection_policy_buff.append(inputdataarray);
					inputdataarray = protection_policy_buff.toString();
					jsonBody = inputdataarray.replace("{", " ");
				}
				jsonBody = "{" + jsonBody;

				OkHttpClient client = new OkHttpClient().newBuilder().build();
				MediaType mediaType = MediaType.parse("application/json");

			//	System.out.println(jsonBody);
				RequestBody body = RequestBody.create(mediaType, jsonBody);
				String urlStr = "http://" + crdpip + ":8090/v1/" + mode;
				// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
				//System.out.println(urlStr);
				Request crdp_request = new Request.Builder()
						// .url("http://192.168.159.143:8090/v1/protect").method("POST", body)
						.url(urlStr).method("POST", body).addHeader("Content-Type", "application/json").build();
				Response crdp_response = client.newCall(crdp_request).execute();
				String crdpreturnstr = null;
				if (crdp_response.isSuccessful()) {
					// Parse JSON response
					String responseBody = crdp_response.body().string();
					JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
					JsonArray protectedDataArray = jsonObject.getAsJsonArray(outputDataKey);

					String status_res = jsonObject.get("status").getAsString();
					int success_count = jsonObject.get("success_count").getAsInt();
					error_count = jsonObject.get("error_count").getAsInt();
					System.out.println("errors " + error_count);

					if (mode.equals("protectbulk")) {

						for (JsonElement element : protectedDataArray) {
							JsonObject protectedDataObject = element.getAsJsonObject();
							if (protectedDataObject.has("protected_data")) {

								protectedData = protectedDataObject.get("protected_data").getAsString();
								//System.out.println(protectedData);
								protectedData = "\"" + protectedData + "\"";
								// add to
								redshiftreturndatasc.append(new String(protectedData));
								redshiftreturndatasc.append(",");
								if (keymetadatalocation.equalsIgnoreCase("external")) {
									externalkeymetadata = protectedDataObject.get("external_version").getAsString();
								//	System.out.println("Protected Data ext key metadata need to store this: "
								//			+ externalkeymetadata);

								}
							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								reshift_ErrorMap.put(i, errorMessage);
								bad_data = true;
							} else
								System.out.println("unexpected json value from results: ");

						}
					} else {
						// reveal logic

						for (JsonElement element : protectedDataArray) {
							JsonObject protectedDataObject = element.getAsJsonObject();
							if (protectedDataObject.has("data")) {
								protectedData = protectedDataObject.get("data").getAsString();
								protectedData = "\"" + protectedData + "\"";
								//System.out.println(protectedData);
								redshiftreturndatasc.append(new String(protectedData));
								redshiftreturndatasc.append(",");
							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								reshift_ErrorMap.put(i, errorMessage);
								bad_data = true;
							} else
								System.out.println("unexpected json value from results: ");

						}
					}

					crdp_response.close();

					numberofchunks++;
					newchunk = true;
					count = 0;

				} else {
					System.err.println("Request failed with status code: " + crdp_response.code());
				}

			 
			}

			redshiftreturndatasc.append("] ");
			redshiftreturndatasb.append(redshiftreturndatasc);
			redshiftreturndatasb.append("}");

			redshiftreturnstring = new String(redshiftreturndatasb);

		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

					for (int i = 0; i < redshiftdata.size(); i++) {
						JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

						JsonPrimitive redshiftcolumn = redshiftrow.get(0).getAsJsonPrimitive();

						String sensitive = redshiftcolumn.getAsJsonPrimitive().toString();

						redshiftreturndata.append(sensitive);
						if (redshiftdata.size() == 1 || i == redshiftdata.size() - 1)
							continue;
						else
							redshiftreturndata.append(",");
					}
					redshiftreturndata.append("]}");

					redshiftreturnstring = new String(redshiftreturndata);

				} else {
					statusCode = 400;
					redshiftreturnstring = formatReturnValue(statusCode);
					e.printStackTrace(System.out);
				}

			} else {
				statusCode = 400;
				redshiftreturnstring = formatReturnValue(statusCode);
				e.printStackTrace(System.out);
			}
		}

		finally {
			// if (session != null) {
			// session.closeSession();
			// }
		}
		int lastIndex = redshiftreturnstring.lastIndexOf(",");
		// Replace the comma before the closing square bracket if it exists
		if (lastIndex != -1) {
			redshiftreturnstring = redshiftreturnstring.substring(0, lastIndex)
					+ redshiftreturnstring.substring(lastIndex + 1);
		}
	//	System.out.println("string  = " + redshiftreturnstring);
	//	System.out.println("numberofchunks  = " + numberofchunks);

		if (bad_data) {
			System.out.println("errors: ");
			for (Map.Entry<Integer, String> entry : reshift_ErrorMap.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error index: " + mkey);
				System.out.println("Error Message: " + mvalue);
			}

		}

		 outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());
	}

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

	}

	public String checkValid(JsonArray redshiftrow) {
		String inputdata = null;
		String notvalid = "notvalid";
		if (redshiftrow != null && redshiftrow.size() > 0) {
			JsonElement element = redshiftrow.get(0);
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
	
	public String formatReturnValue(int statusCode)

	{
		StringBuffer redshiftreturndata = new StringBuffer();

		String errormsg = "\"Error in UDF \"";
		redshiftreturndata.append("{ \"success\":");
		redshiftreturndata.append(false);
		redshiftreturndata.append(" \"num_records\":");
		redshiftreturndata.append(0);
		redshiftreturndata.append(",");
		redshiftreturndata.append(" \"error_msg\":");
		redshiftreturndata.append(errormsg);
		redshiftreturndata.append(",");
		redshiftreturndata.append(" \"results\": [] }");

		return redshiftreturndata.toString();
	}

}