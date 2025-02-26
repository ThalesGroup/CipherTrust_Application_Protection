
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.math.BigInteger;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;


import org.apache.commons.io.IOUtils;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/* This sample AWS Lambda Function is used to implement a Snowflake Database User Defined Function(UDF).  	/*
 * It is an example of how to use Thales Cipher Trust Application Data Protection (CADP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns.
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.14 & CADP CADP 8.15.0.001
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
 * @author  mwarner
 */

public class ThalesAWSSnowCRDPFPEBulkUDFTester implements RequestStreamHandler {

	private static int BATCHLIMIT = 10000;
	private static final String BADDATATAG = new String("9999999999999999");
	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	// private static final Logger logger =
	// Logger.getLogger(LambdaRequestStreamHandlerNbrEncyrptBulkFPE.class.getName());
	private static final Gson gson = new Gson();

	public static void main(String[] args) throws Exception {
		ThalesAWSSnowCRDPFPEBulkUDFTester nw2 = new ThalesAWSSnowCRDPFPEBulkUDFTester();
		String request = "{\r\n" + "  \"resource\": \"/snowflake_proxy\",\r\n" + "  \"path\": \"/snowflake_proxy\",\r\n"
				+ "  \"httpMethod\": \"POST\",\r\n" + "  \"headers\": {\r\n" + "    \"Accept\": \"*/*\",\r\n"
				+ "    \"Accept-Encoding\": \"gzip\",\r\n" + "    \"Content-Encoding\": \"gzip\",\r\n"
				+ "    \"Content-Type\": \"application/json\",\r\n"
				+ "    \"Host\": \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\",\r\n"
				+ "    \"sf-external-function-current-query-id\": \"01b02bdf-0001-7b58-0003-27d60056b5a6\",\r\n"
				+ "    \"sf-external-function-format\": \"json\",\r\n"
				+ "    \"sf-external-function-format-version\": \"1.0\",\r\n"
				+ "    \"sf-external-function-name\": \"thales-aws-lambda-snow-cadp-encrypt-nbr\",\r\n"
				+ "    \"sf-external-function-name-base64\": \"VEhBTEVTX0NBRFBfQVdTX1RPS0VOSVpFQ0hBUg==\",\r\n"
				+ "    \"sf-external-function-query-batch-id\": \"01b02bdf-0001-7b58-0003-27d60056b5a6:1:1:0:0\",\r\n"
				+ "    \"sf-external-function-return-type\": \"VARIANT\",\r\n"
				+ "    \"sf-external-function-return-type-base64\": \"VkFSSUFOVA==\",\r\n"
				+ "    \"sf-external-function-signature\": \"(B VARCHAR)\",\r\n"
				+ "    \"sf-external-function-signature-base64\": \"KEIgVkFSQ0hBUik=\",\r\n"
				+ "    \"User-Agent\": \"snowflake/1.0\",\r\n"
				+ "    \"x-amz-content-sha256\": \"550cead700c849cd6f159aca9dd81083306bb5c919939c1e2c4f3f909f32332b\",\r\n"
				+ "    \"x-amz-date\": \"20231107T142353Z\",\r\n"
				+ "    \"x-amz-security-token\": \"IQoJb3JpZ2luX2VjEG8aCXVzLWVhc3QtMSJGMEQCICKJkvz9H9bTmSg3rRMNQYHnGeNzDyseSK3GxkGkxH6NAiBm/1kqxf5r25Z7154EYa93MaMOFIdMKS/b7MheulrJxCqHAwio//////////8BEAAaDDQ5NjQ4NDM0Mjc2NCIMCJwVrXJkl8t82Se4KtsC1mBjS4CLPcQEHJ+qRnw5HHbMTWx1DkJ6SeAjMWj/QypGy3yipoi20gY49xkbo4A0kzv7bty06Oa/VPp4id/hWdVEPVypuUQpyHKYdJAn/ZrnhvyqOMlKpGSg3157v1zPduOQOz9XvjpWC12NCaF3HAcj2/aH0DfCRacsAS+XwIWxNFOtrGbsbibrSJqFe2NqbvIbLU39cVLCD51cTMRMTXhdcRpU9JhXc8+I8+eWwsgpl823OrjwTwqDCnYs/9AY+yRCUDVjuLbKKQ+lXNWlaOMD6YfBzgNnjZZDbctx1lSMHG7HRHQrFIuZe0oKnVkbeF05CSxLBorfigKX8AF/Kyq5OhSnJPdTZKG6PbtWAub+JHaelZdEo3wDTMN04MkL+Nef+gV+g2vxejZiOc+v0HL0qXB1z2OLDqXfMm1zoACue3sYLqeK2jRjWqpEoPes7rU7jHOgkrWDgfkw7ZCpqgY6ngGFyKE++chqS6vGrZJ2e/HQL12UVqyxfT2NDRQZDA0gZmWnK5drpNJECXH9DeFcVqUnnDU77Ui5v6tXfUrq9cSOOYG68b2qCYiQ+TNkQPiMZNJmx4FYDL46RWtcxyvAMqaQz/5bhwf9W/Iw2QzYuSWj4FTC29H0eD1B5Frnq69Eg3A1A1bJ8m0LfDhT7gfK/rp7I2N0LSnYbhi2ksZU6A==\",\r\n"
				+ "    \"X-Amzn-Trace-Id\": \"Root=1-654a4879-4aa55d5e4a5648a0268543d1\",\r\n"
				+ "    \"X-Forwarded-For\": \"3.33.33.35\",\r\n" + "    \"X-Forwarded-Port\": \"443\",\r\n"
				+ "    \"X-Forwarded-Proto\": \"https\"\r\n" + "  },\r\n" + "  \"multiValueHeaders\": {\r\n"
				+ "    \"Accept\": [\r\n" + "      \"*/*\"\r\n" + "    ],\r\n" + "    \"Accept-Encoding\": [\r\n"
				+ "      \"gzip\"\r\n" + "    ],\r\n" + "    \"Content-Encoding\": [\r\n" + "      \"gzip\"\r\n"
				+ "    ],\r\n" + "    \"Content-Type\": [\r\n" + "      \"application/json\"\r\n" + "    ],\r\n"
				+ "    \"Host\": [\r\n" + "      \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-current-query-id\": [\r\n" + "      \"sdfsdfsdff-27d60056b5a6\"\r\n"
				+ "    ],\r\n" + "    \"sf-external-function-format\": [\r\n" + "      \"json\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-format-version\": [\r\n" + "      \"1.0\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-name\": [\r\n" + "      \"THALES_CADP_AWS_R\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-name-base64\": [\r\n" + "      \"wewewewewewe==\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-query-batch-id\": [\r\n"
				+ "      \"01b02bdf-0001-7b58-0003-27d60056b5a6:1:1:0:0\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-return-type\": [\r\n" + "      \"VARIANT\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-return-type-base64\": [\r\n" + "      \"VkFSSUFOVA==\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-signature\": [\r\n" + "      \"(B VARCHAR)\"\r\n" + "    ],\r\n"
				+ "    \"sf-external-function-signature-base64\": [\r\n" + "      \"KEIgVkFSQ0hBUik=\"\r\n"
				+ "    ],\r\n" + "    \"User-Agent\": [\r\n" + "      \"snowflake/1.0\"\r\n" + "    ],\r\n"
				+ "    \"x-amz-content-sha256\": [\r\n" + "      \"550cead70rtrtrtrtb5c919939c1e2c4f3f909f32332b\"\r\n"
				+ "    ],\r\n" + "    \"x-amz-date\": [\r\n" + "      \"20231107T142353Z\"\r\n" + "    ],\r\n"
				+ "    \"x-amz-security-token\": [\r\n"
				+ "      \"IQoJb3JpZ2luX2VjEG8aCXVzLWVhc3QtMSJGMEQCICKJkvz9H9bTmSg3rRMNQYHnGeNzDyseSK3GxkGkxH6NAiBm/1kqxf5r25Z7154EYa93MaMOFIdMKS/b7MheulrJxCqHAwio//////////8BEAAaDDQ5NjQ4NDM0Mjc2NCIMCJwVrXJkl8t82Se4KtsC1mBjS4CLPcQEHJ+qRnw5HHbMTWx1DkJ6SeAjMWj/QypGy3yipoi20gY49xkbo4A0kzv7bty06Oa/VPp4id/hWdVEPVypuUQpyHKYdJAn/ZrnhvyqOMlKpGSg3157v1zPduOQOz9XvjpWC12NCaF3HAcj2/aH0DfCRacsAS+XwIWxNFOtrGbsbibrSJqFe2NqbvIbLU39cVLCD51cTMRMTXhdcRpU9JhXc8+I8+eWwsgpl823OrjwTwqDCnYs/9AY+yRCUDVjuLbKKQ+lXNWlaOMD6YfBzgNnjZZDbctx1lSMHG7HRHQrFIuZe0oKnVkbeF05CSxLBorfigKX8AF/Kyq5OhSnJPdTZKG6PbtWAub+JHaelZdEo3wDTMN04MkL+Nef+gV+g2vxejZiOc+v0HL0qXB1z2OLDqXfMm1zoACue3sYLqeK2jRjWqpEoPes7rU7jHOgkrWDgfkw7ZCpqgY6ngGFyKE++chqS6vGrZJ2e/HQL12UVqyxfT2NDRQZDA0gZmWnK5drpNJECXH9DeFcVqUnnDU77Ui5v6tXfUrq9cSOOYG68b2qCYiQ+TNkQPiMZNJmx4FYDL46RWtcxyvAMqaQz/5bhwf9W/Iw2QzYuSWj4FTC29H0eD1B5Frnq69Eg3A1A1bJ8m0LfDhT7gfK/rp7I2N0LSnYbhi2ksZU6A==\"\r\n"
				+ "    ],\r\n" + "    \"X-Amzn-Trace-Id\": [\r\n"
				+ "      \"Root=1-654a4879-4aa55d5e4a5648a0268543d1\"\r\n" + "    ],\r\n"
				+ "    \"X-Forwarded-For\": [\r\n" + "      \"3.34.44.35\"\r\n" + "    ],\r\n"
				+ "    \"X-Forwarded-Port\": [\r\n" + "      \"443\"\r\n" + "    ],\r\n"
				+ "    \"X-Forwarded-Proto\": [\r\n" + "      \"https\"\r\n" + "    ]\r\n" + "  },\r\n"
				+ "  \"queryStringParameters\": null,\r\n" + "  \"multiValueQueryStringParameters\": null,\r\n"
				+ "  \"pathParameters\": null,\r\n" + "  \"stageVariables\": null,\r\n" + "  \"requestContext\": {\r\n"
				+ "    \"resourceId\": \"erw8lc\",\r\n" + "    \"resourcePath\": \"/snowflake_proxy\",\r\n"
				+ "    \"httpMethod\": \"POST\",\r\n" + "    \"extendedRequestId\": \"OCBC9FLtiYcEThQ=\",\r\n"
				+ "    \"requestTime\": \"07/Nov/2023:14:23:53 +0000\",\r\n"
				+ "    \"path\": \"/test/snowflake_proxy\",\r\n" + "    \"accountId\": \"455555555564\",\r\n"
				+ "    \"protocol\": \"HTTP/1.1\",\r\n" + "    \"stage\": \"test\",\r\n"
				+ "    \"domainPrefix\": \"asdfsdfsfff\",\r\n" + "    \"requestTimeEpoch\": 1699367033023,\r\n"
				+ "    \"requestId\": \"f53460af-d302-4e3a-b837-f5a9785badcb\",\r\n" + "    \"identity\": {\r\n"
				+ "      \"cognitoIdentityPoolId\": null,\r\n" + "      \"accountId\": \"34343434\",\r\n"
				+ "      \"cognitoIdentityId\": null,\r\n" + "      \"caller\": \"ARODFDFDFFDFDFX7G:snowflake\",\r\n"
				+ "      \"sourceIp\": \"3.33.44.35\",\r\n" + "      \"principalOrgId\": null,\r\n"
				+ "      \"accessKey\": \"FAKE\",\r\n" + "      \"cognitoAuthenticationType\": null,\r\n"
				+ "      \"cognitoAuthenticationProvider\": null,\r\n"
				+ "      \"userArn\": \"arn:aws:sts::496484342764:assumed-role/snowflakerole/snowflake\",\r\n"
				+ "      \"userAgent\": \"snowflake/1.0\",\r\n"
				+ "      \"user\": \"shawnscanlan@snowflakecomputing.com\"\r\n" + "    },\r\n"
				+ "    \"domainName\": \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\",\r\n"
				+ "    \"apiId\": \"asdfsdfsfff\"\r\n" + "  },\r\n"
				+ "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"47764370337599674\\\"]\\n,[1,\\\"9500405729277875\\\"]\\n,[2,\\\"57\\\"]\\n,[3,\\\"29330926862189\\\"]\\n,[4,\\\"909554854973\\\"]\\n]\\n}\",\r\n"
				+ "  \"isBase64Encoded\": false\r\n" + "}";

//+ "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"4545554545675\\\"]\\n,[1,\\\"124313145756\\\"]\\n,[2,\\\"584785473839\\\"]\\n,[3,\\\"32323232323232\\\"]\\n,[4,\\\"121212121212\\\"]\\n]\\n}\",\r\n"
//+ "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"47764370337599674\\\"]\\n,[1,\\\"9500405729277875\\\"]\\n,[2,\\\"57\\\"]\\n,[3,\\\"64310756511368\\\"]\\n,[4,\\\"909554854973\\\"]\\n]\\n}\",\r\n"
		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"6\\\"]\\n,[1,\\\"null\\\"]\\n,[2,\\\"49\\\"]\\n,[3,\\\"64310756511368\\\"]\\n,[4,\\\"294461560470\\\"]\\n]\\n}\",\r\n"
		// temp{"data":[[0,"1676960812748"],[1,"933211143272"],[2,"505141998387"],[3,"64310756511368"],[4,"294461560470"]]}
// reveal 1002001 temp{"data":[[0,"47764370337599674"],[1,"9500405729277875"],[2,"57"],[3,"29330926862189"],[4,"909554854973"]]}
//		 + "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"47764370337599674\\\"]\\n,[1,\\\"9500405729277875\\\"]\\n,[2,\\\"57\\\"]\\n,[3,\\\"29330926862189\\\"]\\n,[4,\\\"909554854973\\\"]\\n]\\n}\",\r\n"

//	+ "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"4\\\"]\\n,[1,\\\"12431-3145-756\\\"]\\n,[2,\\\"null\\\"]\\n,[3,\\\"\\\"]\\n,[4,\\\"121212121212\\\"]\\n]\\n}\",\r\n"
		// nw2.handleRequest(request, null, null);
		// backup

		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"454-55545-45675\\\"]\\n,[1,\\\"1243-131457-56\\\"]\\n,[2,\\\"584785473839\\\"]\\n,[3,\\\"32323232323232\\\"]\\n,[4,\\\"121212121212\\\"]\\n]\\n}\",\r\n"
		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"9500405729277875\\\"]\\n,[1,\\\"9500405729277875\\\"]\\n,[2,\\\"49\\\"]\\n,[3,\\\"64310756511368\\\"]\\n,[4,\\\"294461560470\\\"]\\n]\\n}\",\r\n"
		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"0\\\"]\\n,[1,\\\"null\\\"]\\n,[2,\\\"45\\\"]\\n,[3,\\\"32323232323232\\\"]\\n,[4,\\\"121212121212\\\"]\\n]\\n}\",\r\n"
		// temp{"data":[[0,"9500405729277875"],[1,"9500405729277875"],[2,"49"],[3,"64310756511368"],[4,"294461560470"]]}
		nw2.handleRequest2(request, null, null);
	}

	public void handleRequest2(String input, OutputStream outputStream, Context context) throws IOException {
		// context.getLogger().log("Input: " + inputStream);
		//String input = IOUtils.toString(inputStream, "UTF-8");

		Map<Integer, String> snowErrorMap = new HashMap<Integer, String>();
		String encdata = "";
		int error_count = 0;
		int statusCode = 200;

		JsonObject bodyObject = new JsonObject();
		JsonArray dataArray = new JsonArray();
		JsonArray innerDataArray = new JsonArray();
		String snowflakereturnstring = null;
		JsonObject body_input_request = null;

		int numberofchunks = 0;

		String callerStr = null;

		JsonObject snowflakeinput = null;

		JsonArray snowflakedata = null;

		String keyName = "testfaas";
		String crdpip = System.getenv("CRDPIP");
		// String keyName = System.getenv("CMKEYNAME");
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
		String keymetadatalocation = System.getenv("keymetadatalocation");
		String external_version_from_ext_source = System.getenv("keymetadata");
		String protection_profile = System.getenv("protection_profile");
		String mode = System.getenv("mode");
		String datatype = System.getenv("datatype");
		
		String showrevealkey = "yes";
		
		int batchsize = Integer.parseInt(System.getenv("BATCHSIZE"));

		String inputDataKey = null;
		String outputDataKey = null;
		String protectedData = null;
		String externalkeymetadata = null;
		String jsonBody = null;

		String jsonTagForProtectReveal = null;

		boolean bad_data = false;
		if (mode.equals("protectbulk")) {
			inputDataKey = "data_array";
			outputDataKey = "protected_data_array";
			jsonTagForProtectReveal = PROTECTRETURNTAG;
			if (keymetadatalocation.equalsIgnoreCase("internal")) {
				showrevealkey = System.getenv("showrevealinternalkey");
				if (showrevealkey == null)
					showrevealkey = "yes";
			}
		} else {
			inputDataKey = "protected_data_array";
			outputDataKey = "data_array";
			jsonTagForProtectReveal = REVEALRETURNTAG;
		}
		
		boolean showrevealkeybool = showrevealkey.equalsIgnoreCase("yes");

		try {

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
					// System.out.println("bodystr after replace" + bodystr);
					body_input_request = gson.fromJson(bodystr, JsonObject.class);
					snowflakedata = body_input_request.getAsJsonArray("data");

					JsonObject requestContext = snowflakeinput.getAsJsonObject("requestContext");

					if (requestContext != null) {
						JsonObject identity = requestContext.getAsJsonObject("identity");

						if (identity != null) {
							callerStr = identity.get("user").getAsString();
							System.out.println("user: " + callerStr);
						} else {
							System.out.println("Identity not found.");
						}
					} else {
						System.out.println("Request context not found.");
					}

					if (usersetlookupbool) { // make sure cmuser is in Application Data Protection Clients Group

						boolean founduserinuserset = findUserInUserSet(callerStr, userName, password, usersetID,
								userSetLookupIP);
						// System.out.println("Found User " + founduserinuserset);
						if (!founduserinuserset)
							throw new CustomException("1001, User Not in User Set", 1001);

					} else {
						usersetlookupbool = false;
					}

				} else {
					System.out.println("eerror");

				}
			}

			StringBuffer protection_policy_buff = new StringBuffer();
			String notvalid = "notvalid";

			int numberOfLines = snowflakedata.size();
			int totalRowsLeft = numberOfLines;

			if (batchsize > numberOfLines)
				batchsize = numberOfLines;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;

			int i = 0;
			int count = 0;
			int totalcount = 0;

			int dataIndex = 0; // assumes index from snowflake will always be sequential.
			JsonObject crdp_payload = new JsonObject();
			String sensitive = null;
			JsonArray crdp_payload_array = new JsonArray();

			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");
			String urlStr = "http://" + crdpip + ":8090/v1/" + mode;

			while (i < numberOfLines) {

				for (int b = 0; b < batchsize && b < totalRowsLeft; b++) {

					JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

					sensitive = checkValid(snowflakerow);
					protection_profile = protection_profile.trim();
					// Format the output
					String formattedElement = String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
					protection_policy_buff.append(formattedElement);
					protection_policy_buff.append(",");

					if (mode.equals("protectbulk")) {
						if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								if (sensitive.contains("notvalid")) {
									// System.out.println("adding null not charint or nbr");
									sensitive = sensitive.replace("notvalid", "");
									sensitive = BADDATATAG + sensitive;
								} else
									sensitive = BADDATATAG;

							} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {

							} else if (sensitive.contains("notvalid")) {
								// sensitive = sensitive.replace("notvalid", "");

							}
							encdata = sensitive;

						}
						crdp_payload_array.add(sensitive);
					} else {
						JsonObject protectedDataObject = new JsonObject();
						protectedDataObject.addProperty("protected_data", sensitive);
						if (keymetadatalocation.equalsIgnoreCase("external")) {
							protectedDataObject.addProperty("external_version", external_version_from_ext_source);
						}
						crdp_payload_array.add(protectedDataObject);

					}

					if (count == batchsize - 1) {
						crdp_payload.add(inputDataKey, crdp_payload_array);
						String inputdataarray = null;
						if (mode.equals("revealbulk")) {
							crdp_payload.addProperty("username", callerStr);
							inputdataarray = crdp_payload.toString();
							protection_policy_buff.append(inputdataarray);
							jsonBody = protection_policy_buff.toString();
							jsonBody = jsonBody.replaceFirst("\\{", " ");

						} else {
							inputdataarray = crdp_payload.toString();
							protection_policy_buff.append(inputdataarray);
							inputdataarray = protection_policy_buff.toString();
							jsonBody = inputdataarray.replace("{", " ");
						}
						jsonBody = "{" + jsonBody;

						// System.out.println(jsonBody);
						RequestBody body = RequestBody.create(mediaType, jsonBody);

						// System.out.println(urlStr);
						Request crdp_request = new Request.Builder().url(urlStr).method("POST", body)
								.addHeader("Content-Type", "application/json").build();
						Response crdp_response = client.newCall(crdp_request).execute();
						String crdpreturnstr = null;
						if (crdp_response.isSuccessful()) {
							// Parse JSON response
							String responseBody = crdp_response.body().string();
							JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
							JsonArray protectedDataArray = jsonObject.getAsJsonArray(outputDataKey);

							String status = jsonObject.get("status").getAsString();
							int success_count = jsonObject.get("success_count").getAsInt();
							error_count = jsonObject.get("error_count").getAsInt();
							if (error_count > 0)
								System.out.println("errors " + error_count);

							for (JsonElement element : protectedDataArray) {

								JsonObject protectedDataObject = element.getAsJsonObject();
								if (protectedDataObject.has(jsonTagForProtectReveal)) {

									protectedData = protectedDataObject.get(jsonTagForProtectReveal).getAsString();
									// System.out.println(protectedData);
									if (keymetadatalocation.equalsIgnoreCase("internal") && mode.equalsIgnoreCase("protectbulk") && !showrevealkeybool) {
										if (protectedData.length()>7) 
											protectedData = protectedData.substring(7);							 
									}
									
									innerDataArray.add(dataIndex);
									innerDataArray.add(new String(protectedData));
									dataArray.add(innerDataArray);
									innerDataArray = new JsonArray();
									if (mode.equals("protectbulk")) {
										if (keymetadatalocation.equalsIgnoreCase("external")
												&& mode.equalsIgnoreCase("protectbulk")) {
											externalkeymetadata = protectedDataObject.get("external_version")
													.getAsString();
											// System.out.println("Protected Data ext key metadata need to store this: "
											// + externalkeymetadata);

										}
									}
								} else if (protectedDataObject.has("error_message")) {
									String errorMessage = protectedDataObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									snowErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");
								dataIndex++;

							}

							crdp_payload_array = new JsonArray();
							protection_policy_buff = new StringBuffer();
							numberofchunks++;
							totalcount = totalcount + count;
							count = 0;
						} else {// throw error....
							System.err.println("Request failed with status code: " + crdp_response.code());
							throw new CustomException("1010, Unexpected Error ", 1010);
						}

					} else {
						count++;
					}
					totalRowsLeft--;
					i++;
				}
			}
			if (count > 0) {
				crdp_payload.add(inputDataKey, crdp_payload_array);
				String inputdataarray = null;
				if (mode.equals("revealbulk")) {
					crdp_payload.addProperty("username", callerStr);
					inputdataarray = crdp_payload.toString();
					protection_policy_buff.append(inputdataarray);
					jsonBody = protection_policy_buff.toString();
					jsonBody = jsonBody.replaceFirst("\\{", " ");

				} else {
					inputdataarray = crdp_payload.toString();
					protection_policy_buff.append(inputdataarray);
					inputdataarray = protection_policy_buff.toString();
					jsonBody = inputdataarray.replace("{", " ");
				}
				jsonBody = "{" + jsonBody;

				// System.out.println(jsonBody);
				RequestBody body = RequestBody.create(mediaType, jsonBody);

				// System.out.println(urlStr);
				Request crdp_request = new Request.Builder().url(urlStr).method("POST", body)
						.addHeader("Content-Type", "application/json").build();
				Response crdp_response = client.newCall(crdp_request).execute();
				String crdpreturnstr = null;
				if (crdp_response.isSuccessful()) {
					// Parse JSON response
					String responseBody = crdp_response.body().string();
					JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
					JsonArray protectedDataArray = jsonObject.getAsJsonArray(outputDataKey);

					String status = jsonObject.get("status").getAsString();
					int success_count = jsonObject.get("success_count").getAsInt();
					error_count = jsonObject.get("error_count").getAsInt();
					if (error_count > 0)
						System.out.println("errors " + error_count);

					if (mode.equals("protectbulk")) {

						for (JsonElement element : protectedDataArray) {
							JsonObject protectedDataObject = element.getAsJsonObject();
							if (protectedDataObject.has("protected_data")) {

								protectedData = protectedDataObject.get("protected_data").getAsString();

								innerDataArray.add(dataIndex);
								innerDataArray.add(new String(protectedData));
								dataArray.add(innerDataArray);
								innerDataArray = new JsonArray();

								if (keymetadatalocation.equalsIgnoreCase("external")
										&& mode.equalsIgnoreCase("protectbulk")) {
									externalkeymetadata = protectedDataObject.get("external_version").getAsString();
									// System.out.println("Protected Data ext key metadata need to store this: "
									// + externalkeymetadata);

								}
								
								if (keymetadatalocation.equalsIgnoreCase("internal") && mode.equalsIgnoreCase("protectbulk") && !showrevealkeybool) {
									if (protectedData.length()>7) 
										protectedData = protectedData.substring(7);							 
								}
								
							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								snowErrorMap.put(i, errorMessage);
								bad_data = true;
							} else {
								System.out.println("unexpected json value from results: ");
								throw new CustomException("1010, Unexpected Error ", 1010);
							}
							dataIndex++;
						}
					} else {
						// reveal logic

						for (JsonElement element : protectedDataArray) {
							JsonObject protectedDataObject = element.getAsJsonObject();
							if (protectedDataObject.has("data")) {
								protectedData = protectedDataObject.get("data").getAsString();
								// System.out.println(protectedData);

								innerDataArray.add(dataIndex);
								innerDataArray.add(new String(protectedData));
								dataArray.add(innerDataArray);
								innerDataArray = new JsonArray();

							} else if (protectedDataObject.has("error_message")) {
								String errorMessage = protectedDataObject.get("error_message").getAsString();
								System.out.println("error_message: " + errorMessage);
								snowErrorMap.put(i, errorMessage);
								bad_data = true;
							} else
								System.out.println("unexpected json value from results: ");
							dataIndex++;
						}
					}

					crdp_response.close();

					numberofchunks++;

					totalcount = totalcount + count;
					count = 0;

				} else {
					System.err.println("Request failed with status code: " + crdp_response.code());
				}
			}
			System.out.println("total chuncks " + numberofchunks);

			bodyObject.add("data", dataArray);
			JsonObject inputJsonObject = new JsonObject();
			String bodyString = bodyObject.toString();
			inputJsonObject.addProperty("statusCode", 200);
			inputJsonObject.addProperty("body", bodyString);

			snowflakereturnstring = inputJsonObject.toString();

		} catch (Exception e) {
			System.out.println("in exception with " + e.getMessage());
			snowflakereturnstring = "exception ";
			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {

					bodyObject = new JsonObject();
					dataArray = new JsonArray();
					innerDataArray = new JsonArray();
					int nbrofrows = snowflakedata.size();
					for (int i = 0; i < nbrofrows; i++) {

						JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

						for (int j = 0; j < snowflakerow.size(); j++) {
							if (j == 1) {
								// String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
								// FPE example
								String sensitive = checkValid(snowflakerow);

								if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
									if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
										if (sensitive.contains("notvalid")) {
											sensitive = sensitive.replace("notvalid", "");
										} else
											sensitive = BADDATATAG;

									} else if (sensitive.equalsIgnoreCase("null")
											|| sensitive.equalsIgnoreCase("notvalid")) {

									} else if (sensitive.contains("notvalid")) {
										sensitive = sensitive.replace("notvalid", "");

									}
									encdata = sensitive;

								} else {
									// System.out.println("normal number data" + sensitive);
								}
								innerDataArray.add(sensitive);
								dataArray.add(innerDataArray);
								innerDataArray = new JsonArray();

							} else {
								JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
								int row_number = snowflakecolumn.getAsInt();
								innerDataArray.add(row_number);
							}
						}
					}

					bodyObject.add("data", dataArray);
					JsonObject inputJsonObject = new JsonObject();
					String bodyString = bodyObject.toString();
					inputJsonObject.addProperty("statusCode", 200);
					inputJsonObject.addProperty("body", bodyString);

					snowflakereturnstring = inputJsonObject.toString();
					// System.out.println(" new data " + snowflakereturnstring);

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

		}
		 System.out.println(snowflakereturnstring);
		//outputStream.write(snowflakereturnstring.getBytes());

	}

	public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID,
			String userSetLookupIP) throws Exception {

		CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);

		String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
		String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);

		boolean founduserinuserset = cmuserset.findUserInUserSet(userName, newtoken);

		return founduserinuserset;

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

	@Override
	public void handleRequest(InputStream input, OutputStream output, Context context) throws IOException {
		// TODO Auto-generated method stub
		
	}


}