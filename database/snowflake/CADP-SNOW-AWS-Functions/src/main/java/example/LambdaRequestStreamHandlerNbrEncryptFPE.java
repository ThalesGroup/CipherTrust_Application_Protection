package example;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

/* This sample AWS Lambda Function is used to implement a Snowflake Database User Defined Function(UDF).  	/*
     * It is an example of how to use Thales Cipher Trust Application Data Protection (CADP)
	 * to protect sensitive data in a column. This example uses
	 * Format Preserve Encryption (FPE) to maintain the original format of the data
	 * so applications or business intelligence tools do not have to change in order
	 * to use these columns. 
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts.
	 * Not production ready code. Was not tested for all possible data sizes and
	 * combinations of encryption algorithms and IV, etc. Was tested with CM 2.14 &
	 * CADP 8.15.0.001 For more information on CADP see link below.
*  For more information on CADP see link below. 
https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
*  For more information on Snowflake External Functions see link below. 
https://docs.snowflake.com/en/sql-reference/external-functions-creating-aws
 * 
 */

public class LambdaRequestStreamHandlerNbrEncryptFPE implements RequestStreamHandler {
//	private static final Logger logger = Logger.getLogger(LambdaRequestStreamHandlerCharEncryptFPE.class.getName());
	private static final Gson gson = new Gson();

	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
		// context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");

		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonObject body = null;
		int statusCode = 200;

		// https://www.baeldung.com/java-aws-lambda
		JsonObject snowflakeinput = null;
		String callerStr = null;
		JsonArray snowflakedata = null;

		NAESession session = null;

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
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.matches("-?\\d+"); // Using regular

		// usersetlookup = should a userset lookup be done on the user from Big Query? 1
		// = true 0 = false.
		String usersetlookup = System.getenv("usersetlookup");
		// usersetID = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it
		// is
		// the userset in CM but could be a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.matches("-?\\d+");

		try {

			JsonElement rootNode = JsonParser.parseString(input).getAsJsonObject();
			if (rootNode.isJsonObject()) {
				snowflakeinput = rootNode.getAsJsonObject();
				if (snowflakeinput.isJsonObject()) {
					// For some reason when using snowflake it adds \n and \ to quotes in json.
					// the JsonParser.parseString(input).getAsJsonObject(); is supposed to remove
					// all of those
					// characters but it does not do it for snowflake json.
					JsonElement bodyele = snowflakeinput.get("body");
					String bodystr = bodyele.getAsString().replaceAll(System.lineSeparator(), "");
					// System.out.println("bodystr before replace" + bodystr );
					bodystr = bodystr.replaceAll("\\\\", "");
					// System.out.println("bodystr after replace" + bodystr );
					body = gson.fromJson(bodystr, JsonObject.class);
					snowflakedata = body.getAsJsonArray("data");
					JsonObject requestContext = snowflakeinput.getAsJsonObject("requestContext");

					if (requestContext != null) {
						JsonObject identity = requestContext.getAsJsonObject("identity");

						if (identity != null) {
							callerStr = identity.get("user").getAsString();
							System.out.println("user: " + callerStr);
						} else {
							System.out.println("Identity not found.");
						}
					} else {
						System.out.println("Request context not found.");
					}

					if (usersetlookupbool) {
						// Convert the string to an integer
						int num = Integer.parseInt(usersetlookup);
						// make sure cmuser is in Application Data Protection Clients Group
						if (num >= 1) {
							boolean founduserinuserset = findUserInUserSet(callerStr, userName, password, usersetID,
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

				} else {
					System.out.println("eerror");

				}
			}

			// System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			String algorithm = "FPE/FF1/CARD10";
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			///
			// ivSpec = param;
			Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");

			encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
			snowflakereturnstring = formatReturnValue(statusCode, snowflakedata, false, encryptCipher);

		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401") || (e.getMessage().contains("1001") || (e.getMessage().contains("1002"))) ) {

					try {
						snowflakereturnstring = formatReturnValue(statusCode, snowflakedata, true, null);
					} catch (IllegalBlockSizeException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					} catch (BadPaddingException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}

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
		
		 outputStream.write(snowflakereturnstring.getBytes());

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

	public String formatReturnValue(int statusCode, JsonArray snowflakedata, boolean error, Cipher encryptCipher)
			throws IllegalBlockSizeException, BadPaddingException {
		int row_number = 0;
		String snowflakereturnstring = null;
		StringBuffer snowflakereturndatasc = new StringBuffer();
		StringBuffer snowflakereturndatasb = new StringBuffer();
		// Serialization
		snowflakereturndatasb.append("{ \"statusCode\":");
		snowflakereturndatasb.append(statusCode);
		snowflakereturndatasb.append(",");
		snowflakereturndatasb.append(" \"body\":  ");
		snowflakereturndatasc.append("{ \"data\": [");
		String encdata = null;

		for (int i = 0; i < snowflakedata.size(); i++) {
			JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();
			snowflakereturndatasc.append("[");
			for (int j = 0; j < snowflakerow.size(); j++) {

				JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
				String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();

				// boolean isNumber = StringUtils.isNumeric(sensitive);
				// get a cipher
				if (j == 1) {
					if (error)
						snowflakereturndatasc.append(sensitive);
					else {
						// FPE example
						// initialize cipher to encrypt.
						// encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
						// encrypt data
						byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());
						encdata = new String(outbuf);

						snowflakereturndatasc.append(encdata);

					}

				} else {
					row_number = snowflakecolumn.getAsInt();
					snowflakereturndatasc.append(row_number);
					snowflakereturndatasc.append(",");
				}

			}
			if (snowflakedata.size() == 1 || i == snowflakedata.size() - 1)
				snowflakereturndatasc.append("]");
			else
				snowflakereturndatasc.append("],");

		}
		snowflakereturndatasc.append("] }");
		snowflakereturndatasb.append(new Gson().toJson(snowflakereturndatasc));
		snowflakereturndatasb.append("}");
		snowflakereturnstring = new String(snowflakereturndatasb);

		return snowflakereturnstring;

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