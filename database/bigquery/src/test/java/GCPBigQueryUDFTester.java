
import javax.crypto.Cipher;
import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.ingrian.security.nae.AbstractNAECipher;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
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
import com.google.gson.JsonParser;

import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class GCPBigQueryUDFTester {
//  @Override
	/* This test app to test the logic for a BigQuery Database User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
	 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
	 * data so applications or business intelligence tools do not have to change in order to use these columns.  There is no need to deploy a function to run it. 
	*  
	*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
	*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
	*  Was tested with CM 2.11 & CADP 8.13
	*  For more information on CADP see link below. 
	https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
	 * 
	 *@author  mwarner
	 * 
	 */

	private static final Logger logger = Logger.getLogger(GCPBigQueryUDFTester.class.getName());
	private static final Gson gson = new Gson();
	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;

	private static int BATCHLIMIT = 10000;

	public static void main(String[] args) throws Exception

	{
		GCPBigQueryUDFTester nw2 = new GCPBigQueryUDFTester();

		String request = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"char\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"David Cullen\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";

		String response = null;
		nw2.service(request, response);

	}

	public void service(String request, String response) throws Exception {

		String keyName = "testfaas";

		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");

		Map<Integer, String> thalesErrorMapTotal = new HashMap<Integer, String>();
		String tweakAlgo = null;
		String tweakData = null;
		StringBuffer bigqueryreturndatasc = new StringBuffer();

		String bigqueryreturnstring = null;
		StringBuffer bigqueryreturndata = new StringBuffer();

		// Optional<String> parm = request.getFirstQueryParameter("parm");

		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		String mode = null;
		String datatype = null;

		try {

			JsonObject requestJson = null;
			try {
				JsonElement requestParsed = gson.fromJson(request, JsonElement.class);

				if (requestParsed != null && requestParsed.isJsonObject()) {
					requestJson = requestParsed.getAsJsonObject();
				}

				if (requestJson != null && requestJson.has("sessionUser")) {
					bigquerysessionUser = requestJson.get("sessionUser").getAsString();
					System.out.println("name " + bigquerysessionUser);
				}

				if (requestJson != null && requestJson.has("userDefinedContext")) {
					bigqueryuserDefinedContext = requestJson.get("userDefinedContext");
					System.out.println("userDefinedContext " + bigqueryuserDefinedContext);
					JsonObject location = requestJson.getAsJsonObject("userDefinedContext");

					mode = location.get("mode").getAsString();
					System.out.println("mode is " + mode);
					datatype = location.get("datatype").getAsString();
					System.out.println("datatype is " + datatype);
				}

			} catch (JsonParseException e) {
				logger.severe("Error parsing JSON: " + e.getMessage());
			}

			int batchsize = 2;
			// int batchsize = System.getenv("BATCHSIZE");
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];

			JsonArray bigquerydata = requestJson.getAsJsonArray("calls");
			// System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			NAESession session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			// Serialization

			bigqueryreturndata.append("{ \"replies\": [");

			int cipherType = 0;
			String algorithm = "FPE/FF1/CARD62";

			if (mode.equals("encrypt"))
				cipherType = Cipher.ENCRYPT_MODE;
			else
				cipherType = Cipher.DECRYPT_MODE;
			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else
				algorithm = "FPE/FF1/CARD10";

			// String algorithm = "AES/CBC/PKCS5Padding";

			AbstractNAECipher thalesCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			int i = 0;

			int totalRowsLeft = bigquerydata.size();

			while (i < bigquerydata.size()) {
				System.out.println("while loop " + i);
				int dataIndex = 0;
				int specIndex = 0;
				int index = 0;

				// System.out.println("totalRowsLeft begining =" + totalRowsLeft);
				if (totalRowsLeft < batchsize) {
					spec = new FPEParameterAndFormatSpec[totalRowsLeft];
					data = new byte[totalRowsLeft][];

				} else {
					spec = new FPEParameterAndFormatSpec[batchsize];
					data = new byte[batchsize][];

				}

				for (int b = 0; b < batchsize && b < totalRowsLeft; b++) {
					System.out.println("first loop " + b);
					System.out.println("totalRowsLeft " + totalRowsLeft);
					JsonArray bigqueryrow = bigquerydata.get(i).getAsJsonArray();
					System.out.println("bigqueryrow " + bigqueryrow.size());
					// for (int j = 0; j < bigqueryrow.size(); j++) {
					// System.out.println("second loop " + j);
					// System.out.println("dataIndex " + dataIndex);
					String sensitive = bigqueryrow.getAsString();

					data[dataIndex++] = sensitive.getBytes();
					spec[specIndex++] = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
							.build();

					// }

					i++;
				}
				// make bulk call....
				// initializing the cipher for decrypt operation
				thalesCipher.init(cipherType, key, spec[0]);

				// Map to store exceptions while encryption
				Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();

				// performing bulk operation
				byte[][] thalesReturnData = thalesCipher.doFinalBulk(data, spec, bqErrorMap);

				for (Map.Entry<Integer, String> entry : bqErrorMap.entrySet()) {
					Integer mkey = entry.getKey();
					String mvalue = entry.getValue();
					thalesErrorMapTotal.put(mkey, mvalue);
				}

				for (int loopindex = 0; loopindex < thalesReturnData.length; loopindex++) {
					// bigqueryreturndatasc.append(new String(thalesReturnData[loopindex]));
					bigqueryreturndatasc.append(new String(thalesReturnData[loopindex]));
					// bigqueryreturndata.append(new Gson().toJson(encdata));
					if (index <= batchsize - 1 || index < totalRowsLeft - 1)
					// if (index < batchsize -1 && index < totalRowsLeft -1 )
					{
						if (totalRowsLeft - 1 > 0)
							bigqueryreturndatasc.append(",");
					}

					totalRowsLeft--;
					index++;

				}

			}

			bigqueryreturndatasc.append("] }");
			bigqueryreturndata.append(bigqueryreturndatasc);
			bigqueryreturnstring = new String(bigqueryreturndata);

		} catch (

		Exception e) {

			for (Map.Entry<Integer, String> entry : thalesErrorMapTotal.entrySet()) {
				Integer mkey = entry.getKey();
				String mvalue = entry.getValue();
				System.out.println("Error records ");
				System.out.println("Key=" + mkey + ", Value=" + mvalue);
			}

			System.out.println("in exception with ");

			e.printStackTrace(System.out);
		}

		System.out.println(bigqueryreturnstring);
		String formattedString = formatString(bigqueryreturnstring);

		// Print the reformatted string
		System.out.println(formattedString);

		// response.getWriter().write(formattedString);
	}

	public static String formatString(String inputString) {
		// Split the input string to isolate the array content
		String[] parts = inputString.split("\\[")[1].split("\\]")[0].split(",");

		// Reformat the array elements to enclose them within double quotes
		StringBuilder formattedArray = new StringBuilder();
		for (String part : parts) {
			formattedArray.append("\"").append(part.trim()).append("\",");
		}

		// Build the final formatted string
		return inputString.replaceFirst("\\[.*?\\]",
				"[" + formattedArray.deleteCharAt(formattedArray.length() - 1) + "]");
	}

}