
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;
import javax.crypto.Cipher;
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
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;
import com.ingrian.security.nae.NAECipher;

/*
 * This test app to test the logic for a Redshift Database User Defined
 * Function(UDF). It is an example of how to use Thales Cipher Trust Application Data Protection (CADP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns. There is no need to deploy a function to run it.
 * 
 * Note: This source code is only to be used for testing and proof of concepts.
 * Not production ready code. Was not tested for all possible data sizes and
 * combinations of encryption algorithms and IV, etc. Was tested with CM 2.14 &
 * CADP 8.15.0.001 For more information on CADP see link below.    
*  For more details on how to write Redshift UDF's please see
*  https://docs.aws.amazon.com/redshift/latest/dg/udf-creating-a-lambda-sql-udf.html#udf-lambda-json
*     
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

public class ThalesAWSRedshiftCADPBulkTester implements RequestStreamHandler {
	private static final Logger logger = Logger.getLogger(ThalesAWSRedshiftCADPBulkTester.class.getName());
	private static final Gson gson = new Gson();

	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;
	private static int BATCHLIMIT = 10000;

	public static void main(String[] args) throws Exception {

		ThalesAWSRedshiftCADPBulkTester nw2 = new ThalesAWSRedshiftCADPBulkTester();

		String request = "{\r\n" + "  \"request_id\" : \"23FF1F97-F28A-44AA-AB67-266ED976BF40\",\r\n"
				+ "  \"cluster\" : \"arn:aws:redshift:xxxx\",\r\n" + "  \"user\" : \"adminuser\",\r\n"
				+ "  \"database\" : \"db1\",\r\n" + "  \"external_function\": \"public.foo\",\r\n"
				+ "  \"query_id\" : 5678234,\r\n" + "  \"num_records\" : 3,\r\n" + "  \"arguments\" : [\r\n"
				+ "     [ \"thisisthefirstvalue\"],\r\n" + "     [ \"Thisisthesecondvalue\"],\r\n"
				+ "     [ \"Thisisthethirdvalue\"]\r\n" + "   ]\r\n" + " }";

		nw2.handleRequest(request, null, null);

	}

	/**
	 * Returns an String that will be the encrypted value
	 * <p>
	 * Examples: select thales_token_cadp_char(eventname) as enceventname ,
	 * eventname from event where len(eventname) > 5
	 *
	 * @param is any column in the database or any value that needs to be encrypted.
	 *           Mostly used for ELT processes.
	 */

	public void handleRequest(String inputStream, OutputStream outputStream, Context context) throws IOException {

		String input = inputStream;
		JsonParser parser = new JsonParser();
		int statusCode = 200;

		String redshiftreturnstring = null;
		StringBuffer redshiftreturndata = new StringBuffer();

		boolean status = true;
		int numberofchunks = 0;
		JsonObject redshiftinput = null;
		JsonElement rootNode = parser.parse(input);
		JsonArray redshiftdata = null;
		String redshiftuserstr = null;

		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();
		Map<Integer, String> encryptedErrorMap = new HashMap<Integer, String>();
		// https://www.baeldung.com/java-aws-lambda

		StringBuffer redshiftreturndatasb = new StringBuffer();
		StringBuffer redshiftreturndatasc = new StringBuffer();

		NAESession session = null;

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
			System.out.println("Bad data from Redshift.");

		}

		JsonPrimitive nbr_of_rows_json = redshiftinput.getAsJsonPrimitive("num_records");
		String nbr_of_rows_json_str = nbr_of_rows_json.getAsJsonPrimitive().toString();
		int nbr_of_rows_json_int = new Integer(nbr_of_rows_json_str);

		System.out.println("number of records " + nbr_of_rows_json_str);

		// apiuser
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
		int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
		if (batchsize >= BATCHLIMIT)
			batchsize = BATCHLIMIT;
		spec = new FPEParameterAndFormatSpec[batchsize];
		data = new byte[batchsize][];

		try {

			System.setProperty("com.ingrian.security.nae.IngrianNAE_Properties_Conf_Filename",
					"D:\\product\\Build\\IngrianNAE-134.properties");

			/*
			 * System.setProperty(
			 * "com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
			 * "CADP_for_JAVA.properties"); IngrianProvider builder = new
			 * Builder().addConfigFileInputStream(
			 * getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).
			 * build();
			 */
			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			int row_number = 0;

			// Serialization
			redshiftreturndatasb.append("{ \"success\":");
			redshiftreturndatasb.append(status);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"num_records\":");
			redshiftreturndatasb.append(nbr_of_rows_json_int);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"results\": [");

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

			String algorithm = "FPE/FF1/CARD62";

			String tweakAlgo = null;
			String tweakData = null;
			int totalRowsLeft = redshiftdata.size();
			AbstractNAECipher encryptCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, spec[0]);
			
			int i = 0;
			int index = 0;
			int count = 0;
			boolean newchunk = true;
			int dataIndex = 0;
			int specIndex = 0;

			while (i < redshiftdata.size()) {
				index = 0;

				if (newchunk) {
					if (totalRowsLeft < batchsize) {
						spec = new FPEParameterAndFormatSpec[totalRowsLeft];
						data = new byte[totalRowsLeft][];

					} else {
						spec = new FPEParameterAndFormatSpec[batchsize];
						data = new byte[batchsize][];

					}
					newchunk = false;
				}

				JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

				JsonPrimitive redshiftcolumn = redshiftrow.get(0).getAsJsonPrimitive();
				//System.out.print(redshiftcolumn + " ");
				String sensitive = redshiftcolumn.getAsJsonPrimitive().toString();
				data[dataIndex++] = sensitive.getBytes();
				spec[specIndex++] = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();

				if (count == batchsize - 1) {

				// Map to store exceptions while encryption
					encryptedErrorMap = new HashMap<Integer, String>();

					// performing bulk operation
					byte[][] encryptedData = encryptCipher.doFinalBulk(data, spec, encryptedErrorMap);

					for (Map.Entry<Integer, String> entry : encryptedErrorMap.entrySet()) {
						Integer mkey = entry.getKey();
						String mvalue = entry.getValue();
						encryptedErrorMapTotal.put(mkey, mvalue);
					}

					for (int enc = 0; enc < encryptedData.length; enc++) {

						redshiftreturndatasc.append(new String(encryptedData[enc]));
						redshiftreturndatasc.append(",");
						index++;

					}

					numberofchunks++;
					newchunk = true;
					count = 0;
					dataIndex = 0;
					specIndex = 0;
				} else
					count++;

				totalRowsLeft--;
				i++;
			}

			if (count > 0) {
				numberofchunks++;
				byte[][] encryptedData = encryptCipher.doFinalBulk(data, spec, encryptedErrorMap);
				for (int enc = 0; enc < encryptedData.length; enc++) {

					redshiftreturndatasc.append(new String(encryptedData[enc]));
					redshiftreturndatasc.append(",");
					index++;
					totalRowsLeft--;

				}
			}

			redshiftreturndatasc.append("] ");
			redshiftreturndatasb.append(redshiftreturndatasc);
			redshiftreturndatasb.append("}");

			redshiftreturnstring = new String(redshiftreturndatasb);

		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401") || (e.getMessage().contains("1001") || (e.getMessage().contains("1002"))) ) {

					for (int i = 0; i < redshiftdata.size(); i++) {
						JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

						JsonPrimitive redshiftcolumn = redshiftrow.get(0).getAsJsonPrimitive();

						String sensitive = redshiftcolumn.getAsJsonPrimitive().toString();

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
		}

		finally {
			if (session != null) {
				session.closeSession();
			}
		}
		int lastIndex = redshiftreturnstring.lastIndexOf(",");
		// Replace the comma before the closing square bracket if it exists
		if (lastIndex != -1) {
			redshiftreturnstring = redshiftreturnstring.substring(0, lastIndex)
					+ redshiftreturnstring.substring(lastIndex + 1);
		}
		System.out.println("string  = " + redshiftreturnstring);
		System.out.println("numberofchunks  = " + numberofchunks);
		// outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());
	}

	@Override
	public void handleRequest(InputStream input, OutputStream output, Context context) throws IOException {
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

}