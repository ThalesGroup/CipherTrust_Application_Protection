package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.io.IOUtils;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.common.util.concurrent.RateLimiter;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;


/*
 * This is an example of how to use Thales Cipher REST Data Protection (CRDP)
 * to protect sensitive data in a column in a AWS Redshift DB. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns.
 * 
 * Note: This source code is only to be used for testing and proof of concepts.
 * Not production ready code. Was tested with CM 2.14 &
 * CRDP 1.0 tech preview For more information on CRDP see link below.
 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
 * 
 * @author mwarner
 * 
 */

public class ThalesAWSRedshiftCRDPCharFPERLRetry implements RequestStreamHandler {

	private static final Gson gson = new Gson();
	private static final int MAX_RETRIES = 3;
	// private static final double REQUESTS_PER_SECOND = 5.0; // Adjust this rate as
	// needed
	  private static final double REQUESTS_PER_SECOND = 10.0; // Adjust this rate as needed

	private static final RateLimiter rateLimiter = RateLimiter.create(REQUESTS_PER_SECOND);

	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context)
			throws IOException {
		rateLimiter.acquire(); // Acquire a permit from the rate limiter
		Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();
		String input = IOUtils.toString(inputStream, "UTF-8");
		JsonParser parser = new JsonParser();
 
		int statusCode = 200;

		String encdata = "";
		String redshiftreturnstring = null;
		String sensitive = null;

		StringBuffer redshiftreturndata = new StringBuffer();

		boolean status = true;

		JsonObject redshiftinput = null;
		JsonElement rootNode = parser.parse(input);
		JsonArray redshiftdata = null;
		String redshiftuserstr = null;

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
 
		String dataKey = null;
		String protectedData = null;
		String externalkeymetadata = null;
		String crdpjsonBody = null;
		boolean bad_data = false;

		// String external_version_from_ext_source = "1004001";
		// String external_version_from_ext_source = "1001001";

		JsonObject crdp_payload = new JsonObject();

		crdp_payload.addProperty("protection_policy_name", protection_profile);

		if (mode.equals("protect"))
			dataKey = "data";
		else
			dataKey = "protected_data";

		int attempt = 0;
		boolean success = false;

		while (attempt < MAX_RETRIES && !success) {
			try {
				redshiftreturndata.append("{ \"success\":");
				redshiftreturndata.append(status);
				redshiftreturndata.append(",");
				redshiftreturndata.append(" \"num_records\":");
				redshiftreturndata.append(nbr_of_rows_json_int);
				redshiftreturndata.append(",");
				redshiftreturndata.append(" \"results\": [");

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

				for (int i = 0; i < redshiftdata.size(); i++) {
					JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

					sensitive = checkValid(redshiftrow);
					if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
						System.out.println("not valid or null");
						encdata = sensitive;
					} else {

						OkHttpClient client = new OkHttpClient().newBuilder().build();
						MediaType mediaType = MediaType.parse("application/json");
						crdp_payload.addProperty(dataKey, sensitive);
						if (mode.equals("reveal")) {
							crdp_payload.addProperty("username", redshiftuserstr);
							if (keymetadatalocation.equalsIgnoreCase("external")) {
								crdp_payload.addProperty("external_version", external_version_from_ext_source);
							}
						}
						crdpjsonBody = crdp_payload.toString();
						//System.out.println(crdpjsonBody);
						RequestBody body = RequestBody.create(mediaType, crdpjsonBody);
						String urlStr = "http://" + crdpip + ":8090/v1/" + mode;
						// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
						//System.out.println(urlStr);
						Request crdp_request = new Request.Builder()
								// .url("http://192.168.159.143:8090/v1/protect").method("POST", body)
								.url(urlStr).method("POST", body).addHeader("Content-Type", "application/json").build();
						Response crdp_response = client.newCall(crdp_request).execute();

						if (crdp_response.isSuccessful()) {

							// Parse JSON response
							String responseBody = crdp_response.body().string();
							Gson gson = new Gson();
							JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);

							if (mode.equals("protect")) {
								if (jsonObject.has("protected_data")) {
									protectedData = jsonObject.get("protected_data").getAsString();
									if (keymetadatalocation.equalsIgnoreCase("external")) {
										externalkeymetadata = jsonObject.get("external_version").getAsString();
										//System.out.println("Protected Data ext key metadata need to store this: "
										//		+ externalkeymetadata);
									}
								} else if (jsonObject.has("error_message")) {
									String errorMessage = jsonObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									bqErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");

							}

							else if (jsonObject.has("data")) {
								protectedData = jsonObject.get("data").getAsString();
							//	System.out.println("Protected Data: " + protectedData);
							} else if (jsonObject.has("error_message")) {
								String errorMessage = jsonObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								bqErrorMap.put(i, errorMessage);
								bad_data = true;
							} else
								System.out.println("unexpected json value from results: ");
						} else {
							System.err.println("Request failed with status code: " + crdp_response.code());
						}

						crdp_response.close();

						encdata = protectedData;
					}

					encdata = "\"" + encdata + "\"";
					redshiftreturndata.append(encdata);
					if (redshiftdata.size() != 1 && i != redshiftdata.size() - 1) {
						redshiftreturndata.append(",");
					}
				} // for
				redshiftreturndata.append("]}");
				redshiftreturnstring = new String(redshiftreturndata);

				success = true; // Mark success if no exceptions occurred
			} catch (Exception e) {
				attempt++;
				if (attempt >= MAX_RETRIES) {
					handleException(e, redshiftreturndata, redshiftdata, returnciphertextbool);
					redshiftreturnstring = new String(redshiftreturndata);
					statusCode = 400;
				} else {
					System.out.println("Attempt " + attempt + " failed, retrying...");
				}
			} finally {

			}
		}
		success = true;
		
		if (bad_data) {
			System.out.println("errors: ");
			for (Map.Entry<Integer, String> entry : bqErrorMap.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error index: " + mkey);
				System.out.println("Error Message: " + mvalue);
			}

		}
		
		//System.out.println(redshiftreturnstring);
		outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());
	}

	private void handleException(Exception e, StringBuffer redshiftreturndata, JsonArray redshiftdata,
			boolean returnciphertextbool) {
		String sensitive = null;
		if (returnciphertextbool) {
			if (e.getMessage().contains("1401") || e.getMessage().contains("1001") || e.getMessage().contains("1002")) {
				for (int i = 0; i < redshiftdata.size(); i++) {
					JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();
					if (redshiftrow != null && redshiftrow.size() > 0) {
						JsonElement element = redshiftrow.get(0);
						if (element != null && !element.isJsonNull()) {
							sensitive = element.getAsString();
							if (sensitive.isEmpty()) {
								JsonElement elementforNull = new JsonPrimitive("null");
								sensitive = elementforNull.getAsJsonPrimitive().toString();
							} else {
								sensitive = element.getAsJsonPrimitive().toString();
							}
						} else {
							JsonElement elementforNull = new JsonPrimitive("null");
							sensitive = elementforNull.getAsJsonPrimitive().toString();
						}
					}
					redshiftreturndata.append(sensitive);
					if (redshiftdata.size() != 1 && i != redshiftdata.size() - 1) {
						redshiftreturndata.append(",");
					}
				}
				redshiftreturndata.append("]}");
			}
		}
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
	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {
		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);
		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);
		return cmuserset.findUserInUserSet(userName, newtoken);
	}

}
