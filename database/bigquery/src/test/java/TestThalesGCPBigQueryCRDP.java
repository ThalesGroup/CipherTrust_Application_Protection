
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

public class TestThalesGCPBigQueryCRDP implements HttpFunction {
//  @Override
	/*
	 * This test app to test the logic for a BigQuery Database User Defined Function(UDF). It is an example of how to
	 * use Thales Cipher REST Data Protection (CRDP) to protect sensitive data in a column. This example uses Format
	 * Preserve Encryption (FPE) to maintain the original format of the data so applications or business intelligence
	 * tools do not have to change in order to use these columns. There is no need to deploy a function to run it.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts. Not production ready code. Was
	 * tested with CM 2.14 & CRDP 1.0 For more information on CRDP see link below.
	 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */

	private static final Gson gson = new Gson();
	private static final String BADDATATAG = new String("9999999999999999");

	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	public static void main(String[] args) throws Exception

	{
		TestThalesGCPBigQueryCRDP nw2 = new TestThalesGCPBigQueryCRDP();

		String requestprotectnbrinternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"datatype\": \"charint\",\r\n" + "    \"mode\": \"protect\",\r\n"
				+ "    \"protection_profile\": \"plain-nbr-internal\",\r\n"
				+ "    \"keymetadatalocation\": \"internal\",\r\n" + "    \"keymetadata\": \"1001001\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"5678234\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"24\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"5\"\r\n" + "    ]\r\n" + "  ]\r\n" + "}";

		String requestprotectnbrinternal_reveal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"datatype\": \"charint\",\r\n" + "    \"mode\": \"reveal\",\r\n"
				+ "    \"protection_profile\": \"plain-nbr-internal\",\r\n"
				+ "    \"keymetadatalocation\": \"internal\",\r\n" + "    \"keymetadata\": \"1001001\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"10010012159021\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"100100102\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"5\"\r\n" + "    ]\r\n" + "  ]\r\n"
				+ "}";

		String requestprotectinternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"datatype\": \"char\",\r\n" + "    \"mode\": \"protect\",\r\n"
				+ "    \"protection_profile\": \"plain-alpha-internal\",\r\n"
				+ "    \"keymetadatalocation\": \"internal\",\r\n" + "    \"keymetadata\": \"1001001\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"David Cullen\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";

		String requestprotectexternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"datatype\": \"char\",\r\n" + "    \"mode\": \"protect\",\r\n"
				+ "    \"protection_profile\": \"alpha-external\",\r\n"
				+ "    \"keymetadatalocation\": \"external\",\r\n" + "    \"keymetadata\": \"1001001\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"null\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";

		String revealinternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"datatype\": \"char\",\r\n" + "    \"mode\": \"reveal\",\r\n"
				+ "    \"protection_profile\": \"plain-alpha-internal\",\r\n"
				+ "    \"keymetadatalocation\": \"internal\",\r\n" + "    \"keymetadata\": \"1001001\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"100400120ep 3rbGWH\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"1004001xeBv udb4N\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"1004001r2ZQh UPd3Am\"\r\n"
				+ "    ]\r\n" + "  ]\r\n" + "}";

		String revealexternal = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"datatype\": \"char\",\r\n" + "    \"mode\": \"reveal\",\r\n"
				+ "    \"protection_profile\": \"alpha-external\",\r\n"
				+ "    \"keymetadatalocation\": \"external\",\r\n" + "    \"keymetadata\": \"1001001\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"BSTCa CrcLKT\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"3bvF qWMiyk\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"AFud mVfPi\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";

		String response = null;
		nw2.service(requestprotectnbrinternal_reveal, response);

	}

	public void service(String request, String response) throws Exception {
		Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();
		String encdata = "";
		// The following must be entered in as environment variables in the GCP Cloud
		// Function.
		// CM User and CM Password. These can also be provided as secrets in GCP as
		// well.
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

		String keymetadatalocation = null;
		String external_version_from_ext_source = null;
		String datatype = null;
		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		String mode = null;
		String protection_profile = null;
		String dataKey = null;
		String formattedString = null;
		JsonArray bigquerydata = null;
		boolean bad_data = false;
		JsonObject result = new JsonObject();
		JsonArray replies = new JsonArray();
		int nbrofrows = 0;

		try {

			// Parse JSON request and check for "name" field
			JsonObject requestJson = null;
			String jsonTagForProtectReveal = null;

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
					JsonObject location = requestJson.getAsJsonObject("userDefinedContext");
					mode = location.get("mode").getAsString();
					protection_profile = location.get("protection_profile").getAsString();
					datatype = location.get("datatype").getAsString();
					keymetadatalocation = location.get("keymetadatalocation").getAsString();
					if (keymetadatalocation.equalsIgnoreCase("external") && mode.equalsIgnoreCase("reveal")) {
						external_version_from_ext_source = location.get("keymetadata").getAsString();
					}
				}

			} catch (JsonParseException e) {

				System.out.println(e.getMessage());
			}
			bigquerydata = requestJson.getAsJsonArray("calls");

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

			for (int i = 0; i < nbrofrows; i++) {

				JsonArray bigquerytrow = bigquerydata.get(i).getAsJsonArray();

				sensitive = checkValid(bigquerytrow);

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
						crdp_payload.addProperty("username", bigquerysessionUser);
						if (keymetadatalocation.equalsIgnoreCase("external")) {
							crdp_payload.addProperty("external_version", external_version_from_ext_source);
						}
					}
					crdpjsonBody = crdp_payload.toString();
					System.out.println(crdpjsonBody);
					RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

					// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
					System.out.println(urlStr);
					Request crdp_request = new Request.Builder()
							// .url("http://192.168.159.143:8090/v1/protect").method("POST", body)
							.url(urlStr).method("POST", body).addHeader("Content-Type", "application/json").build();
					Response crdp_response = client.newCall(crdp_request).execute();

					if (crdp_response.isSuccessful()) {

						// Parse JSON response
						String responseBody = crdp_response.body().string();
						Gson gson = new Gson();
						JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);

						if (jsonObject.has(jsonTagForProtectReveal)) {
							protectedData = jsonObject.get(jsonTagForProtectReveal).getAsString();
							if (keymetadatalocation.equalsIgnoreCase("external") && mode.equalsIgnoreCase("protect")) {
								externalkeymetadata = jsonObject.get("external_version").getAsString();
								System.out.println(
										"Protected Data ext key metadata need to store this: " + externalkeymetadata);
							}

							if (keymetadatalocation.equalsIgnoreCase("internal") && mode.equalsIgnoreCase("protect")
									&& !showrevealkeybool) {
								if (protectedData.length() > 7)
									protectedData = protectedData.substring(7);
							}

						} else if (jsonObject.has("error_message")) {
							String errorMessage = jsonObject.get("error_message").getAsString();
							System.out.println("error_message: " + errorMessage);
							bqErrorMap.put(i, errorMessage);
							bad_data = true;
						} else
							System.out.println("unexpected json value from results: ");

						System.out.println("Protected Data: " + protectedData);

					} else {
						System.err.println("Request failed with status code: " + crdp_response.code());
					}

					crdp_response.close();
//		String showrevealkey = System.getenv("showrevealinternalkey");

					encdata = protectedData;

				}
				replies.add(encdata);
			} // end for loop

			result.add("replies", replies);
			formattedString = result.toString();

		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					result = new JsonObject();
					replies = new JsonArray();
					if (bigquerydata != null) {
						for (int i = 0; i < bigquerydata.size(); i++) {
							JsonArray innerArray = bigquerydata.get(i).getAsJsonArray();
							replies.add(innerArray.get(0).getAsString());
						}
						result.add("replies", replies);
						formattedString = result.toString();
					} else {
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
			} else {
				e.printStackTrace(System.out);
				// response.setStatusCode(500);
				// BufferedWriter writer = response.getWriter();
				// writer.write("Internal Server Error Review logs for details");
			}
		} finally

		{

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

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

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