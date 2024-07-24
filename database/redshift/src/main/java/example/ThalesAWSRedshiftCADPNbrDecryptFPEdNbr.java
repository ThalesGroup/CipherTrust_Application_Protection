package example;


import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.math.BigInteger;
import java.util.logging.Logger;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.spec.IvParameterSpec;
import org.apache.commons.io.IOUtils;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

/*
 * This test app to test the logic for a Redshift Database User Defined
 * Function(UDF). It is an example of how to use Thales Cipher Trust Application Data Protection (CADP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns.  
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.11 & CADP 8.12.6 or above.  
*  For more details on how to write Redshift UDF's please see
*  https://docs.aws.amazon.com/redshift/latest/dg/udf-creating-a-lambda-sql-udf.html#udf-lambda-json
*     
 */

public class ThalesAWSRedshiftCADPNbrDecryptFPEdNbr implements RequestStreamHandler {
	private static final Logger logger = Logger.getLogger(ThalesAWSRedshiftCADPNbrDecryptFPEdNbr.class.getName());
	private static final Gson gson = new Gson();
	/**
	* Returns an String that will be the encrypted value
	* <p>
	* Examples:
	* select thales_token_cadp_char(eventname) as enceventname  , eventname from event where len(eventname) > 5
	*
	* @param is any column in the database or any value that needs to be encrypted.  Mostly used for ELT processes.  
	*/
	
	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {



		// context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");
		JsonParser parser = new JsonParser();
		NAESession session = null;
		int statusCode = 200;

		String redshiftreturnstring = null;
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
		int nbr_of_rows_json_int = new Integer(nbr_of_rows_json_str);

		//System.out.println("number of records " + nbr_of_rows_json_str);

		String keyName = "testfaas";
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");

		// returnciphertextforuserwithnokeyaccess = is a environment variable to express
		// how data should be
		// returned when the user above does not have access to the key and if doing a
		// lookup in the userset
		// and the user does not exist. If returnciphertextforuserwithnokeyaccess = null
		// then an error will be
		// returned to the query, else the results set will provide ciphertext.
		// validvalues are 1 or null
		// 1 will return cipher text
		// null will return error.
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");

		// usersetlookup = should a userset lookup be done on the user from Big Query? 1
		// = true 0 = false.
		String usersetlookup = System.getenv("usersetlookup");
		// usersetID = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it
		// is
		// the userset in CM but could be a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");


		try {

			// Serialization
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

			//System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			String algorithm = "FPE/FF1/CARD10";
			// String algorithm = "AES/CBC/PKCS5Padding";
			String tweakAlgo = null;
			String tweakData = null;
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// initialize cipher to encrypt.
			decryptCipher.init(Cipher.DECRYPT_MODE, key, param);

			redshiftreturnstring = doTransform(decryptCipher, redshiftdata, redshiftreturndata);


		} catch (Exception e) {
			String sensitive = null;

			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

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
								System.out.println("Sensitive data is null or empty.");
							}
						} else {
							System.out.println("redshiftrow  is null or empty.");

						}

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

		} finally {
			if (session != null) {
				session.closeSession();
			}
		}
		//System.out.println("string  = " + redshiftreturnstring);
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
	
	public String doTransform(Cipher encryptCipher, JsonArray redshiftdata, StringBuffer redshiftreturndata)
			throws IllegalBlockSizeException, BadPaddingException {
		String decdata = "";
		String redshiftreturnstring = null;
		String sensitive = null;
		BigInteger sensitiveBI = new BigInteger("0");

		for (int i = 0; i < redshiftdata.size(); i++) {
			JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

			if (redshiftrow != null && redshiftrow.size() > 0) {
				JsonElement element = redshiftrow.get(0);
				if (element != null && !element.isJsonNull()) {
					sensitive = element.getAsString();
					if (sensitive.isEmpty() || sensitive.length() < 2) {
						if (sensitive.isEmpty()) {
							JsonElement elementforNull = new JsonPrimitive(0);
							sensitiveBI = new BigInteger("0");
						} else {
							boolean isvalid = isNumeric(sensitive);
							if (isvalid)
								sensitiveBI = element.getAsJsonPrimitive().getAsBigInteger();
							else
								sensitiveBI = new BigInteger("0");
						}

					} else {

						sensitive = element.getAsString();

						byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());
						decdata = new String(outbuf);

						sensitiveBI = new BigInteger(decdata);
					}
				} else {
					sensitiveBI = new BigInteger("0");

				}
			} else {
				sensitiveBI = new BigInteger("0");

			}
			redshiftreturndata.append(sensitiveBI);

			if (redshiftdata.size() == 1 || i == redshiftdata.size() - 1)
				continue;
			else
				redshiftreturndata.append(",");

		}

		redshiftreturndata.append("]}");

		redshiftreturnstring = new String(redshiftreturndata);

		return redshiftreturnstring;

	}
	
	public static boolean isNumeric(String strNum) {
		if (strNum == null) {
			return false;
		}
		try {
			double d = Double.parseDouble(strNum);
		} catch (NumberFormatException nfe) {
			return false;
		}
		return true;
	}
	
	public String formatReturnValue(int statusCode)

	{
		StringBuffer redshiftreturndata = new StringBuffer();

		String errormsg = "\"Error in UDF \"";
		redshiftreturndata.append("{ \"success\":");
		redshiftreturndata.append(false);
		redshiftreturndata.append(" \"num_records\":");
		redshiftreturndata.append(0);
		// redshiftreturndata.append(nbr_of_rows_json_int);
		redshiftreturndata.append(",");
		redshiftreturndata.append(" \"error_msg\":");
		redshiftreturndata.append(errormsg);
		redshiftreturndata.append(",");
		redshiftreturndata.append(" \"results\": [] }");
		// outputStream.write(redshiftreturnstring.getBytes());

		return redshiftreturndata.toString();
	}

}