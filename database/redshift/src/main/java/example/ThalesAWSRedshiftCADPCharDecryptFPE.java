package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.logging.Logger;
import javax.crypto.Cipher;
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

/* This sample Database User Defined Function(UDF) for AWS Redshift is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.  This example encrypts data in a column or whatever
 * is passed to the function.
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.11 & and CADP 8.13 or above.  
*  For more details on how to write Redshift UDF's please see
*  https://docs.aws.amazon.com/redshift/latest/dg/udf-creating-a-lambda-sql-udf.html#udf-lambda-json
*     
 */

public class ThalesAWSRedshiftCADPCharDecryptFPE implements RequestStreamHandler {
	private static final Logger logger = Logger.getLogger(ThalesAWSRedshiftCADPCharDecryptFPE.class.getName());
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
		context.getLogger().log("Input: " + inputStream);
		String input = IOUtils.toString(inputStream, "UTF-8");
		JsonParser parser = new JsonParser();
		NAESession session = null;

		// https://www.baeldung.com/java-aws-lambda

		JsonObject redshiftinput = null;
		JsonElement rootNode = parser.parse(input);
		JsonArray redshiftdata = null;
		if (rootNode.isJsonObject()) {
			redshiftinput = rootNode.getAsJsonObject();

			redshiftdata = redshiftinput.getAsJsonArray("arguments");
		}

		String redshiftreturnstring = null;
		StringBuffer redshiftreturndata = new StringBuffer();

		boolean status = true;
		int nbr_of_rows_json_int = 0;

		try {

			String keyName = "testfaas";
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");

			JsonPrimitive nbr_of_rows_json = redshiftinput.getAsJsonPrimitive("num_records");
			String nbr_of_rows_json_str = nbr_of_rows_json.getAsJsonPrimitive().toString();
			nbr_of_rows_json_int = new Integer(nbr_of_rows_json_str);

			System.out.println("number of records " + nbr_of_rows_json_str);

			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			 session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);


			// Serialization
			redshiftreturndata.append("{ \"success\":");
			redshiftreturndata.append(status);
			redshiftreturndata.append(",");
			redshiftreturndata.append(" \"num_records\":");
			redshiftreturndata.append(nbr_of_rows_json_int);
			redshiftreturndata.append(",");
			redshiftreturndata.append(" \"results\": [");

			String algorithm = "FPE/FF1/CARD62";
			// String algorithm = "AES/CBC/PKCS5Padding";
			String tweakAlgo = null;
			String tweakData = null;
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			String encdata = "";

			for (int i = 0; i < redshiftdata.size(); i++) {
				JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

				JsonPrimitive redshiftcolumn = redshiftrow.get(0).getAsJsonPrimitive();
			 

				String sensitive = redshiftcolumn.getAsJsonPrimitive().toString();
				// initialize cipher to decrypt.
				encryptCipher.init(Cipher.DECRYPT_MODE, key, param);
				// encrypt data
				byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());
				encdata = new String(outbuf);

				redshiftreturndata.append(encdata);
				if (redshiftdata.size() == 1 || i == redshiftdata.size() - 1)
					continue;
				else
					redshiftreturndata.append(",");
			}

			redshiftreturndata.append("]}");

			redshiftreturnstring = new String(redshiftreturndata);
			System.out.println("string  = " + redshiftreturnstring);
			// System.out.println(new Gson().toJson(redshiftreturnstring));

		} catch (Exception e) {
			status = false;
			String errormsg = "\"something went wrong, fix it\"";
			redshiftreturndata.append("{ \"success\":");
			redshiftreturndata.append(status);
			redshiftreturndata.append(" \"num_records\":");
			redshiftreturndata.append(0);
			// redshiftreturndata.append(nbr_of_rows_json_int);
			redshiftreturndata.append(",");
			redshiftreturndata.append(" \"error_msg\":");
			redshiftreturndata.append(errormsg);
			// redshiftreturndata.append(",");
			//redshiftreturndata.append(" \"results\": []");
			//outputStream.write(redshiftreturnstring.getBytes());
			System.out.println("in exception with ");
			e.printStackTrace(System.out);
		}
		 finally{
				if(session!=null) {
					session.closeSession();
				}
			}
		//System.out.println("string  = " + redshiftreturnstring);
		outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());

	}
}