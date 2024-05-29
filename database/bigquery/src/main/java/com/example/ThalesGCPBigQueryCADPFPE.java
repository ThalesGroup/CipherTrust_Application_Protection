package com.example;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
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
import java.io.BufferedWriter;
import java.util.logging.Logger;

public class ThalesGCPBigQueryCADPFPE implements HttpFunction {
//  @Override
	/*
	 * This test app to test the logic for a BigQuery Database User Defined
	 * Function(UDF). It is an example of how to use Thales Cipher Trust Application Data Protection (CADP)
	 * to protect sensitive data in a column. This example uses
	 * Format Preserve Encryption (FPE) to maintain the original format of the data
	 * so applications or business intelligence tools do not have to change in order
	 * to use these columns. There is no need to deploy a function to run it.
	 * This example uses the bulk API.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts.
	 * Not production ready code. Was not tested for all possible data sizes and
	 * combinations of encryption algorithms and IV, etc. Was tested with CM 2.14 &
	 * CADP 8.16 For more information on CADP see link below.
	 * https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */
	private static final Logger logger = Logger.getLogger(ThalesGCPBigQueryCADPFPE.class.getName());
	private static final Gson gson = new Gson();

	public void service(HttpRequest request, HttpResponse response) throws Exception {

		String encdata = "";
		String keyName = "testfaas";
		//The following must be entered in as environment variables in the GCP Cloud Function. 
		//CM User and CM Password.  These can also be provided as secrets in GCP as well.
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		//returnciphertextforuserwithnokeyaccess = is a environment variable to express how  data should be
		//returned when the user above does not have access to the key and if doing a lookup in the userset 
		//and the user does not exist.  If returnciphertextforuserwithnokeyaccess = null then an error will be 
		//returned to the query, else the results set will provide ciphertext. 
		// validvalues are 1 or null
		// 1 will return cipher text
		// null will return error.
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.matches("-?\\d+"); // Using regular
		
		//usersetlookup = should a userset lookup be done on the user from Big Query?  1 = true 0 = false. 
		String usersetlookup = System.getenv("usersetlookup");
		//usersetID = should be the usersetid in CM to query.  
		String usersetID = System.getenv("usersetidincm");
		//usersetlookupip = this is the IP address to query the userset.  Currently it is 
		//the userset in CM but could be a memcache or other in memory db. 
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.matches("-?\\d+");

		String bigqueryreturnstring = null;
		StringBuffer bigqueryreturndata = new StringBuffer();
		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		String mode = null;
		String datatype = null;
		NAESession session = null;
		String formattedString = null;
		JsonArray bigquerydata = null;

		try {

			// Parse JSON request and check for "name" field
			JsonObject requestJson = null;
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
					JsonObject location = requestJson.getAsJsonObject("userDefinedContext");
					mode = location.get("mode").getAsString();
					datatype = location.get("datatype").getAsString();

				}

			} catch (JsonParseException e) {
				logger.severe("Error parsing JSON: " + e.getMessage());
			}
			bigquerydata = requestJson.getAsJsonArray("calls");
			
			if (usersetlookupbool) {
				// Convert the string to an integer
				int num = Integer.parseInt(usersetlookup);
				// make sure cmuser is in Application Data Protection Clients Group
				if (num >= 1) {
					boolean founduserinuserset = findUserInUserSet(bigquerysessionUser, userName, password, usersetID,
							userSetLookupIP);
					// System.out.println("Found User " + founduserinuserset);
					if (!founduserinuserset)
						throw new CustomException("1001, User Not in User Set", 1001);

				}

				else
					usersetlookupbool = false;
			} else {
				usersetlookupbool = false;
			}



			// System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			NAESecureRandom rng = new NAESecureRandom(session);

			byte[] iv = new byte[16];
			rng.nextBytes(iv);
			IvParameterSpec ivSpec = new IvParameterSpec(iv);

			// Serialization

			bigqueryreturndata.append("{ \"replies\": [");

			int cipherType = 0;
			String algorithm = "FPE/FF1/CARD62";

			if (mode.equals("encrypt"))
				cipherType = Cipher.ENCRYPT_MODE;
			else
				cipherType = Cipher.DECRYPT_MODE;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else if (datatype.equals("charint"))
				algorithm = "FPE/FF1/CARD10";
			else
				algorithm = "FPE/FF1/CARD10";

			String tweakAlgo = null;
			String tweakData = null;
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			///
			ivSpec = param;
			Cipher thalesCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			thalesCipher.init(cipherType, key, ivSpec);
			String sensitive = null;
			for (int i = 0; i < bigquerydata.size(); i++) {
				JsonArray bigquerytrow = bigquerydata.get(i).getAsJsonArray();
				if (bigquerytrow != null && bigquerytrow.size() > 0) {
					JsonElement element = bigquerytrow.get(0);
					if (element != null && !element.isJsonNull()) {
						sensitive = element.getAsString();
						if (sensitive.isEmpty() || sensitive.length() < 2) {
							encdata = sensitive;
						} else {
							if (sensitive.equalsIgnoreCase("null")) {
								encdata = sensitive;
							} else {
								byte[] outbuf = thalesCipher.doFinal(sensitive.getBytes());
								encdata = new String(outbuf);

								//System.out.println("Sensitive data: " + sensitive);
							}
						}
					} else {
						//System.out.println("Sensitive data is null or empty.");
						encdata = sensitive;
					}
				} else {
					//System.out.println("bigquerytrow is null or empty.");
					encdata = sensitive;
				}

				bigqueryreturndata.append(encdata);
				if (bigquerydata.size() == 1 || i == bigquerydata.size() - 1)
					continue;
				else
					bigqueryreturndata.append(",");

			}

			bigqueryreturndata.append("]}");

			bigqueryreturnstring = new String(bigqueryreturndata);
	        formattedString = formatString(bigqueryreturnstring);
			
		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401") || (e.getMessage().contains("1001") || (e.getMessage().contains("1002"))) ) {
					JsonObject result = new JsonObject();
					JsonArray replies = new JsonArray();
					if (bigquerydata != null) {
						for (int i = 0; i < bigquerydata.size(); i++) {
							JsonArray innerArray = bigquerydata.get(i).getAsJsonArray();
							replies.add(innerArray.get(0).getAsString());
						}
						result.add("replies", replies);
						formattedString = result.toString();
					} else {
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
			} else {
				e.printStackTrace(System.out);
				response.setStatusCode(500);
				BufferedWriter writer = response.getWriter();
				writer.write("Internal Server Error Review logs for details");
			}
		} finally

		{
			if (session != null) {
				session.closeSession();
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