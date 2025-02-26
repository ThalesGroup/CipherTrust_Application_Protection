package example;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.InputStream;
import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

public class ThalesDataBricksCRDPFPE {
//  @Override
	/*
	 * This test app to test the logic for a Databricks Database User Defined Function(UDF). It is an example of how to
	 * use Thales Cipher REST Data Protection (CRDP) to protect sensitive data in a column. This example uses Format
	 * Preserve Encryption (FPE) to maintain the original format of the data so applications or business intelligence
	 * tools do not have to change in order to use these columns.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts. Not production ready code. Was
	 * tested with CM 2.14 & CRDP 1.0 tech preview For more information on CRDP see link below.
	 * https://thalesdocs.com/ctp/con/crdp/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */

	private static final Gson gson = new Gson();
	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	private static Properties properties;

	static {
		try (InputStream input = ThalesDataBricksCRDPFPE.class.getClassLoader()
				.getResourceAsStream("udfConfig.properties")) {
			properties = new Properties();
			if (input == null) {
				throw new RuntimeException("Unable to find udfConfig.properties");
			}
			properties.load(input);
		} catch (Exception ex) {
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	public static void main(String[] args) throws Exception

	{
		

		String request_decrypt_nbr = "4356346534533";
		String request = "4545";

		System.out.println("input data = " + request);
		String mode = "protect";
		String datatype = "nbr";

		System.out.println("results = " + thales_crdp_udf(request, mode, datatype));
	}

	public static String thales_crdp_udf(String databricks_inputdata, String mode, String datatype) throws Exception {

		String protectedData = null;
		// Check for invalid data.
		if (databricks_inputdata != null && !databricks_inputdata.isEmpty()) {
			if (databricks_inputdata.length() < 2)
				return databricks_inputdata;

			if (!datatype.equalsIgnoreCase("char")) {

				BigInteger lowerBound = BigInteger.valueOf(-9);
				BigInteger upperBound = BigInteger.valueOf(-1);

				try {
					// Convert the string to an integer
					BigInteger number = new BigInteger(databricks_inputdata);

					// Check if the number is between -1 and -9
					if (number.compareTo(lowerBound) >= 0 && number.compareTo(upperBound) <= 0) {
						System.out.println("The input is a negative number between -1 and -9.");
						return databricks_inputdata;
					}
				} catch (NumberFormatException e) {
					System.out.println("The input is not a valid number.");
					return databricks_inputdata;
				}
			}

		} else {
			//System.out.println("The input is either null or empty.");
			return databricks_inputdata;
		}

		Map<Integer, String> dataBricksErrorMap = new HashMap<Integer, String>();
		String crdpip = properties.getProperty("CRDPIP");
		if (crdpip == null) {
			throw new IllegalArgumentException("No CRDPIP found for UDF: ");
		}
		int i = 0;
		// Please review Databricks documentation for other options such as spark broadcast env. variables,
		// cluster settings and ,spark session to obtain variables needed for the UDF.
		// returnciphertextforuserwithnokeyaccess = is a environment variable to express how data should be returned
		String returnciphertextforuserwithnokeyaccess = properties
				.getProperty("returnciphertextforuserwithnokeyaccess");
		// yes,no
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");
		String keymetadatalocation = properties.getProperty("keymetadatalocation");

		String external_version_from_ext_source = properties.getProperty("keymetadata");

		// Hard coded for now until CRDP 1.1 which the jwt will provide
		String databricksuser = properties.getProperty("CRDPUSER");

		String protection_profile = properties.getProperty("protection_profile");
		// String protection_profile = System.getenv("protection_profile");
		String dataKey = null;
		boolean bad_data = false;

		try {

			String jsonTagForProtectReveal = null;

			String showrevealkey = "yes";

			if (mode.equals("protect")) {
				dataKey = "data";
				jsonTagForProtectReveal = PROTECTRETURNTAG;
				if (keymetadatalocation.equalsIgnoreCase("internal")) {
					showrevealkey = properties.getProperty("showrevealinternalkey");
					if (showrevealkey == null)
						showrevealkey = "yes";
				}
			} else {
				dataKey = "protected_data";
				jsonTagForProtectReveal = REVEALRETURNTAG;
			}
			boolean showrevealkeybool = showrevealkey.equalsIgnoreCase("yes");

			String externalkeymetadata = null;
			String crdpjsonBody = null;

			JsonObject crdp_payload = new JsonObject();

			crdp_payload.addProperty("protection_policy_name", protection_profile);

			String sensitive = null;
			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");
			String urlStr = "http://" + crdpip + ":8090/v1/" + mode;

			sensitive = databricks_inputdata;

			crdp_payload.addProperty(dataKey, sensitive);
			if (mode.equals("reveal")) {
				crdp_payload.addProperty("username", databricksuser);
				if (keymetadatalocation.equalsIgnoreCase("external")) {
					crdp_payload.addProperty("external_version", external_version_from_ext_source);
				}
			}
			crdpjsonBody = crdp_payload.toString();

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
					if (keymetadatalocation.equalsIgnoreCase("external") && mode.equalsIgnoreCase("protect")) {
						externalkeymetadata = jsonObject.get("external_version").getAsString();
						// System.out.println("Protected Data ext key metadata need to store this: "
						// + externalkeymetadata);
					}

					if (keymetadatalocation.equalsIgnoreCase("internal") && mode.equalsIgnoreCase("protect")
							&& !showrevealkeybool) {
						if (protectedData.length() > 7)
							protectedData = protectedData.substring(7);
					}

				} else if (jsonObject.has("error_message")) {
					String errorMessage = jsonObject.get("error_message").getAsString();
					System.out.println("error_message: " + errorMessage);
					dataBricksErrorMap.put(i, errorMessage);
					bad_data = true;
				} else
					System.out.println("unexpected json value from results: ");

				// System.out.println("Protected Data: " + protectedData);
			} else {
				System.err.println("Request failed with status code: " + crdp_response.code());
			}

			crdp_response.close();

		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					protectedData = databricks_inputdata;
				}

			} else {
				e.printStackTrace(System.out);

			}
		}

		if (bad_data) {
			System.out.println("errors: ");
			for (Map.Entry<Integer, String> entry : dataBricksErrorMap.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error index: " + mkey);
				System.out.println("Error Message: " + mvalue);
			}

		}

		return protectedData;

	}

}