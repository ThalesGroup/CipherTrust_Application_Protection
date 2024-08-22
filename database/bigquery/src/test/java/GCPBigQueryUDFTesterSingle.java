
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.spec.IvParameterSpec;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.ingrian.security.nae.FPECharset;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonPrimitive;

import java.math.BigInteger;
import java.security.Security;
import java.util.logging.Logger;

public class GCPBigQueryUDFTesterSingle implements HttpFunction {
//  @Override
	/*
	 * This test app to test the logic for a BigQuery Database User Defined Function(UDF). It is an example of how to
	 * use Thales Cipher Trust Application Data Protection (CADP) to protect sensitive data in a column. This example
	 * uses Format Preserve Encryption (FPE) to maintain the original format of the data so applications or business
	 * intelligence tools do not have to change in order to use these columns.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts. Not production ready code. Was not
	 * tested for all possible data sizes and combinations of encryption algorithms and IV, etc. Was tested with CM 2.14
	 * & CADP 8.15.0.001 For more information on CADP see link below.
	 * https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */
	private static final Logger logger = Logger.getLogger(GCPBigQueryUDFTesterSingle.class.getName());
	private static final Gson gson = new Gson();
	private static final String BADDATATAG = new String("9999999999999999");

	public static void main(String[] args) throws Exception

	{
		GCPBigQueryUDFTesterSingle nw2 = new GCPBigQueryUDFTesterSingle();

		String requestnullcharint = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"charint\"\r\n" + "  },\r\n" + "  \"calls\": [\r\n"
				+ "    [\r\n" + "      \"34534534555\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"0\"\r\n"
				+ "    ],\r\n" + "    [\r\n" + "      \"\"\r\n" + "    ]\r\n" + "  ]\r\n" + "}";

		String requestnbrnull = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test1-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"nbr\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"1\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"null\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"\"\r\n" + "    ]\r\n" + "  ]\r\n" + "}";

		String requestnbr = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test1-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"nbr\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"34234234\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"4543321\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"67453435\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		String request_decrypt_nbr = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test1-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"decrypt\",\r\n" + "    \"datatype\": \"nbr\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"54986217\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"6550422\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"01403274\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		
		String request = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test1-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"char\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"David Cullen\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		String requestdecrypt = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test1-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"decrypt\",\r\n" + "    \"datatype\": \"char\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"izVS UukS9q\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"b0Dl I41Za\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"IEXMh rgrZ1q\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		String response = null;
		nw2.service(request_decrypt_nbr, response);

	}

	public void service(String request, String response) throws Exception {

		String encdata = "";
		String keyName = "testfaas";
		// The following must be entered in as environment variables in the GCP Cloud
		// Function.
		// CM User and CM Password. These can also be provided as secrets in GCP as
		// well.
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
		
		String mode = null;
		String datatype = null;

		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		NAESession session = null;
		String formattedString = null;
		JsonArray bigquerydata = null;
		JsonObject result = new JsonObject();
		JsonArray replies = new JsonArray();

		try {

			// Parse JSON request and check for "name" field
			JsonObject requestJson = null;
			try {
				JsonElement requestParsed = gson.fromJson(request, JsonElement.class);

				if (requestParsed != null && requestParsed.isJsonObject()) {
					requestJson = requestParsed.getAsJsonObject();
				}

				if (requestJson != null && requestJson.has("sessionUser")) {
					bigquerysessionUser = requestJson.get("sessionUser").getAsString();
					System.out.println("name " + bigquerysessionUser);
				}

				if (requestJson != null && requestJson.has("userDefinedContext")) {
					bigqueryuserDefinedContext = requestJson.get("userDefinedContext");
					JsonObject location = requestJson.getAsJsonObject("userDefinedContext");
					mode = location.get("mode").getAsString();
					datatype = location.get("datatype").getAsString();

				}

			} catch (JsonParseException e) {
				logger.severe("Error parsing JSON: " + e.getMessage());
			}

			bigquerydata = requestJson.getAsJsonArray("calls");

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

			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"D:\\product\\Build\\CADP_for_JAVA.properties");


			// System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
			// "D:\\product\\Build\\CADP_for_JAVA.properties");

			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			int cipherType = 0;
			String algorithm = "FPE/FF1/CARD62";

			String tweakAlgo = null;
			String tweakData = null;
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			
			if (mode.equals("encrypt"))
				cipherType = Cipher.ENCRYPT_MODE;
			else
				cipherType = Cipher.DECRYPT_MODE;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else {
				algorithm = "FPE/FF1/CARD10";
		//		FPECharset charset = FPECharset.getUnicodeRangeCharset("31-39");
		//		param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).set_charset(charset).build();
			}

			IvParameterSpec ivSpec = null;


			///
			ivSpec = param;
			Cipher thalesCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			thalesCipher.init(cipherType, key, ivSpec);

			formattedString = formatReturnValue(200,bigquerydata,false,thalesCipher,datatype);

		} catch (

		Exception e) {

			System.out.println("in exception with " + e.getMessage());
			String inputdata = null;
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					result = new JsonObject();
					replies = new JsonArray();
					formattedString = formatReturnValue(200,bigquerydata,true,null,datatype);

				} else
					e.printStackTrace(System.out);
			} else
				e.printStackTrace(System.out);
		} finally {
			if (session != null) {
				session.closeSession();
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

	public String formatReturnValue(int statusCode, JsonArray bigQueryArray, boolean error, Cipher thalesCipher,
			String datatype) throws IllegalBlockSizeException, BadPaddingException {
		int row_number = 0;

		String encdata = null;
		String sensitive = null;
		String formattedString = null;
		JsonObject bodyObject = new JsonObject();
		JsonArray dataArray = new JsonArray();


		for (int i = 0; i < bigQueryArray.size(); i++) {
			JsonArray bigQueryRow = bigQueryArray.get(i).getAsJsonArray();

			sensitive = checkValid(bigQueryRow);

			if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
				if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
					if (sensitive.contains("notvalid")) {
						System.out.println("adding null not charint or nbr");
						sensitive = sensitive.replace("notvalid", "");
						dataArray.add(sensitive);
						// Can not return number since a leading 0 will not work.
						// innerDataArray.add(new BigInteger(sensitive));
					} else
						dataArray.add(BADDATATAG);

				} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {
					dataArray.add("");
				} else if (sensitive.contains("notvalid")) {
					sensitive = sensitive.replace("notvalid", "");
					dataArray.add(sensitive);
				} else {
					dataArray.add(sensitive);
				}

			} else {
				if (!error) {
					byte[] outbuf = thalesCipher.doFinal(sensitive.getBytes());
					encdata = new String(outbuf);
					if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
						dataArray.add(encdata);
						// innerDataArray.add(new BigInteger(encdata));
					} else {
						dataArray.add(encdata);
					}
				} else {
					encdata = sensitive;
					if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
						dataArray.add(encdata);
						// innerDataArray.add(new BigInteger(encdata));
					} else {
						dataArray.add(encdata);
					}
				}
			}

			// innerDataArray.add(encdata);
		 
			 

		}

		bodyObject.add("replies", dataArray);
		formattedString = bodyObject.toString();
		return formattedString;
		// return bodyString;

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

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

	}

}