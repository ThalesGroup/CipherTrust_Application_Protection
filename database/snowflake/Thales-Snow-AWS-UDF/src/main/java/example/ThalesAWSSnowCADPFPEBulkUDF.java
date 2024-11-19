package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.math.BigInteger;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;

import org.apache.commons.io.IOUtils;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.ingrian.security.nae.AbstractNAECipher;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

/* This sample AWS Lambda Function is used to implement a Snowflake Database User Defined Function(UDF).  	/*
 * It is an example of how to use Thales Cipher Trust Application Data Protection (FCADP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns.
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.14 & CADP CADP 8.15.0.001
*  For more information on CADP see link below. 
https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
*  For more information on Snowflake External Functions see link below. 
https://docs.snowflake.com/en/sql-reference/external-functions-creating-aws

Notes: This example uses the CADP bulk API.  
Maximum elements supported are 10000 and each data element must be of size <= 3500. If the data
element has Unicode characters then the supported size limit would be 1750 characters

Size of spec array should be same as the number of elements if user wants to use separate spec values
for each data index.  Spec array of size equal to data size is passed. Each spec array index represents corresponding data
index.
 * 
 * @author  mwarner
 */

public class ThalesAWSSnowCADPFPEBulkUDF implements RequestStreamHandler {

	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;
	private static Integer[] snowrownbrs;
	private static final String BADDATATAG = new String("9999999999999999");
	private static int BATCHLIMIT = 10000;

	// private static final Logger logger =
	// Logger.getLogger(LambdaRequestStreamHandlerNbrEncyrptBulkFPE.class.getName());
	private static final Gson gson = new Gson();

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

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
		int nbrofrows = snowflakedata.size();
		
		for (int i = 0; i < nbrofrows; i++) {
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
		JsonObject inputJsonObject = new JsonObject();
		String bodyString = bodyObject.toString();
		inputJsonObject.addProperty("statusCode", 200);
		inputJsonObject.addProperty("body", bodyString);

		String formattedStringnew = inputJsonObject.toString();

		return formattedStringnew;
	}

	@Override
	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
		// context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");

		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();

		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonObject body = null;
		int statusCode = 200;
		int numberofchunks = 0;

		String callerStr = null;

		// https://www.baeldung.com/java-aws-lambda

		JsonObject snowflakeinput = null;

		JsonArray snowflakedata = null;
		NAESession session = null;
		String keyName = "testfaas";
		// String keyName = System.getenv("CMKEYNAME");
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		// returnciphertextforuserwithnokeyaccess = is a environment variable to express how data should be
		// returned when the user above does not have access to the key and if doing a lookup in the userset
		// and the user does not exist. If returnciphertextforuserwithnokeyaccess = no then an error will be
		// returned to the query, else the results set will provide ciphertext.
		// yes/no
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");

		// usersetlookup = should a userset lookup be done on the user from Cloud DB?
		// yes/no
		String usersetlookup = System.getenv("usersetlookup");
		// usersetidincm = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it
		// is the userset in CM but could be a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");
		// datatype - data type in db/actual data format/return type. valid values are char, charint, nbr, charintchar
		String datatype = System.getenv("datatype");
		// mode of operation valid values are : encrypt or decrypt
		String mode = System.getenv("mode");

		int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));

		int cipherType = 0;
		if (mode.equals("encrypt"))
			cipherType = Cipher.ENCRYPT_MODE;
		else
			cipherType = Cipher.DECRYPT_MODE;

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
					bodystr = bodystr.replaceAll("\\\\", "");
					// System.out.println("bodystr after replace" + bodystr);
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

					if (usersetlookupbool) { // make sure cmuser is in Application Data Protection Clients Group

						boolean founduserinuserset = findUserInUserSet(callerStr, userName, password, usersetID,
								userSetLookupIP);
						// System.out.println("Found User " + founduserinuserset);
						if (!founduserinuserset)
							throw new CustomException("1001, User Not in User Set", 1001);

					} else {
						usersetlookupbool = false;
					}

				} else {
					System.out.println("eerror");

				}
			}
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			String algorithm = null;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else if (datatype.equals("charint"))
				algorithm = "FPE/FF1/CARD10";
			else
				algorithm = "FPE/FF1/CARD10";

			int row_number = 0;

			AbstractNAECipher thalesCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");

			System.out.println("Batchsize = " + batchsize);
			int numberOfLines = snowflakedata.size();
			int totalRowsLeft = numberOfLines;

			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;

			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			snowrownbrs = new Integer[batchsize];
			JsonObject bodyObject = new JsonObject();
			JsonArray dataArray = new JsonArray();
			JsonArray innerDataArray = new JsonArray();

			thalesCipher.init(cipherType, key, spec[0]);

			int i = 0;
			int count = 0;
			boolean newchunk = true;
			int dataIndex = 0;
			int specIndex = 0;
			int snowRowIndex = 0;
			String sensitive = null;

			while (i < numberOfLines) {
				int index = 0;

				if (newchunk) {

					if (totalRowsLeft < batchsize) {
						spec = new FPEParameterAndFormatSpec[totalRowsLeft];
						data = new byte[totalRowsLeft][];
						snowrownbrs = new Integer[totalRowsLeft];
					} else {
						spec = new FPEParameterAndFormatSpec[batchsize];
						data = new byte[batchsize][];
						snowrownbrs = new Integer[batchsize];
					}
					newchunk = false;
				}

				JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

				for (int j = 0; j < snowflakerow.size(); j++) {

					if (j == 1) {

						// FPE example
						sensitive = checkValid(snowflakerow);
						if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								if (sensitive.contains("notvalid")) {
									sensitive = sensitive.replace("notvalid", "");
									sensitive = BADDATATAG + sensitive;
									data[dataIndex++] = sensitive.getBytes();
									// Can not return number since a leading 0 will not work.
									// innerDataArray.add(new BigInteger(sensitive));
								} else
									data[dataIndex++] = BADDATATAG.getBytes();
							} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {
								data[dataIndex++] = sensitive.getBytes();
							} else {
								data[dataIndex++] = sensitive.getBytes();
							}
							spec[specIndex++] = param;

						} else {
							data[dataIndex++] = sensitive.getBytes();
							spec[specIndex++] = param;
						}

					} else {
						JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
						row_number = snowflakecolumn.getAsInt();
						snowrownbrs[snowRowIndex++] = row_number;

					}

				}

				if (count == batchsize - 1) {

					// Map to store exceptions while encryption
					Map<Integer, String> encryptedErrorMap = new HashMap<Integer, String>();

					byte[][] encryptedData = thalesCipher.doFinalBulk(data, spec, encryptedErrorMap);

					for (Map.Entry<Integer, String> entry : encryptedErrorMap.entrySet()) {
						Integer mkey = entry.getKey();
						String mvalue = entry.getValue();
						encryptedErrorMapTotal.put(mkey, mvalue);
					}

					for (int enc = 0; enc < encryptedData.length; enc++) {

						innerDataArray.add(snowrownbrs[enc]);
						innerDataArray.add(new String(encryptedData[enc]));
						dataArray.add(innerDataArray);
						innerDataArray = new JsonArray();

						index++;

					}

					numberofchunks++;
					newchunk = true;
					count = 0;
					dataIndex = 0;
					specIndex = 0;
					snowRowIndex = 0;
				} else
					count++;

				totalRowsLeft--;
				i++;
			}

			if (count > 0) {
				numberofchunks++;
				int index = 0;
				Map<Integer, String> encryptedErrorMap = new HashMap<Integer, String>();
				byte[][] encryptedData = thalesCipher.doFinalBulk(data, spec, encryptedErrorMap);
				for (int enc = 0; enc < encryptedData.length; enc++) {
					innerDataArray.add(snowrownbrs[enc]);
					innerDataArray.add(new String(encryptedData[enc]));
					dataArray.add(innerDataArray);
					innerDataArray = new JsonArray();

					index++;

				}
			}

			bodyObject.add("data", dataArray);
			JsonObject inputJsonObject = new JsonObject();
			String bodyString = bodyObject.toString();
			inputJsonObject.addProperty("statusCode", 200);
			inputJsonObject.addProperty("body", bodyString);

			snowflakereturnstring = inputJsonObject.toString();
			// System.out.println("snowflakereturnstring = " + snowflakereturnstring);

		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

					try {
						snowflakereturnstring = formatReturnValue(statusCode, snowflakedata, true, null, datatype);
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
		System.out.println("number of chunks = " + numberofchunks);
		outputStream.write(snowflakereturnstring.getBytes());
	}
}