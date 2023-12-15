package com.example;

import javax.crypto.Cipher;
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
 * 
 *@author  mwarner
 * 
 */
public class ThalesGCPSnowCADPCharEncryptFPE implements HttpFunction {
//  @Override

	private static final Logger logger = Logger.getLogger(ThalesGCPSnowCADPCharEncryptFPE.class.getName());
	private static final Gson gson = new Gson();

	public void service(HttpRequest request, HttpResponse response) throws Exception {

		String encdata = "";
		String tweakAlgo = null;
		String tweakData = null;
		String snowflakereturnstring = null;

		try {

			String keyName = "testfaas";
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");
			JsonArray snowflakedata = null;

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
			// String algorithm = "AES/CBC/PKCS5Padding";
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");

			for (int i = 0; i < snowflakedata.size(); i++) {
				JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();
				snowflakereturndata.append("[");
				for (int j = 0; j < snowflakerow.size(); j++) {

					JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
					String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
					// get a cipher
					if (j == 1) {

						// FPE example

						// initialize cipher to encrypt.
						encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
						// encrypt data
						byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());
						encdata = new String(outbuf);

						snowflakereturndata.append(encdata);

					} else {
						row_number = snowflakecolumn.getAsInt();
						snowflakereturndata.append(row_number);
						snowflakereturndata.append(",");
					}

				}
				if (snowflakedata.size() == 1 || i == snowflakedata.size() - 1)
					snowflakereturndata.append("]");
				else
					snowflakereturndata.append("],");

			}

			snowflakereturndata.append("]}");

			snowflakereturnstring = new String(snowflakereturndata);
			System.out.println("string  = " + snowflakereturnstring);
			// System.out.println(new Gson().toJson(snowflakereturnstring));

		} catch (Exception e) {
			// return "check exception";
		}

		response.getWriter().write(snowflakereturnstring);
		// response.getWriter().write(new Gson().toJson(snowflakereturnstring));
	}
}