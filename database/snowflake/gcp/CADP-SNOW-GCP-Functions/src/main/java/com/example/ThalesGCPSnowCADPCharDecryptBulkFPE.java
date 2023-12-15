package com.example;

import javax.crypto.Cipher;
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
*  Was tested with CM 2.8 & CADP 8.13
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

public class ThalesGCPSnowCADPCharDecryptBulkFPE implements HttpFunction {
//  @Override
	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;
	private static Integer[] snowrownbrs;

	private static int BATCHLIMIT = 10000;
	private static final Logger logger = Logger.getLogger(ThalesGCPSnowCADPCharDecryptBulkFPE.class.getName());
	private static final Gson gson = new Gson();

	public void service(HttpRequest request, HttpResponse response) throws Exception {

		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;
		JsonArray snowflakedata = null;
		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();
		try {

			String keyName = "testfaas";
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");
			// JsonArray snowflakedata = null;
			int batchsize = 1000;
			// int batchsize = System.getenv("BATCHSIZE");
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			snowrownbrs = new Integer[batchsize];

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
			NAESession session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			int row_number = 0;

			StringBuffer snowflakereturndata = new StringBuffer();
			// Serialization
			snowflakereturndata.append("{ \"data\": [");
			String algorithm = "FPE/FF1/CARD62";

			AbstractNAECipher decryptCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			int i = 0;

			int totalRowsLeft = snowflakedata.size();
			while (i < snowflakedata.size()) {
				int index = 0;
				int dataIndex = 0;
				int specIndex = 0;
				int snowRowIndex = 0;
				// System.out.println("totalRowsLeft begining =" + totalRowsLeft);
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
						// System.out.print(snowflakecolumn + " ");
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
				decryptCipher.init(Cipher.DECRYPT_MODE, key, spec[0]);

				// Map to store exceptions while encryption
				Map<Integer, String> decryptErrorMap = new HashMap<Integer, String>();

				// performing bulk operation
				byte[][] decryptedData = decryptCipher.doFinalBulk(data, spec, decryptErrorMap);

				for (Map.Entry<Integer, String> entry : decryptErrorMap.entrySet()) {
					Integer mkey = entry.getKey();
					String mvalue = entry.getValue();
					encryptedErrorMapTotal.put(mkey, mvalue);
				}

				for (int enc = 0; enc < decryptedData.length; enc++) {

					snowflakereturndata.append("[");
					snowflakereturndata.append(snowrownbrs[enc]);
					snowflakereturndata.append(",");
					snowflakereturndata.append(new String(decryptedData[enc]));

					if (index <= batchsize - 1 || index < totalRowsLeft - 1)
					// if (index < batchsize -1 && index < totalRowsLeft -1 )
					{
						if (totalRowsLeft - 1 > 0)
							snowflakereturndata.append("],");
						else
							snowflakereturndata.append("]");
					} else {

						snowflakereturndata.append("]");
					}

					index++;
					totalRowsLeft--;

				}
			}

			snowflakereturndata.append("]}");

			snowflakereturnstring = new String(snowflakereturndata);
			System.out.println("string  = " + snowflakereturnstring);
			// System.out.println(new Gson().toJson(snowflakereturnstring));

		} catch (Exception e) {
			// return "check exception";
		}

		response.getWriter().write(snowflakereturnstring);

	}
}