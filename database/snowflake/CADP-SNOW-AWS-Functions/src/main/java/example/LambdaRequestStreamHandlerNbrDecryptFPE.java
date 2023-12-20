package example;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import javax.crypto.Cipher;
import org.apache.commons.io.IOUtils;
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
@author  mwarner
 * 
 */

public class LambdaRequestStreamHandlerNbrDecryptFPE implements  RequestStreamHandler {
//	private static final Logger logger = Logger.getLogger(LambdaRequestStreamHandlerCharEncryptFPE.class.getName());
	private static final Gson gson = new Gson();

	public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
		context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");

		//System.out.println("input  = " + input);
		// JsonParser parser = new JsonParser();

		String decData = "";
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
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");

			JsonElement rootNode = JsonParser.parseString(input).getAsJsonObject();
			if (rootNode.isJsonObject()) {
				snowflakeinput = rootNode.getAsJsonObject();
				if (snowflakeinput.isJsonObject()) {
					//For some reason when using snowflake it adds \n and \ to quotes in json.  
					// the JsonParser.parseString(input).getAsJsonObject(); is supposed to remove all of those
					//characters but it does not do it for snowflake json.  
					JsonElement bodyele = snowflakeinput.get("body");
					String bodystr = bodyele.getAsString().replaceAll(System.lineSeparator(),"");
					System.out.println("bodystr before replace" + bodystr );
					bodystr = bodystr.replaceAll("\\\\", "");
					System.out.println("bodystr after replace" + bodystr );
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
		//	NAESecureRandom rng = new NAESecureRandom(session);

		//	byte[] iv = new byte[16];
		//	rng.nextBytes(iv);
		//	IvParameterSpec ivSpec = new IvParameterSpec(iv);
			System.out.println("Key Name is : " + key.getName());
			int row_number = 0;

			snowflakereturndatasb = new StringBuffer();
			// Serialization
			snowflakereturndatasb.append("{ \"statusCode\":");
			snowflakereturndatasb.append(statusCode);
			snowflakereturndatasb.append(",");
			snowflakereturndatasb.append(" \"body\":  ");
			snowflakereturndatasc.append("{ \"data\": [");
			String algorithm = "FPE/FF1/CARD10";
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			///
		//	ivSpec = param;
			Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");

			for (int i = 0; i < snowflakedata.size(); i++) {
				JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();
				snowflakereturndatasc.append("[");
				for (int j = 0; j < snowflakerow.size(); j++) {

					JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
					String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
					
		//			boolean isNumber = StringUtils.isNumeric(sensitive);
					// get a cipher
					if (j == 1) {

						// FPE example
						// initialize cipher to encrypt.
						decryptCipher.init(Cipher.DECRYPT_MODE, key, param);
						// encrypt data
						byte[] outbuf = decryptCipher.doFinal(sensitive.getBytes());
						decData = new String(outbuf);

						snowflakereturndatasc.append(decData);

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
			System.out.println("snowflakereturnstring  " + snowflakereturnstring);

		} catch (Exception e) {
			statusCode = 400;
			String errormsg = "\"something went wrong, fix it\"";
			snowflakereturndatasb.append("{ \"statusCode\":");
			snowflakereturndatasb.append(statusCode);
			snowflakereturndatasb.append(",");
			snowflakereturndatasb.append(" \"body\": {");
			snowflakereturndatasb.append(" \"data\": [");
			snowflakereturndatasb.append("] }}");
			System.out.println("in exception with ");
			e.printStackTrace(System.out);
		}
			outputStream.write(snowflakereturnstring.getBytes());

	}
}