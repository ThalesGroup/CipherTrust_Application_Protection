package com.example;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import java.io.BufferedWriter;
import java.util.HashMap;
import java.util.Map;

public class ThalesGCPBigQueryCRDPBulkFPE implements HttpFunction {
//  @Override
	/*
	 * This test app to test the logic for a BigQuery Database User Defined Function(UDF). It is an example of how to
	 * use Thales Cipher REST Data Protection (CRDP) to protect sensitive data in a column. This example uses Format
	 * Preserve Encryption (FPE) to maintain the original format of the data so applications or business intelligence
	 * tools do not have to change in order to use these columns. This example uses the bulk API.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts. Not production ready code. Was
	 * tested with CM 2.14 & CRDP 1.0 tech preview For more information on CRDP see link below.
	 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */

	private static final Gson gson = new Gson();

	private static final String BADDATATAG = new String("9999999999999999");
	private static int BATCHLIMIT = 10000;

	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	public void service(HttpRequest request, HttpResponse response) throws Exception {

		Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();

		boolean bad_data = false;
		JsonObject result = new JsonObject();
		JsonArray replies = new JsonArray();

		int error_count = 0;
		String encdata = "";

		// The following must be entered in as environment variables in the GCP Cloud
		// Function.
		// CM User and CM Password. These can also be provided as secrets in GCP as
		// well.
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		String crdpip = System.getenv("CRDPIP");
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

		String keymetadatalocation = null;
		String external_version_from_ext_source = null;

		String mode = null;
		String datatype = null;

		// How many records in a chunk. Testing has indicated point of diminishing
		// returns at 100 or 200, but
		// may vary depending on size of data.
		int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
		int numberofchunks = 0;
		JsonArray bigquerydata = null;
		String formattedString = null;
		String notvalid = "notvalid";

		StringBuffer protection_policy_buff = new StringBuffer();

		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		JsonObject requestJson = null;
		int numberOfLines = 0;
		String protection_profile = null;
		String inputDataKey = null;
		String outputDataKey = null;
		String protectedData = null;
		String externalkeymetadata = null;
		String jsonBody = null;
		String jsonTagForProtectReveal = null;

		try {

			if (usersetlookupbool) {
				// make sure cmuser is in Application Data Protection Clients Group

				boolean founduserinuserset = findUserInUserSet(bigquerysessionUser, userName, password, usersetID,
						userSetLookupIP);
				// System.out.println("Found User " + founduserinuserset);
				if (!founduserinuserset)
					throw new CustomException("1001, User Not in User Set", 1001);

			} else {
				usersetlookupbool = false;
			}

			try {
				JsonElement requestParsed = gson.fromJson(request.getReader(), JsonElement.class);

				if (requestParsed != null && requestParsed.isJsonObject()) {
					requestJson = requestParsed.getAsJsonObject();
				}

				if (requestJson != null && requestJson.has("sessionUser")) {
					bigquerysessionUser = requestJson.get("sessionUser").getAsString();
					// System.out.println("name " + bigquerysessionUser);
				}

				if (requestJson != null && requestJson.has("userDefinedContext")) {
					bigqueryuserDefinedContext = requestJson.get("userDefinedContext");
					// System.out.println("userDefinedContext " + bigqueryuserDefinedContext);
					JsonObject location = requestJson.getAsJsonObject("userDefinedContext");
					mode = location.get("mode").getAsString();
					protection_profile = location.get("protection_profile").getAsString();
					datatype = location.get("datatype").getAsString();
					keymetadatalocation = location.get("keymetadatalocation").getAsString();
					if (keymetadatalocation.equalsIgnoreCase("external") && mode.equalsIgnoreCase("revealbulk")) {
						external_version_from_ext_source = location.get("keymetadata").getAsString();
					}

				}

			} catch (JsonParseException e) {
				System.out.println("Error parsing JSON: " + e.getMessage());
			}

			String showrevealkey = "yes";

			if (mode.equals("protectbulk")) {
				inputDataKey = "data_array";
				outputDataKey = "protected_data_array";
				jsonTagForProtectReveal = PROTECTRETURNTAG;
				if (keymetadatalocation.equalsIgnoreCase("internal")) {
					showrevealkey = System.getenv("showrevealinternalkey");
					if (showrevealkey == null)
						showrevealkey = "yes";
				}
			} else {
				inputDataKey = "protected_data_array";
				outputDataKey = "data_array";
				jsonTagForProtectReveal = REVEALRETURNTAG;
			}

			boolean showrevealkeybool = showrevealkey.equalsIgnoreCase("yes");

			bigquerydata = requestJson.getAsJsonArray("calls");

			numberOfLines = bigquerydata.size();
			int totalRowsLeft = numberOfLines;

			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			// Serialization

			int i = 0;
			int count = 0;
			int totalcount = 0;
			boolean newchunk = true;
			int dataIndex = 0;
			int specIndex = 0;
			JsonObject crdp_payload = new JsonObject();

			JsonArray crdp_payload_array = new JsonArray();

			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");
			String urlStr = "http://" + crdpip + ":8090/v1/" + mode;

			while (i < numberOfLines) {

				String sensitive = null;
				JsonArray bigqueryrow = bigquerydata.get(i).getAsJsonArray();

				// insert new....
				sensitive = checkValid(bigqueryrow);

				protection_profile = protection_profile.trim();
				// Format the output
				String formattedElement = String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
				protection_policy_buff.append(formattedElement);
				protection_policy_buff.append(",");

				if (mode.equals("protectbulk")) {
					if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
						if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
							if (sensitive.contains("notvalid")) {
								// System.out.println("adding null not charint or nbr");
								sensitive = sensitive.replace("notvalid", "");
								sensitive = BADDATATAG + sensitive;
							} else
								sensitive = BADDATATAG;

						} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {

						} else if (sensitive.contains("notvalid")) {
							// sensitive = sensitive.replace("notvalid", "");

						}
						encdata = sensitive;

					}
					crdp_payload_array.add(sensitive);
				} else {
					JsonObject protectedDataObject = new JsonObject();
					protectedDataObject.addProperty("protected_data", sensitive);
					if (keymetadatalocation.equalsIgnoreCase("external")) {
						protectedDataObject.addProperty("external_version", external_version_from_ext_source);
					}
					crdp_payload_array.add(protectedDataObject);

				}

				if (count == batchsize - 1) {
					crdp_payload.add(inputDataKey, crdp_payload_array);
					String inputdataarray = null;
					if (mode.equals("revealbulk")) {
						crdp_payload.addProperty("username", bigquerysessionUser);
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

					RequestBody body = RequestBody.create(mediaType, jsonBody);

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

						String status = jsonObject.get("status").getAsString();
						int success_count = jsonObject.get("success_count").getAsInt();
						error_count = jsonObject.get("error_count").getAsInt();
						if (error_count > 0)
							System.out.println("errors " + error_count);
						for (JsonElement element : protectedDataArray) {

							JsonObject protectedDataObject = element.getAsJsonObject();
							if (protectedDataObject.has(jsonTagForProtectReveal)) {

								protectedData = protectedDataObject.get(jsonTagForProtectReveal).getAsString();

								if (keymetadatalocation.equalsIgnoreCase("internal")
										&& mode.equalsIgnoreCase("protectbulk") && !showrevealkeybool) {
									if (protectedData.length() > 7)
										protectedData = protectedData.substring(7);
								}

								replies.add(new String(protectedData));

								if (mode.equals("protectbulk")) {
									if (keymetadatalocation.equalsIgnoreCase("external")
											&& mode.equalsIgnoreCase("protectbulk")) {
										externalkeymetadata = protectedDataObject.get("external_version").getAsString();
										// System.out.println("Protected Data ext key metadata need to store this: "
										// + externalkeymetadata);

									}
								}
							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								bqErrorMap.put(i, errorMessage);
								bad_data = true;
							} else
								System.out.println("unexpected json value from results: ");
							dataIndex++;

						}

						crdp_response.close();
						crdp_payload_array = new JsonArray();
						protection_policy_buff = new StringBuffer();
						numberofchunks++;
						totalcount = totalcount + count;
						count = 0;
					} else {
						System.err.println("Request failed with status code: " + crdp_response.code());
					}

				} else {
					count++;
				}
				totalRowsLeft--;
				i++;

			}

			if (count > 0) {
				crdp_payload.add(inputDataKey, crdp_payload_array);
				String inputdataarray = null;
				if (mode.equals("revealbulk")) {
					crdp_payload.addProperty("username", bigquerysessionUser);
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

				RequestBody body = RequestBody.create(mediaType, jsonBody);

				Request crdp_request = new Request.Builder().url(urlStr).method("POST", body)
						.addHeader("Content-Type", "application/json").build();
				Response crdp_response = client.newCall(crdp_request).execute();
				String crdpreturnstr = null;
				if (crdp_response.isSuccessful()) {
					// Parse JSON response
					String responseBody = crdp_response.body().string();
					JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
					JsonArray protectedDataArray = jsonObject.getAsJsonArray(outputDataKey);

					String status = jsonObject.get("status").getAsString();
					int success_count = jsonObject.get("success_count").getAsInt();
					error_count = jsonObject.get("error_count").getAsInt();
					if (error_count > 0)
						System.out.println("errors " + error_count);
					for (JsonElement element : protectedDataArray) {

						JsonObject protectedDataObject = element.getAsJsonObject();
						if (protectedDataObject.has(jsonTagForProtectReveal)) {

							protectedData = protectedDataObject.get(jsonTagForProtectReveal).getAsString();

							if (keymetadatalocation.equalsIgnoreCase("internal") && mode.equalsIgnoreCase("protectbulk")
									&& !showrevealkeybool) {
								if (protectedData.length() > 7)
									protectedData = protectedData.substring(7);
							}

							replies.add(new String(protectedData));

							if (mode.equals("protectbulk")) {
								if (keymetadatalocation.equalsIgnoreCase("external")) {
									externalkeymetadata = protectedDataObject.get("external_version").getAsString();
									// System.out.println("Protected Data ext key metadata need to store this: "
									// + externalkeymetadata);

								}
							}
						} else if (protectedDataObject.has("error_message")) {
							String errorMessage = protectedDataObject.get("error_message").getAsString();
							System.out.println("error_message: " + errorMessage);
							bqErrorMap.put(i, errorMessage);
							bad_data = true;
						} else
							System.out.println("unexpected json value from results: ");
						dataIndex++;

					}

					crdp_response.close();
					crdp_payload_array = new JsonArray();
					protection_policy_buff = new StringBuffer();
					numberofchunks++;
					totalcount = totalcount + count;
					count = 0;
				} else {
					System.err.println("Request failed with status code: " + crdp_response.code());
				}
			}
			System.out.println("total chuncks " + numberofchunks);

			result.add("replies", replies);
			formattedString = result.toString();

		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					result = new JsonObject();
					replies = new JsonArray();
					for (int i = 0; i < bigquerydata.size(); i++) {
						JsonArray innerArray = bigquerydata.get(i).getAsJsonArray();
						replies.add(innerArray.get(0).getAsString());
					}
					result.add("replies", replies);
					formattedString = result.toString();

				} else {

					e.printStackTrace(System.out);
					response.setStatusCode(500);
					BufferedWriter writer = response.getWriter();
					writer.write("Internal Server Error Review logs for details");

				}

			} else {

				e.printStackTrace(System.out);
				response.setStatusCode(500);
				BufferedWriter writer = response.getWriter();
				writer.write("Internal Server Error Review logs for details");

			}

		} finally {

		}
		if (bad_data) {
			System.out.println("errors: ");
			for (Map.Entry<Integer, String> entry : bqErrorMap.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error index: " + mkey);
				System.out.println("Error Message: " + mvalue);
			}

		}

		response.getWriter().write(formattedString);
	}

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

	}

	public String checkValid(JsonArray bigquerytrow) {
		String inputdata = null;
		String notvalid = "notvalid";
		if (bigquerytrow != null && bigquerytrow.size() > 0) {
			JsonElement element = bigquerytrow.get(0);
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

	public static String formatString(String inputString) {
		// Split the input string to isolate the array content
		String[] parts = inputString.split("\\[")[1].split("\\]")[0].split(",");

		// Reformat the array elements to enclose them within double quotes
		StringBuilder formattedArray = new StringBuilder();
		for (String part : parts) {
			formattedArray.append("\"").append(part.trim()).append("\",");
		}

		// Build the final formatted string
		return inputString.replaceFirst("\\[.*?\\]",
				"[" + formattedArray.deleteCharAt(formattedArray.length() - 1) + "]");
	}

}