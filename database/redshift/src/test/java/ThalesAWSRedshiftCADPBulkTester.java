


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
	private static Integer[] redshiftrownbrs;

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
	* Examples:
	* select thales_token_cadp_char(eventname) as enceventname  , eventname from event where len(eventname) > 5
	*
	* @param is any column in the database or any value that needs to be encrypted.  Mostly used for ELT processes.  
	*/
	
	public void handleRequest(String inputStream, OutputStream outputStream, Context context) throws IOException {
		 
		String input = inputStream;
		JsonParser parser = new JsonParser();

		Map<Integer, String> encryptedErrorMapTotal = new HashMap<Integer, String>();
		String redshiftreturnstring = null;
		// https://www.baeldung.com/java-aws-lambda

		JsonObject redshiftinput = null;
		JsonElement rootNode = parser.parse(input);
		JsonArray redshiftdata = null;
		if (rootNode.isJsonObject()) {
			redshiftinput = rootNode.getAsJsonObject();

			redshiftdata = redshiftinput.getAsJsonArray("arguments");
		}
		
		StringBuffer redshiftreturndatasb = new StringBuffer();
		StringBuffer redshiftreturndatasc = new StringBuffer();

		boolean status = true;
		int nbr_of_rows_json_int = 0;
		NAESession session = null;

		try {

			String keyName = "testfaas";
			String userName = System.getenv("CMUSER");
			String password = System.getenv("CMPWD");
			
			int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;
			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];
			//redshiftrownbrs = new Integer[batchsize];
			

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

			int row_number = 0;
			


			// Serialization
			redshiftreturndatasb.append("{ \"success\":");
			redshiftreturndatasb.append(status);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"num_records\":");
			redshiftreturndatasb.append(nbr_of_rows_json_int);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"results\": [");

			String algorithm = "FPE/FF1/CARD62";
			// String algorithm = "AES/CBC/PKCS5Padding";
			String tweakAlgo = null;
			String tweakData = null;
			
			AbstractNAECipher encryptCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");
			int i = 0;

			int totalRowsLeft = redshiftdata.size();
			//String encdata = "";

			while (i < redshiftdata.size()) {
				int index = 0;
				int dataIndex = 0;
				int specIndex = 0;
				int redshiftRowIndex = 0;
				//System.out.println("totalRowsLeft begining =" + totalRowsLeft);
				if (totalRowsLeft < batchsize) {
					spec = new FPEParameterAndFormatSpec[totalRowsLeft];
					data = new byte[totalRowsLeft][];
				//	redshiftrownbrs = new Integer[totalRowsLeft];
				} else {
					spec = new FPEParameterAndFormatSpec[batchsize];
					data = new byte[batchsize][];
				//	redshiftrownbrs = new Integer[batchsize];
				}

				for (int b = 0; b < batchsize && b < totalRowsLeft; b++) {

					JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();

					for (int j = 0; j < redshiftrow.size(); j++) {

						JsonPrimitive redshiftcolumn = redshiftrow.get(j).getAsJsonPrimitive();
						System.out.print(redshiftcolumn + " ");
						String sensitive = redshiftcolumn.getAsJsonPrimitive().toString();
						// get a cipher
							// FPE example
							data[dataIndex++] = sensitive.getBytes();
							spec[specIndex++] = new FPEParameterAndFormatBuilder(tweakData)
									.set_tweakAlgorithm(tweakAlgo).build();

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

					redshiftreturndatasc.append("[");
					//redshiftreturndatasc.append(redshiftrownbrs[enc]);
					//redshiftreturndatasc.append(",");
					redshiftreturndatasc.append(new String(encryptedData[enc]));

					if (index <= batchsize - 1 || index < totalRowsLeft - 1)
					// if (index < batchsize -1 && index < totalRowsLeft -1 )
					{
						if (totalRowsLeft -1 > 0)
							redshiftreturndatasc.append("],");
						else
							redshiftreturndatasc.append("]");
					} else {
			 
						redshiftreturndatasc.append("]");
					}

					index++;
					totalRowsLeft--;

				}

				// totalRowsLeft = redshiftdata.size() - i;

			}

			redshiftreturndatasc.append("] }");
			redshiftreturndatasb.append(redshiftreturndatasc);
			redshiftreturndatasb.append("}");

			redshiftreturnstring = new String(redshiftreturndatasb);


		} catch (

		Exception e) {
			status = false;
			String errormsg = "\"something went wrong, fix it\"";
			redshiftreturndatasb.append("{ \"success\":");
			redshiftreturndatasb.append(status);
			redshiftreturndatasb.append(" \"num_records\":");
			redshiftreturndatasb.append(0);
			// redshiftreturndata.append(nbr_of_rows_json_int);
			redshiftreturndatasb.append(",");
			redshiftreturndatasb.append(" \"error_msg\":");
			redshiftreturndatasb.append(errormsg);
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

		System.out.println("string  = " + redshiftreturnstring);
		// outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());
	}

	@Override
	public void handleRequest(InputStream input, OutputStream output, Context context) throws IOException {
		// TODO Auto-generated method stub
		
	}
}