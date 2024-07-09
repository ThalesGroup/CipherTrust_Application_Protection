
import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class TestThalesGCPBigQueryCRDPBulkFPE implements HttpFunction {
//  @Override
	/*
	 * This test app to test the logic for a BigQuery Database User Defined
	 * Function(UDF). It is an example of how to use Thales Cipher REST Data
	 * Protection (CRDP) to protect sensitive data in a column. This example uses
	 * Format Preserve Encryption (FPE) to maintain the original format of the data
	 * so applications or business intelligence tools do not have to change in order
	 * to use these columns. There is no need to deploy a function to run it. This
	 * example uses the bulk API.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts.
	 * Not production ready code. Was tested with CM 2.14 & CRDP 1.0 For more
	 * information on CRDP see link below.
	 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */

	private static final Gson gson = new Gson();

	private static int BATCHLIMIT = 10000;

	public static void main(String[] args) throws Exception

	{
		TestThalesGCPBigQueryCRDPBulkFPE nw2 = new TestThalesGCPBigQueryCRDPBulkFPE();

		String requestprotectinternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"protectbulk\",\r\n" + "    \"protection_profile\": \"plain-alpha-internal\"\r\n"
				+ "  },\r\n" + "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n"
				+ "    [\r\n" + "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"David Cullen\"\r\n"
				+ "    ]\r\n" + "  ]\r\n" + "}";

		String requestprotectexternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"protectbulk\",\r\n" + "    \"protection_profile\": \"alpha-external\"\r\n"
				+ "  },\r\n" + "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n"
				+ "    [\r\n" + "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"David Cullen\"\r\n"
				+ "    ]\r\n" + "  ]\r\n" + "}";
		
		String requestprotectexternalnull = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"protectbulk\",\r\n" + "    \"protection_profile\": \"alpha-external\"\r\n"
				+ "  },\r\n" + "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n"
				+ "    [\r\n" + "      \"\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"null\"\r\n"
				+ "    ]\r\n" + "  ]\r\n" + "}";
		

		String revealinternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"revealbulk\",\r\n" + "    \"protection_profile\": \"plain-alpha-internal\"\r\n"
				+ "  },\r\n" + "  \"calls\": [\r\n" + "    [\r\n" + "      \"100400120ep 3rbGWH\"\r\n" + "    ],\r\n"
				+ "    [\r\n" + "      \"1004001xeBv udb4N\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"1004001r2ZQh UPd3Am\"\r\n" + "    ]\r\n" + "  ]\r\n" + "}";

		String revealexternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"revealbulk\",\r\n" + "    \"protection_profile\": \"alpha-external\"\r\n"
				+ "  },\r\n" + "  \"calls\": [\r\n" + "    [\r\n" + "      \"BSTCa CrcLKT\"\r\n" + "    ],\r\n"
				+ "    [\r\n" + "      \"3bvF qWMiyk\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"AFud mVfPi\"\r\n"
				+ "    ]\r\n" + "  ]\r\n" + "}";

		String revealexternalnull = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"revealbulk\",\r\n" + "    \"protection_profile\": \"alpha-external\"\r\n"
				+ "  },\r\n" + "  \"calls\": [\r\n" + "    [\r\n" + "      \"BSTCa CrcLKT\"\r\n" + "    ],\r\n"
				+ "    [\r\n" + "      \"wugVwf0C\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"qRbZ\"\r\n"
				+ "    ]\r\n" + "  ]\r\n" + "}";
		
		String response = null;
		nw2.service(revealexternalnull, response);

	}

	public void service(String request, String response) throws Exception {

		Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();

		boolean bad_data = false;
		int error_count = 0;
		String encdata = "";

		// The following must be entered in as environment variables in the GCP Cloud
		// Function.
		// CM User and CM Password. These can also be provided as secrets in GCP as
		// well.
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		String crdpip = System.getenv("CRDPIP");
		// returnciphertextforuserwithnokeyaccess = is a environment variable to express
		// how data should be returned when the user above does not have access to the
		// key and if doing a
		// lookup in the userset
		// and the user does not exist. If returnciphertextforuserwithnokeyaccess = null
		// then an error will be returned to the query, else the results set will
		// provide ciphertext.
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");
		// usersetlookup = should a userset lookup be done on the user from Big Query?  
		// yes,no
		String usersetlookup = System.getenv("usersetlookup");
		// usersetID = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it
		// is
		// the userset in CM but could be a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");
		String keymetadatalocation = System.getenv("keymetadatalocation");
		String external_version_from_ext_source = System.getenv("keymetadata");
		// How many records in a chunk. Testing has indicated point of diminishing
		// returns at 100 or 200, but
		// may vary depending on size of data.
		// int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
		int numberofchunks = 0;
		JsonArray bigquerydata = null;
		String formattedString = null;
		String notvalid = "notvalid";
		StringBuffer bigqueryreturndatasc = new StringBuffer();
		StringBuffer protection_policy_buff = new StringBuffer();
		String bigqueryreturnstring = null;
		StringBuffer bigqueryreturndata = new StringBuffer();

		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		String mode = null;
		String datatype = null;
		JsonObject requestJson = null;
		boolean debug = true;
		int numberOfLines = 0;
		String protection_profile = null;
		String inputDataKey = null;
		String outputDataKey = null;
		String protectedData = null;
		String externalkeymetadata = null;
		String jsonBody = null;

		// long startTime = System.currentTimeMillis();

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
				JsonElement requestParsed = gson.fromJson(request, JsonElement.class);

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
					if (mode.equals("protectbulk")) {
						inputDataKey = "data_array";
						outputDataKey = "protected_data_array";
					} else {
						inputDataKey = "protected_data_array";
						outputDataKey = "data_array";

					}
				}

			} catch (JsonParseException e) {
				System.out.println("Error parsing JSON: " + e.getMessage());
			}

			bigquerydata = requestJson.getAsJsonArray("calls");

			numberOfLines = bigquerydata.size();
			int totalRowsLeft = numberOfLines;

			int batchsize = 3;
			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			// Serialization

			bigqueryreturndata.append("{ \"replies\": [");

			int i = 0;
			int count = 0;
			int totalcount = 0;
			boolean newchunk = true;
			int dataIndex = 0;
			int specIndex = 0;
			JsonObject crdp_payload = new JsonObject();

			JsonArray crdp_payload_array = new JsonArray();

			// crdp_payload.addProperty("protection_policy_name", protection_profile);

			while (i < numberOfLines) {

				if (newchunk) {
					crdp_payload_array = new JsonArray();
					protection_policy_buff = new StringBuffer();
					newchunk = false;
					count = 0;
				}

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
					crdp_payload_array.add(sensitive);
				} else {
					JsonObject protectedDataObject = new JsonObject();
					protectedDataObject.addProperty("protected_data", sensitive);
					if (keymetadatalocation.equalsIgnoreCase("external")) {
						protectedDataObject.addProperty("external_version", external_version_from_ext_source);
					}
					crdp_payload_array.add(protectedDataObject);
					System.out.println(gson.toJson(crdp_payload_array));
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

					OkHttpClient client = new OkHttpClient().newBuilder().build();
					MediaType mediaType = MediaType.parse("application/json");

					System.out.println(jsonBody);
					RequestBody body = RequestBody.create(mediaType, jsonBody);
					String urlStr = "http://" + crdpip + ":8090/v1/" + mode;
					// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
					System.out.println(urlStr);
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
						System.out.println("errors " + error_count);

						if (mode.equals("protectbulk")) {

							for (JsonElement element : protectedDataArray) {
								JsonObject protectedDataObject = element.getAsJsonObject();
								if (protectedDataObject.has("protected_data")) {

									protectedData = protectedDataObject.get("protected_data").getAsString();
									System.out.println(protectedData);
									// add to
									bigqueryreturndatasc.append(new String(protectedData));
									bigqueryreturndatasc.append(",");
									if (keymetadatalocation.equalsIgnoreCase("external")) {
										externalkeymetadata = protectedDataObject.get("external_version").getAsString();
										System.out.println("Protected Data ext key metadata need to store this: "
												+ externalkeymetadata);

									}
								} else if (protectedDataObject.has("error_message")) {
									String errorMessage = protectedDataObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									bqErrorMap.put(i, errorMessage);
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
									System.out.println(protectedData);
									bigqueryreturndatasc.append(new String(protectedData));
									bigqueryreturndatasc.append(",");
								} else if (protectedDataObject.has("error_message")) {
									String errorMessage = protectedDataObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									bqErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");

							}
						}

						crdp_response.close();

						numberofchunks++;
						newchunk = true;
						totalcount = totalcount + count;
						count = 0;
						dataIndex = 0;
						specIndex = 0;
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

				OkHttpClient client = new OkHttpClient().newBuilder().build();
				MediaType mediaType = MediaType.parse("application/json");

				System.out.println(jsonBody);
				RequestBody body = RequestBody.create(mediaType, jsonBody);
				String urlStr = "http://" + crdpip + ":8090/v1/" + mode;
				// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
				System.out.println(urlStr);
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
					System.out.println("errors " + error_count);

					if (mode.equals("protectbulk")) {

						for (JsonElement element : protectedDataArray) {
							JsonObject protectedDataObject = element.getAsJsonObject();
							if (protectedDataObject.has("protected_data")) {

								protectedData = protectedDataObject.get("protected_data").getAsString();
								System.out.println(protectedData);
								// add to
								bigqueryreturndatasc.append(new String(protectedData));
								bigqueryreturndatasc.append(",");
								if (keymetadatalocation.equalsIgnoreCase("external")) {
									externalkeymetadata = protectedDataObject.get("external_version").getAsString();
									System.out.println("Protected Data ext key metadata need to store this: "
											+ externalkeymetadata);

								}
							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								bqErrorMap.put(i, errorMessage);
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
								System.out.println(protectedData);
								bigqueryreturndatasc.append(new String(protectedData));
								bigqueryreturndatasc.append(",");
							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								bqErrorMap.put(i, errorMessage);
								bad_data = true;
							} else
								System.out.println("unexpected json value from results: ");

						}
					}

					crdp_response.close();

					numberofchunks++;
					newchunk = true;
					totalcount = totalcount + count;
					count = 0;
					dataIndex = 0;
					specIndex = 0;
				} else {
					System.err.println("Request failed with status code: " + crdp_response.code());
				}
			}
			System.out.println("total chuncks " + numberofchunks);

			bigqueryreturndatasc.append("] }");
			bigqueryreturndata.append(bigqueryreturndatasc);
			bigqueryreturnstring = new String(bigqueryreturndata);
			formattedString = formatString(bigqueryreturnstring);

		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					JsonObject result = new JsonObject();
					JsonArray replies = new JsonArray();
					for (int i = 0; i < bigquerydata.size(); i++) {
						JsonArray innerArray = bigquerydata.get(i).getAsJsonArray();
						replies.add(innerArray.get(0).getAsString());
					}
					result.add("replies", replies);
					formattedString = result.toString();

				} else {

					e.printStackTrace(System.out);
					// response.setStatusCode(500);
					// BufferedWriter writer = response.getWriter();
					// writer.write("Internal Server Error Review logs for details");

				}

			} else {

				e.printStackTrace(System.out);
				// response.setStatusCode(500);
				// BufferedWriter writer = response.getWriter();
				// writer.write("Internal Server Error Review logs for details");

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
		System.out.println(formattedString);
		// response.getWriter().write(formattedString);
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

	@Override
	public void service(HttpRequest request, HttpResponse response) throws Exception {
		// TODO Auto-generated method stub

	}

}