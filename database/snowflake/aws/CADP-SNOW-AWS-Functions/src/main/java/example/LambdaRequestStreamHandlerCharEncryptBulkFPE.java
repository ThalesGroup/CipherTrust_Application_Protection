<<<<<<< HEAD
package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
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
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

/* This sample AWS Lambda Function is used to implement a Snowflake Database User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.
*   
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.8 & CADP 8.13
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
 *@author  mwarner
 */

public class LambdaRequestStreamHandlerCharEncryptBulkFPE implements RequestStreamHandler {

	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;
	private static Integer[] snowrownbrs;

	private static int BATCHLIMIT = 10000;

//	private static final Logger logger = Logger.getLogger(LambdaRequestStreamHandlerCharEncryptBulkFPE.class.getName());
	private static final Gson gson = new Gson();

	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
		context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");

		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();
		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonObject body = null;
		int statusCode = 200;

		// https://www.baeldung.com/java-aws-lambda

		JsonObject snowflakeinput = null;

		JsonArray snowflakedata = null;
		StringBuffer snowflakereturndatasb = new StringBuffer();
		StringBuffer snowflakereturndatasc = new StringBuffer();

		try {

			String keyName = "testfaas";
			// String keyName = System.getenv("CMKEYNAME");
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");
			int batchsize = 1000;
			// int batchsize = System.getenv("BATCHSIZE");
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			snowrownbrs = new Integer[batchsize];

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
					//System.out.println("bodystr after replace" + bodystr);
					body = gson.fromJson(bodystr, JsonObject.class);
					snowflakedata = body.getAsJsonArray("data");
				} else {
					System.out.println("eerror");

				}
			}
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

			NAESession session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			int row_number = 0;

			snowflakereturndatasb = new StringBuffer();
			// Serialization
			snowflakereturndatasb.append("{ \"statusCode\":");
			snowflakereturndatasb.append(statusCode);
			snowflakereturndatasb.append(",");
			snowflakereturndatasb.append(" \"body\":  ");
			snowflakereturndatasc.append("{ \"data\": [");
			String algorithm = "FPE/FF1/CARD62";
			// String algorithm = "AES/CBC/PKCS5Padding";

			AbstractNAECipher encryptCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			int i = 0;

			int totalRowsLeft = snowflakedata.size();

			while (i < snowflakedata.size()) {
				int index = 0;
				int dataIndex = 0;
				int specIndex = 0;
				int snowRowIndex = 0;
				//System.out.println("totalRowsLeft begining =" + totalRowsLeft);
				if (totalRowsLeft < batchsize) {
					spec = new FPEParameterAndFormatSpec[totalRowsLeft];
					data = new byte[totalRowsLeft][];
					snowrownbrs = new Integer[totalRowsLeft];
				} else {
					spec = new FPEParameterAndFormatSpec[batchsize];
					data = new byte[batchsize][];
					snowrownbrs = new Integer[batchsize];
				}

				for (int b = 0; b < batchsize && b < totalRowsLeft; b++) {

					JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

					for (int j = 0; j < snowflakerow.size(); j++) {

						JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
						System.out.print(snowflakecolumn + " ");
						String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
						// get a cipher
						if (j == 1) {

							// FPE example
							data[dataIndex++] = sensitive.getBytes();
							spec[specIndex++] = new FPEParameterAndFormatBuilder(tweakData)
									.set_tweakAlgorithm(tweakAlgo).build();
						} else {

							row_number = snowflakecolumn.getAsInt();
							snowrownbrs[snowRowIndex++] = row_number;

						}

					}

					i++;
				}
				// make bulk call....
				// initializing the cipher for encrypt operation
				encryptCipher.init(Cipher.ENCRYPT_MODE, key, spec[0]);

				// Map to store exceptions while encryption
				Map<Integer, String> encryptedErrorMap = new HashMap<Integer, String>();

				// performing bulk operation
				byte[][] encryptedData = encryptCipher.doFinalBulk(data, spec, encryptedErrorMap);

				for (Map.Entry<Integer, String> entry : encryptedErrorMap.entrySet()) {
					Integer mkey = entry.getKey();
					String mvalue = entry.getValue();
					encryptedErrorMapTotal.put(mkey, mvalue);
				}

				for (int enc = 0; enc < encryptedData.length; enc++) {

					snowflakereturndatasc.append("[");
					snowflakereturndatasc.append(snowrownbrs[enc]);
					snowflakereturndatasc.append(",");
					snowflakereturndatasc.append(new String(encryptedData[enc]));

					if (index <= batchsize - 1 || index < totalRowsLeft - 1)
					// if (index < batchsize -1 && index < totalRowsLeft -1 )
					{
						if (totalRowsLeft -1 > 0)
							snowflakereturndatasc.append("],");
						else
							snowflakereturndatasc.append("]");
					} else {
			 
						snowflakereturndatasc.append("]");
					}

					index++;
					totalRowsLeft--;

				}

				// totalRowsLeft = snowflakedata.size() - i;

			}

			snowflakereturndatasc.append("] }");
			// snowflakereturndatasb.append(new Gson().toJson(snowflakereturndatasc));
			snowflakereturndatasb.append(snowflakereturndatasc);
			snowflakereturndatasb.append("}");

			snowflakereturnstring = new String(snowflakereturndatasb);

			//System.out.println("string  = " + snowflakereturnstring);

		} catch (

		Exception e) {
			statusCode = 400;
			for (Map.Entry<Integer, String> entry : encryptedErrorMapTotal.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error records ");
				System.out.println("Key=" + mkey + ", Value=" + mvalue);
			}

			String errormsg = "\"something went wrong\"";
			snowflakereturndatasb.append("{ \"statusCode\":");
			snowflakereturndatasb.append(statusCode);
			snowflakereturndatasb.append(",");
			snowflakereturndatasb.append(" \"body\": { ");
			snowflakereturndatasb.append(" \"data\": [");
			snowflakereturndatasb.append("] }}");

			System.out.println("in exception with ");
			e.printStackTrace(System.out);
		}

		JsonObject inputObj = gson.fromJson(snowflakereturnstring, JsonObject.class);

		// Create the desired format
		JsonObject formattedObj = new JsonObject();
		formattedObj.addProperty("statusCode", inputObj.get("statusCode").getAsInt());

		JsonObject bodyObj = new JsonObject();
		JsonArray dataArray = inputObj.getAsJsonObject("body").getAsJsonArray("data");
		bodyObj.add("data", dataArray);

		formattedObj.addProperty("body", bodyObj.toString());

		// Convert to formatted JSON string
		String formattedJson = gson.toJson(formattedObj);

		outputStream.write(formattedJson.getBytes());

	}
=======
package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
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
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

/* This sample AWS Lambda Function is used to implement a Snowflake Database User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.
*   
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.8 & CADP 8.13
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
 *@author  mwarner
 */

public class LambdaRequestStreamHandlerCharEncryptBulkFPE implements RequestStreamHandler {

	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;
	private static Integer[] snowrownbrs;

	private static int BATCHLIMIT = 10000;

//	private static final Logger logger = Logger.getLogger(LambdaRequestStreamHandlerCharEncryptBulkFPE.class.getName());
	private static final Gson gson = new Gson();

	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
		context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");

		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();
		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonObject body = null;
		int statusCode = 200;

		// https://www.baeldung.com/java-aws-lambda

		JsonObject snowflakeinput = null;

		JsonArray snowflakedata = null;
		StringBuffer snowflakereturndatasb = new StringBuffer();
		StringBuffer snowflakereturndatasc = new StringBuffer();

		try {

			String keyName = "testfaas";
			// String keyName = System.getenv("CMKEYNAME");
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");
			int batchsize = 1000;
			// int batchsize = System.getenv("BATCHSIZE");
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			snowrownbrs = new Integer[batchsize];

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
					//System.out.println("bodystr after replace" + bodystr);
					body = gson.fromJson(bodystr, JsonObject.class);
					snowflakedata = body.getAsJsonArray("data");
				} else {
					System.out.println("eerror");

				}
			}
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

			NAESession session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			int row_number = 0;

			snowflakereturndatasb = new StringBuffer();
			// Serialization
			snowflakereturndatasb.append("{ \"statusCode\":");
			snowflakereturndatasb.append(statusCode);
			snowflakereturndatasb.append(",");
			snowflakereturndatasb.append(" \"body\":  ");
			snowflakereturndatasc.append("{ \"data\": [");
			String algorithm = "FPE/FF1/CARD62";
			// String algorithm = "AES/CBC/PKCS5Padding";

			AbstractNAECipher encryptCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			int i = 0;

			int totalRowsLeft = snowflakedata.size();

			while (i < snowflakedata.size()) {
				int index = 0;
				int dataIndex = 0;
				int specIndex = 0;
				int snowRowIndex = 0;
				//System.out.println("totalRowsLeft begining =" + totalRowsLeft);
				if (totalRowsLeft < batchsize) {
					spec = new FPEParameterAndFormatSpec[totalRowsLeft];
					data = new byte[totalRowsLeft][];
					snowrownbrs = new Integer[totalRowsLeft];
				} else {
					spec = new FPEParameterAndFormatSpec[batchsize];
					data = new byte[batchsize][];
					snowrownbrs = new Integer[batchsize];
				}

				for (int b = 0; b < batchsize && b < totalRowsLeft; b++) {

					JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

					for (int j = 0; j < snowflakerow.size(); j++) {

						JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
						System.out.print(snowflakecolumn + " ");
						String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
						// get a cipher
						if (j == 1) {

							// FPE example
							data[dataIndex++] = sensitive.getBytes();
							spec[specIndex++] = new FPEParameterAndFormatBuilder(tweakData)
									.set_tweakAlgorithm(tweakAlgo).build();
						} else {

							row_number = snowflakecolumn.getAsInt();
							snowrownbrs[snowRowIndex++] = row_number;

						}

					}

					i++;
				}
				// make bulk call....
				// initializing the cipher for encrypt operation
				encryptCipher.init(Cipher.ENCRYPT_MODE, key, spec[0]);

				// Map to store exceptions while encryption
				Map<Integer, String> encryptedErrorMap = new HashMap<Integer, String>();

				// performing bulk operation
				byte[][] encryptedData = encryptCipher.doFinalBulk(data, spec, encryptedErrorMap);

				for (Map.Entry<Integer, String> entry : encryptedErrorMap.entrySet()) {
					Integer mkey = entry.getKey();
					String mvalue = entry.getValue();
					encryptedErrorMapTotal.put(mkey, mvalue);
				}

				for (int enc = 0; enc < encryptedData.length; enc++) {

					snowflakereturndatasc.append("[");
					snowflakereturndatasc.append(snowrownbrs[enc]);
					snowflakereturndatasc.append(",");
					snowflakereturndatasc.append(new String(encryptedData[enc]));

					if (index <= batchsize - 1 || index < totalRowsLeft - 1)
					// if (index < batchsize -1 && index < totalRowsLeft -1 )
					{
						if (totalRowsLeft -1 > 0)
							snowflakereturndatasc.append("],");
						else
							snowflakereturndatasc.append("]");
					} else {
			 
						snowflakereturndatasc.append("]");
					}

					index++;
					totalRowsLeft--;

				}

				// totalRowsLeft = snowflakedata.size() - i;

			}

			snowflakereturndatasc.append("] }");
			// snowflakereturndatasb.append(new Gson().toJson(snowflakereturndatasc));
			snowflakereturndatasb.append(snowflakereturndatasc);
			snowflakereturndatasb.append("}");

			snowflakereturnstring = new String(snowflakereturndatasb);

			//System.out.println("string  = " + snowflakereturnstring);

		} catch (

		Exception e) {
			statusCode = 400;
			for (Map.Entry<Integer, String> entry : encryptedErrorMapTotal.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error records ");
				System.out.println("Key=" + mkey + ", Value=" + mvalue);
			}

			String errormsg = "\"something went wrong\"";
			snowflakereturndatasb.append("{ \"statusCode\":");
			snowflakereturndatasb.append(statusCode);
			snowflakereturndatasb.append(",");
			snowflakereturndatasb.append(" \"body\": { ");
			snowflakereturndatasb.append(" \"data\": [");
			snowflakereturndatasb.append("] }}");

			System.out.println("in exception with ");
			e.printStackTrace(System.out);
		}

		JsonObject inputObj = gson.fromJson(snowflakereturnstring, JsonObject.class);

		// Create the desired format
		JsonObject formattedObj = new JsonObject();
		formattedObj.addProperty("statusCode", inputObj.get("statusCode").getAsInt());

		JsonObject bodyObj = new JsonObject();
		JsonArray dataArray = inputObj.getAsJsonObject("body").getAsJsonArray("data");
		bodyObj.add("data", dataArray);

		formattedObj.addProperty("body", bodyObj.toString());

		// Convert to formatted JSON string
		String formattedJson = gson.toJson(formattedObj);

		outputStream.write(formattedJson.getBytes());

	}
>>>>>>> a670442e5a1de13cfea5ce47babcb7c4e387b4ca
}