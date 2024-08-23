
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

/*
 * This test app to test the logic for a AWS Redshift Database User Defined
 * Function(UDF). It is an example of how to use Thales Cipher REST Data Protection (CRDP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns. There is no need to deploy a function to run it.
 * 
 * Note: This source code is only to be used for testing and proof of concepts.
 * Not production ready code. Was tested with CM 2.14 &
 * CRDP 1.0 tech preview For more information on CRDP see link below.
 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
 * 
 * @author mwarner
 * 
 */

public class ThalesAWSRedshiftCRDPFPETester implements RequestStreamHandler {
	private static final Logger logger = Logger.getLogger(ThalesAWSRedshiftCRDPFPETester.class.getName());

	private static final String BADDATATAG = new String("9999999999999999");

	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	private static final Gson gson = new Gson();

	public static void main(String[] args) throws Exception {

		ThalesAWSRedshiftCRDPFPETester nw2 = new ThalesAWSRedshiftCRDPFPETester();

		String protect_internal_request = "{\r\n" + "  \"request_id\" : \"23FF1F97-F28A-44AA-AB67-266ED976BF40\",\r\n"
				+ "  \"cluster\" : \"arn:aws:redshift:xxxx\",\r\n" + "  \"user\" : \"adminuser\",\r\n"
				+ "  \"database\" : \"db1\",\r\n" + "  \"external_function\": \"public.foo\",\r\n"
				+ "  \"query_id\" : 5678234,\r\n" + "  \"num_records\" : 5,\r\n" + "  \"arguments\" : [\r\n"
				+ "     [ \"5678234\"],\r\n" + "     [ \"45345366345\"],\r\n" + "     [ \"2342342342424\"],\r\n"
				+ "     [ \"24\"],\r\n" + "     [ \"5\"]\r\n" + "   ]\r\n" + " }";

		String revealrequest_internal = "{\r\n" + "  \"request_id\" : \"23FF1F97-F28A-44AA-AB67-266ED976BF40\",\r\n"
				+ "  \"cluster\" : \"arn:aws:redshift:xxxx\",\r\n" + "  \"user\" : \"admin\",\r\n"
				+ "  \"database\" : \"db1\",\r\n" + "  \"external_function\": \"public.foo\",\r\n"
				+ "  \"query_id\" : 5678234,\r\n" + "  \"num_records\" : 5,\r\n" + "  \"arguments\" : [\r\n"
				+ "     [ \"10010012159021\"],\r\n" + "     [ \"100100163267367633\"],\r\n"
				+ "     [ \"10010014546420247261\"],\r\n" + "     [ \"100100102\"],\r\n"
				+ "     [ \"1004001ly4A5IY1j7QRDti4A2\"]\r\n" + "   ]\r\n" + " }";

		String protectrequest = "{\r\n" + "  \"request_id\" : \"23FF1F97-F28A-44AA-AB67-266ED976BF40\",\r\n"
				+ "  \"cluster\" : \"arn:aws:redshift:xxxx\",\r\n" + "  \"user\" : \"adminuser\",\r\n"
				+ "  \"database\" : \"db1\",\r\n" + "  \"external_function\": \"public.foo\",\r\n"
				+ "  \"query_id\" : 5678234,\r\n" + "  \"num_records\" : 5,\r\n" + "  \"arguments\" : [\r\n"
				+ "     [ \"5678234\"],\r\n" + "     [ \"45345366345\"],\r\n" + "     [ \"2342342342424\"],\r\n"
				+ "     [ \"2424\"],\r\n" + "     [ \"234234234255667777\"]\r\n" + "   ]\r\n" + " }";

		String revealrequest = "{\r\n" + "  \"request_id\" : \"23FF1F97-F28A-44AA-AB67-266ED976BF40\",\r\n"
				+ "  \"cluster\" : \"arn:aws:redshift:xxxx\",\r\n" + "  \"user\" : \"admin\",\r\n"
				+ "  \"database\" : \"db1\",\r\n" + "  \"external_function\": \"public.foo\",\r\n"
				+ "  \"query_id\" : 5678234,\r\n" + "  \"num_records\" : 5,\r\n" + "  \"arguments\" : [\r\n"
				+ "     [ \"1004001jKVC6JO\"],\r\n" + "     [ \"1004001DW9FaQxLPj3\"],\r\n"
				+ "     [ \"1004001rJivEodgILZg8\"],\r\n" + "     [ \"1004001JvcC\"],\r\n"
				+ "     [ \"1004001ly4A5IY1j7QRDti4A2\"]\r\n" + "   ]\r\n" + " }";

		String revealrequest_ext = "{\r\n" + "  \"request_id\" : \"23FF1F97-F28A-44AA-AB67-266ED976BF40\",\r\n"
				+ "  \"cluster\" : \"arn:aws:redshift:xxxx\",\r\n" + "  \"user\" : \"admin\",\r\n"
				+ "  \"database\" : \"db1\",\r\n" + "  \"external_function\": \"public.foo\",\r\n"
				+ "  \"query_id\" : 5678234,\r\n" + "  \"num_records\" : 5,\r\n" + "  \"arguments\" : [\r\n"
				+ "     [ \"LmCJFjr\"],\r\n" + "     [ \"SsoB9Lalcga\"],\r\n" + "     [ \"p2TryIkXAjCLk\"],\r\n"
				+ "     [ \"J5IX\"],\r\n" + "     [ \"cWENACcmC12zWDxNpq\"]\r\n" + "   ]\r\n" + " }";

		String response = null;
		String testJson = null;
		nw2.handleRequest(protect_internal_request, null, null);

	}

	public void handleRequest(String inputStream, String outputStream, Context context)
			throws IOException, CustomException {
		Map<Integer, String> reshift_ErrorMap = new HashMap<Integer, String>();
		// String input = IOUtils.toString(inputStream, "UTF-8");
		JsonParser parser = new JsonParser();

		int statusCode = 200;

		String encdata = "";
		String redshiftreturnstring = null;
		String sensitive = null;

		// StringBuffer redshiftreturndata = new StringBuffer();

		boolean status = true;

		JsonObject redshiftinput = null;
		JsonElement rootNode = parser.parse(inputStream);
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
		;
		String keymetadatalocation = System.getenv("keymetadatalocation");
		String external_version_from_ext_source = System.getenv("keymetadata");
		String protection_profile = System.getenv("protection_profile");
		String mode = System.getenv("mode");
		String datatype = System.getenv("datatype");

		String dataKey = null;
		String protectedData = null;
		String externalkeymetadata = null;
		String crdpjsonBody = null;
		boolean bad_data = false;

		JsonObject result = new JsonObject();
		JsonArray replies = new JsonArray();

		// String external_version_from_ext_source = "1004001";
		// String external_version_from_ext_source = "1001001";

		JsonObject crdp_payload = new JsonObject();

		crdp_payload.addProperty("protection_policy_name", protection_profile);
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

		int nbrofrecords = redshiftdata.size();

		try {

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
			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");
			String urlStr = "http://" + crdpip + ":8090/v1/" + mode;

			for (int i = 0; i < nbrofrecords; i++) {
				JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

				sensitive = checkValid(redshiftrow);
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
						crdp_payload.addProperty("username", redshiftuserstr);
						if (keymetadatalocation.equalsIgnoreCase("external")) {
							crdp_payload.addProperty("external_version", external_version_from_ext_source);
						}
					}
					crdpjsonBody = crdp_payload.toString();

					RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

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
							reshift_ErrorMap.put(i, errorMessage);
							bad_data = true;
						} else
							System.out.println("unexpected json value from results: ");

					} else {
						System.err.println("Request failed with status code: " + crdp_response.code());
					}

					crdp_response.close();

					encdata = protectedData;

				}
				replies.add(encdata);
			} // end for loop

			result.addProperty("success", true);
			result.addProperty("num_records", nbrofrecords);
			result.add("results", replies);

			redshiftreturnstring = result.toString();

		} catch (Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

					for (int i = 0; i < redshiftdata.size(); i++) {
						JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

						JsonPrimitive redshiftcolumn = redshiftrow.get(0).getAsJsonPrimitive();

						sensitive = redshiftcolumn.getAsJsonPrimitive().toString();
						replies.add(sensitive);

					}
					result.addProperty("success", true);
					result.addProperty("num_records", nbrofrecords);
					result.add("results", replies);
					redshiftreturnstring = result.toString();

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

		}

		if (bad_data) {
			System.out.println("errors: ");
			for (Map.Entry<Integer, String> entry : reshift_ErrorMap.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error index: " + mkey);
				System.out.println("Error Message: " + mvalue);
			}

		}

		System.out.println(redshiftreturnstring);
		// outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());
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

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {
		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);
		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);
		return cmuserset.findUserInUserSet(userName, newtoken);
	}

	@Override
	public void handleRequest(InputStream input, OutputStream output, Context context) throws IOException {
		// TODO Auto-generated method stub

	}
}
