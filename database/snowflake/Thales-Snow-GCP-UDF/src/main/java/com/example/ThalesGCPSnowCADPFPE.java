package com.example;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.NAEKey;
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
import java.util.logging.Logger;

/* This test app to test the logic for a Snowflake Database User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.14 & CADP 8.16
*  For more information on CADP see link below. 
https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
*  For more information on Snowflake External Functions see link below. 
https://docs.snowflake.com/en/sql-reference/external-functions-creating-gcp
 * 
 *@author  mwarner
 * 
 */
public class ThalesGCPSnowCADPFPE implements HttpFunction {
//  @Override

	private static final Gson gson = new Gson();
	private static final String BADDATATAG = new String ("9999999999999999");


	public void service(HttpRequest request, HttpResponse response) throws Exception {

		String encdata = "";
		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonArray snowflakedata = null;
		int statusCode = 200;

		NAESession session = null;
		String keyName = "testfaas";
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
		String datatype = System.getenv("datatype");
		//mode of operation valid values are : encrypt or decrypt 
		String mode = System.getenv("mode");
		
		int cipherType = 0;
		if (mode.equals("encrypt"))
			cipherType = Cipher.ENCRYPT_MODE;
		else
			cipherType = Cipher.DECRYPT_MODE;
		
		try {
			

			//This code  is only to be used when input data contains user info.  
			/*
			 * if (usersetlookupbool) { // make sure cmuser is in Application Data
			 * Protection Clients Group
			 * 
			 * boolean founduserinuserset = findUserInUserSet(bigquerysessionUser, userName,
			 * password, usersetID, userSetLookupIP); // System.out.println("Found User " +
			 * founduserinuserset); if (!founduserinuserset) throw new
			 * CustomException("1001, User Not in User Set", 1001);
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


			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			int row_number = 0;

			String algorithm = null;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else if (datatype.equals("charint"))
				algorithm = "FPE/FF1/CARD10";
			else
				algorithm = "FPE/FF1/CARD10";

			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			Cipher thalesCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// initialize cipher to encrypt.
			thalesCipher.init(cipherType, key, param);
			
			snowflakereturnstring = formatReturnValue(statusCode, snowflakedata, false, thalesCipher, datatype);
			
		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

					snowflakereturnstring = formatReturnValue(statusCode, snowflakedata, true, null, datatype);

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
			if (session != null) {
				session.closeSession();
			}
		}
	//	System.out.println(snowflakereturnstring);
		response.getWriter().write(snowflakereturnstring);

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
	
	public String formatReturnValue(int statusCode, JsonArray snowflakedata, boolean error, Cipher thalesCipher,
			String datatype) throws IllegalBlockSizeException, BadPaddingException {
		int row_number = 0;

		String encdata = null;
		String sensitive = null;

		JsonObject bodyObject = new JsonObject();
		JsonArray dataArray = new JsonArray();
		JsonArray innerDataArray = new JsonArray();

		for (int i = 0; i < snowflakedata.size(); i++) {
			JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();
			for (int j = 0; j < snowflakerow.size(); j++) {
				if (j == 1) {
					sensitive = checkValid(snowflakerow);

					if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
						if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
							if (sensitive.contains("notvalid")) {
								sensitive = sensitive.replace("notvalid", "");
								innerDataArray.add(sensitive);
								// Can not return number since a leading 0 will not work.
								// innerDataArray.add(new BigInteger(sensitive));
							} else
								innerDataArray.add(BADDATATAG);

						} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {
							innerDataArray.add("");
						} else if (sensitive.contains("notvalid")) {
							sensitive = sensitive.replace("notvalid", "");
							innerDataArray.add(sensitive);
						} else {
							innerDataArray.add(sensitive);
						}

					} else {
						if (!error) {
							byte[] outbuf = thalesCipher.doFinal(sensitive.getBytes());
							encdata = new String(outbuf);
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								innerDataArray.add(encdata);
								// innerDataArray.add(new BigInteger(encdata));
							} else {
								innerDataArray.add(encdata);
							}
						} else {
							encdata = sensitive;
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								innerDataArray.add(encdata);
								// innerDataArray.add(new BigInteger(encdata));
							} else {
								innerDataArray.add(encdata);
							}
						}
					}

					dataArray.add(innerDataArray);
					innerDataArray = new JsonArray();

				} else {
					JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
					row_number = snowflakecolumn.getAsInt();
					innerDataArray.add(row_number);
				}
			}
		}

		bodyObject.add("data", dataArray);
		String bodyString = bodyObject.toString();

		return bodyString;

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