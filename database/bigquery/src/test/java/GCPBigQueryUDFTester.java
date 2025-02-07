
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;

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

import java.security.Security;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class GCPBigQueryUDFTester {
//  @Override
	/*
	 * This test app to test the logic for a BigQuery Database User Defined Function(UDF). It is an example of how to
	 * use Thales Cipher Trust Application Data Protection (CADP) to protect sensitive data in a column. This example
	 * uses Format Preserve Encryption (FPE) to maintain the original format of the data so applications or business
	 * intelligence tools do not have to change in order to use these columns. There is no need to deploy a function to
	 * run it. This example uses the bulk API.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts. Not production ready code. Was not
	 * tested for all possible data sizes and combinations of encryption algorithms and IV, etc. Was tested with CM 2.14
	 * & CADP 8.16 For more information on CADP see link below.
	 * https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */

	private static final Logger logger = Logger.getLogger(GCPBigQueryUDFTester.class.getName());
	
	private static final String BADDATATAG = new String("9999999999999999");
	
	private static final Gson gson = new Gson();
	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;

	private static int BATCHLIMIT = 10000;

	public static void main(String[] args) throws Exception

	{
		GCPBigQueryUDFTester nw2 = new GCPBigQueryUDFTester();

		String requestnull = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test1-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"char\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"null\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"\"\r\n" + "    ]\r\n" + "  ]\r\n" + "}";

		String request = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"char\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"Mark Warner\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"Bill Krott\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"David Cullen\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";

		String requestnbr = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"nbr\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"342523455\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"634523321\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"534678943456\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		String requestnbrbad = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"encrypt\",\r\n" + "    \"datatype\": \"nbr\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"6\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"45\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"null\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		String requestnbrbad_decrypt = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"decrypt\",\r\n" + "    \"datatype\": \"nbr\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"73986423219977837\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"91\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"5981610067947269\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		String requestdecryptnbr = "{\r\n" + "  \"requestId\": \"124ab1c\",\r\n"
				+ "  \"caller\": \"//bigquery.googleapis.com/projects/myproject/jobs/myproject:US.bquxjob_5b4c112c_17961fafeaf\",\r\n"
				+ "  \"sessionUser\": \"test-user@test-company.com\",\r\n" + "  \"userDefinedContext\": {\r\n"
				+ "    \"mode\": \"decrypt\",\r\n" + "    \"datatype\": \"charint\"\r\n" + "  },\r\n"
				+ "  \"calls\": [\r\n" + "    [\r\n" + "      \"797708908\"\r\n" + "    ],\r\n" + "    [\r\n"
				+ "      \"681479303\"\r\n" + "    ],\r\n" + "    [\r\n" + "      \"089104593101\"\r\n" + "    ]\r\n"
				+ "  ]\r\n" + "}";
		
		
		String response = null;
		nw2.service(requestdecryptnbr, response);

	}

	public void service(String request, String response) throws Exception {

		String keyName = "testfaas";

		// The following must be entered in as environment variables in the GCP Cloud Function.
		// CM User and CM Password. These can also be provided as secrets in GCP as well.
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		// returnciphertextforuserwithnokeyaccess = is a environment variable to express how data should be returned
		// when the user above does not have access to the key and if doing a
		// lookup in the userset and the user does not exist. If returnciphertextforuserwithnokeyaccess = no
		// then an error will be returned to the query, else the results set will provide ciphertext.
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		// yes,no
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");
		// usersetlookup = should a userset lookup be done on the user from Cloud DB
		// yes,no
		String usersetlookup = System.getenv("usersetlookup");
		// usersetidincm = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it is the userset in CM but could be
		// a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");
		String mode = null;
		String datatype = null;
		
		// How many records in a chunk. Testing has indicated point of diminishing returns at 100 or 200, but
		// may vary depending on size of data.
		// int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));
		int batchsize = 3;
		int numberofchunks = 0;
		JsonArray bigquerydata = null;
		String formattedString = null;
		NAESession session = null;

		Map<Integer, String> thalesErrorMapTotal = new HashMap<Integer, String>();
		Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();

		String tweakAlgo = null;
		String tweakData = null;
	
		String bigquerysessionUser = "";
		JsonElement bigqueryuserDefinedContext = null;
		JsonObject requestJson = null;
		boolean debug = true;
		int numberOfLines = 0;
		long startTime = System.currentTimeMillis();
		JsonObject bodyObject = new JsonObject();
		JsonArray dataArray = new JsonArray();
		

		try {

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
					//System.out.println("userDefinedContext " + bigqueryuserDefinedContext);
					JsonObject location = requestJson.getAsJsonObject("userDefinedContext");

					mode = location.get("mode").getAsString();
					//System.out.println("mode is " + mode);
					datatype = location.get("datatype").getAsString();
					//System.out.println("datatype is " + datatype);
				}

			} catch (JsonParseException e) {
				logger.severe("Error parsing JSON: " + e.getMessage());
			}

			bigquerydata = requestJson.getAsJsonArray("calls");
			// UserSet logic
			numberOfLines = bigquerydata.size();
			int totalRowsLeft = numberOfLines;
			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;

			spec = new FPEParameterAndFormatSpec[batchsize];
			data = new byte[batchsize][];

			if (usersetlookupbool) {
				// make sure cmuser is in Application Data Protection Clients Group

				boolean founduserinuserset = findUserInUserSet(bigquerysessionUser, userName, password, usersetID,
						userSetLookupIP);
				// System.out.println("Found User " + founduserinuserset);
				if (!founduserinuserset)
					throw new CustomException("1001, User Not in User Set", 1001);

			} else {
				usersetlookupbool = false;
			}

			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"D:\\product\\Build\\CADP_for_JAVA.properties");
			// System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			// System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
			// "CADP_for_JAVA.properties");
			// IngrianProvider builder = new Builder().addConfigFileInputStream(
			// getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			int cipherType = 0;
			String algorithm = "FPE/FF1v2/CARD62";

			if (mode.equals("encrypt"))
				cipherType = Cipher.ENCRYPT_MODE;
			else
				cipherType = Cipher.DECRYPT_MODE;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else if (datatype.equals("charint"))
				algorithm = "FPE/FF1/CARD10";
			else
				algorithm = "FPE/FF1/CARD10";

			// String algorithm = "AES/CBC/PKCS5Padding";
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			AbstractNAECipher thalesCipher = NAECipher.getInstanceForBulkData(algorithm, "IngrianProvider");

			thalesCipher.init(cipherType, key, spec[0]);

			int i = 0;
			int count = 0;
			boolean newchunk = true;
			int dataIndex = 0;
			int specIndex = 0;
			String sensitive = null;
			while (i < numberOfLines) {

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

				JsonArray bigqueryrow = bigquerydata.get(i).getAsJsonArray();
				sensitive = checkValid(bigqueryrow);

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

					System.out.println("not valid or null");
				} else {
					data[dataIndex++] = sensitive.getBytes();
					spec[specIndex++] = param;
				}

				if (count == batchsize - 1) {

					// Map to store exceptions while encryption
					bqErrorMap = new HashMap<Integer, String>();

					// performing bulk operation
					byte[][] thalesReturnData = thalesCipher.doFinalBulk(data, spec, bqErrorMap);

					for (Map.Entry<Integer, String> entry : bqErrorMap.entrySet()) {
						Integer mkey = entry.getKey();
						String mvalue = entry.getValue();
						thalesErrorMapTotal.put(mkey, mvalue);
					}

					for (int loopindex = 0; loopindex < thalesReturnData.length; loopindex++) {
						dataArray.add(new String(thalesReturnData[loopindex]));
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
				byte[][] thalesReturnData = thalesCipher.doFinalBulk(data, spec, bqErrorMap);
				for (int loopindex = 0; loopindex < thalesReturnData.length; loopindex++) {
					dataArray.add(new String(thalesReturnData[loopindex]));
				}
			}
			
			
			bodyObject.add("replies", dataArray);
			formattedString = bodyObject.toString();
			
		} catch (

		Exception e) {
			System.out.println("in exception with " + e.getMessage());
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					JsonObject result = new JsonObject();
					JsonArray replies = new JsonArray();
					for (int i = 0; i < bigquerydata.size(); i++) {
						JsonArray innerArray = bigquerydata.get(i).getAsJsonArray();
						replies.add(innerArray.get(0).getAsString());
					}
					result.add("replies", replies);
					formattedString = result.toString();

				} else {

					for (Map.Entry<Integer, String> entry : thalesErrorMapTotal.entrySet()) {
						Integer mkey = entry.getKey();
						String mvalue = entry.getValue();
						System.out.println("Error records ");
						System.out.println("Key=" + mkey + ", Value=" + mvalue);
					}

					System.out.println("in exception with ");

					e.printStackTrace(System.out);

				}

			} else {

				for (Map.Entry<Integer, String> entry : thalesErrorMapTotal.entrySet()) {
					Integer mkey = entry.getKey();
					String mvalue = entry.getValue();
					System.out.println("Error records ");
					System.out.println("Key=" + mkey + ", Value=" + mvalue);
				}

				System.out.println("in exception with ");

				e.printStackTrace(System.out);

			}

		} finally {
			if (session != null) {
				session.closeSession();
			}
		}
		long endTime = System.currentTimeMillis();
		long totalTime = endTime - startTime;

		System.out.println("Time taken For CADP BULK test: " + totalTime + " milliseconds");
		System.out.println("Total Records: " + numberOfLines);
		System.out.println("Number of chunks: " + numberofchunks);
		System.out.println("Batch Size: " + batchsize);
		// Print the reformatted string

		System.out.println("Output " + formattedString);

		// response.getWriter().write(formattedString);
	}

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

	}

	public String checkValid(JsonArray bigquerytrow) {
		String inputdata = null;
		String notvalid = "notvalid";
		if (bigquerytrow != null && bigquerytrow.size() > 0) {
			JsonElement element = bigquerytrow.get(0);
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