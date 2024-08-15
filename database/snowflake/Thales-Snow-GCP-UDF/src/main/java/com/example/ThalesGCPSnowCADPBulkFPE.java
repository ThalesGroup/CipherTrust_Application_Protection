package com.example;


import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.AbstractNAECipher;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;
import com.ingrian.security.nae.NAECipher;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonPrimitive;

import java.math.BigInteger;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;
/* This sample GCP Function is used to implement a Snowflake Database User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.14 & CADP 8.16.001
*  For more information on CADP see link below. 
https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
*  For more information on Snowflake External Functions see link below. 
https://docs.snowflake.com/en/sql-reference/external-functions-creating-gcp

Notes: This example uses the CADP bulk API.  
Maximum elements supported are 10000 and each data element must be of size <= 3500. If the data
element has Unicode characters then the supported size limit would be 1750 characters

Size of spec array should be same as the number of elements if user wants to use separate spec values
for each data index.  Spec array of size equal to data size is passed. Each spec array index represents corresponding data
index.
 * 
 *@author  mwarner
 * 
 */
public class ThalesGCPSnowCADPBulkFPE implements HttpFunction {
//  @Override
	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;
	private static Integer[] snowrownbrs;

	private static int BATCHLIMIT = 10000;
	private static final Logger logger = Logger.getLogger(ThalesGCPSnowCADPBulkFPE.class.getName());
	private static final Gson gson = new Gson();
	private static final String BADDATATAG = new String ("9999999999999999");

	public void service(HttpRequest request, HttpResponse response) throws Exception {

		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonArray snowflakedata = null;
		NAESession session = null;
		
		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();
		JsonObject body = null;
		int statusCode = 200;
		int numberofchunks = 0;
	
		String keyName = "testfaas";
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
		String datatype = System.getenv("datatype");
		//mode of operation valid values are : encrypt or decrypt 
		String mode = System.getenv("mode");
		
		int cipherType = 0;
		if (mode.equals("encrypt"))
			cipherType = Cipher.ENCRYPT_MODE;
		else
			cipherType = Cipher.DECRYPT_MODE;
		
		
		int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
		
		try {



			// This code is only to be used when input data contains user info.
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
			//How many records in a chunk.  Testing has indicated point of diminishing  returns at 100 or 200, but 
			//may vary depending on size of data. 
			
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
				logger.severe("Error parsing JSON: " + e.getMessage());
			}

			// System.setProperty("com.ingrian.security.nae.IngrianNAE_Properties_Conf_Filename",
			// "IngrianNAE.properties");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			// IngrianProvider builder = new
			// Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("IngrianNAE.properties")).build();
			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			int row_number = 0;

			StringBuffer snowflakereturndata = new StringBuffer();
			int numberOfLines = snowflakedata.size();
			int totalRowsLeft = numberOfLines;

			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			snowrownbrs = new Integer[batchsize];
			JsonObject bodyObject = new JsonObject();
			JsonArray dataArray = new JsonArray();
			JsonArray innerDataArray = new JsonArray();
			
			String algorithm = null;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else if (datatype.equals("charint"))
				algorithm = "FPE/FF1/CARD10";
			else
				algorithm = "FPE/FF1/CARD10";
			
			

			AbstractNAECipher thalesCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			int i = 0;

			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();

			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			snowrownbrs = new Integer[batchsize];
			String sensitive = null;
			thalesCipher.init(cipherType, key, spec[0]);

			//int i = 0;
			int count = 0;
			boolean newchunk = true;
			int dataIndex = 0;
			int specIndex = 0;
			int snowRowIndex = 0;
			//String sensitive = null;
			
			
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

						sensitive = checkValid(snowflakerow);
						
						if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								if (sensitive.contains("notvalid")) {
									sensitive = sensitive.replace("notvalid", "");
									sensitive = BADDATATAG+sensitive;
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
			String bodyString = bodyObject.toString();
			
			snowflakereturnstring = bodyString.toString();
			

		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401") || (e.getMessage().contains("1001") || (e.getMessage().contains("1002"))) ) {

					try {
						snowflakereturnstring = formatReturnValue(statusCode, snowflakedata, true, null,datatype);
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
		//System.out.println("snowflakereturnstring = " + snowflakereturnstring);
		  response.getWriter().write(snowflakereturnstring);
		  

		
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