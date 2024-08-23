
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
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
 * 
 */

public class ThalesAWSSnowCRDPFPEUDFTester implements RequestStreamHandler {

	private static final Gson gson = new Gson();
	private static final String BADDATATAG = new String("9999999999999999");
	private static final String REVEALRETURNTAG = new String("data");
	private static final String PROTECTRETURNTAG = new String("protected_data");

	public static void main(String[] args) throws Exception

	{
		ThalesAWSSnowCRDPFPEUDFTester nw2 = new ThalesAWSSnowCRDPFPEUDFTester();
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
				+ "      \"user\": \"AROAXHGGF3PWF4RUKPX7G:snowflake\"\r\n" + "    },\r\n"
				+ "    \"domainName\": \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\",\r\n"
				+ "    \"apiId\": \"asdfsdfsfff\"\r\n" + "  },\r\n"
				+ " \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"100300150\\\"]\\n]\\n}\",\r\n" + "  \"isBase64Encoded\": false\r\n"
				+ "}";

	//	"body":"{\"data\":[[0,\"100300150\"]]}"}
	
		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"4545554545675\\\"]\\n,[1,\\\"124313145756\\\"]\\n,[2,\\\"584785473839\\\"]\\n,[3,\\\"32323232323232\\\"]\\n,[4,\\\"121212121212\\\"]\\n]\\n}\",\r\n"
		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"47764370337599674\\\"]\\n,[1,\\\"9500405729277875\\\"]\\n,[2,\\\"57\\\"]\\n,[3,\\\"64310756511368\\\"]\\n,[4,\\\"909554854973\\\"]\\n]\\n}\",\r\n"
		// + " \"body\":
		// \"{\\n\\\"data\\\":[\\n[0,\\\"6\\\"]\\n,[1,\\\"null\\\"]\\n,[2,\\\"49\\\"]\\n,[3,\\\"64310756511368\\\"]\\n,[4,\\\"294461560470\\\"]\\n]\\n}\",\r\n"
		// temp{"data":[[0,"1676960812748"],[1,"933211143272"],[2,"505141998387"],[3,"64310756511368"],[4,"294461560470"]]}
		// reveal 1002001
		// temp{"data":[[0,"47764370337599674"],[1,"9500405729277875"],[2,"57"],[3,"29330926862189"],[4,"909554854973"]]}
//				 + "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"47764370337599674\\\"]\\n,[1,\\\"9500405729277875\\\"]\\n,[2,\\\"57\\\"]\\n,[3,\\\"29330926862189\\\"]\\n,[4,\\\"909554854973\\\"]\\n]\\n}\",\r\n"

//			+ "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"4\\\"]\\n,[1,\\\"12431-3145-756\\\"]\\n,[2,\\\"null\\\"]\\n,[3,\\\"\\\"]\\n,[4,\\\"121212121212\\\"]\\n]\\n}\",\r\n"

		// + " \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"4545554545675\\\"]\\n]\\n}\",\r\n"
//				+ "  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"4545554-5456-75\\\"]\\n]\\n}\",\r\n"
		// "body":
		// "{\n\"data\":[\n[0,\"ndorgan5@sf_tuts.com\"],\n[1,\"cdevereu6@sf_tuts.co.au\"],\n[2,\"gglaserman7@sf_tuts.com\"],\n[3,\"icasemore8@sf_tuts.com\"],\n[4,\"chovie9@sf_tuts.com\"],\n[5,\"afeatherstona@sf_tuts.com\"],\n[6,\"hanneslieb@sf_tuts.com\"],\n[7,\"bciccoc@sf_tuts.com\"],\n[8,\"bdurnalld@sf_tuts.com\"],\n[9,\"kmacconnale@sf_tuts.com\"],\n[10,\"wsizeyf@sf_tuts.com\"],\n[11,\"dmcgowrang@sf_tuts.com\"],\n[12,\"cbedderh@sf_tuts.co.au\"],\n[13,\"davoryi@sf_tuts.com\"],\n[14,\"rtalmadgej@sf_tuts.co.uk\"],\n[15,\"lboissier@sf_tuts.com\"],\n[16,\"ihanks1@sf_tuts.com\"],\n[17,\"alaudham2@sf_tuts.com\"],\n[18,\"ecornner3@sf_tuts.com\"],\n[19,\"hgoolding4@sf_tuts.com\"],\n[20,\"adavidovitsk@sf_tuts.com\"],\n[21,\"vshermorel@sf_tuts.com\"],\n[22,\"rmattysm@sf_tuts.com\"],\n[23,\"soluwatoyinn@sf_tuts.com\"],\n[24,\"gbassfordo@sf_tuts.co.uk\"]\n]\n}",
		// "isBase64Encoded": false

		// " \"user\": \"ADFDFDFFG:snowflake\"\r\n" +
		// + " \"user\": \"shawnscanlan@snowflakecomputing.com\"\r\n" + " },\r\n"
		nw2.handleRequest(request, null, null);

	}

	public void handleRequest(String inputStream, OutputStream outputStream, Context context) throws Exception {
		Map<Integer, String> bqErrorMap = new HashMap<Integer, String>();
		String encdata = "";
		String snowflakereturnstring = null;

		String input = inputStream;
		JsonObject snowflakebody = null;
		int statusCode = 200;

		// https://www.baeldung.com/java-aws-lambda
		JsonObject snowflakeinput = null;
		String callerStr = null;
		JsonArray snowflakedata = null;

		String keyName = "testfaas";
		String crdpip = System.getenv("CRDPIP");
		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		// returnciphertextforuserwithnokeyaccess = is a environment variable to express how data should be
		// returned when the user above does not have access to the key and if doing a lookup in the userset
		// and the user does not exist. If returnciphertextforuserwithnokeyaccess = no then an error will be
		// returned to the query, else the results set will provide ciphertext.
		// yes/no
		String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");

		// usersetlookup = should a userset lookup be done on the user from Cloud DB?
		// yes/no
		String usersetlookup = System.getenv("usersetlookup");
		// usersetidincm = should be the usersetid in CM to query.
		String usersetID = System.getenv("usersetidincm");
		// usersetlookupip = this is the IP address to query the userset. Currently it
		// is the userset in CM but could be a memcache or other in memory db.
		String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");
		// keymetadatalocation keymeta data can be internal or external
		String keymetadatalocation = System.getenv("keymetadatalocation");
		// keymetadata represents a 7 digit value that contains policy version and key version. example 1001001.
		// Normally would come from a database
		String external_version_from_ext_source = System.getenv("keymetadata");
		// protection_profile = the protection profile to be used for protect or reveal. This is in CM under application
		// data protection/protection profiles.
		String protection_profile = System.getenv("protection_profile");
		// mode of operation. valid values are protect/reveal
		String mode = System.getenv("mode");
		String datatype = System.getenv("datatype");

		String showrevealkey = "yes";

		String dataKey = null;
		JsonObject bodyObject = new JsonObject();
		JsonArray dataArray = new JsonArray();
		JsonArray innerDataArray = new JsonArray();
		String jsonTagForProtectReveal = null;

		boolean bad_data = false;
		
		if (mode.equals("protect")) {
			dataKey = "data";
			jsonTagForProtectReveal = PROTECTRETURNTAG;
			if (keymetadatalocation.equalsIgnoreCase("internal")) {
				showrevealkey = System.getenv("showrevealinternalkey");
				if (showrevealkey == null)
					showrevealkey = "yes";
			}
		} else {
			dataKey = "protected_data";
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
					// System.out.println("bodystr before replace" + bodystr );
					bodystr = bodystr.replaceAll("\\\\", "");
					// System.out.println("bodystr after replace" + bodystr );
					snowflakebody = gson.fromJson(bodystr, JsonObject.class);
					snowflakedata = snowflakebody.getAsJsonArray("data");
					JsonObject requestContext = snowflakeinput.getAsJsonObject("requestContext");

					if (requestContext != null) {
						JsonObject identity = requestContext.getAsJsonObject("identity");

						if (identity != null) {
							callerStr = identity.get("user").getAsString();
							// String[] parts = callerStr.split(":");
							// callerStr = parts[0];

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

			// Serialization

			String protectedData = null;
			String externalkeymetadata = null;
			String crdpjsonBody = null;
			// String external_version_from_ext_source = "1004001";
			// String external_version_from_ext_source = "1001001";
			int row_number = 0;
			JsonObject crdp_payload = new JsonObject();

			crdp_payload.addProperty("protection_policy_name", protection_profile);
			String sensitive = null;
			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");
			String urlStr = "http://" + crdpip + ":8090/v1/" + mode;
			int nbrofrows = snowflakedata.size();

			for (int i = 0; i < nbrofrows; i++) {
				JsonArray snowflakerow = snowflakedata.get(i).getAsJsonArray();

				for (int j = 0; j < snowflakerow.size(); j++) {

					if (j == 1) {
						// String sensitive = snowflakecolumn.getAsJsonPrimitive().toString();
						// FPE example
						sensitive = checkValid(snowflakerow);
						if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
							if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
								if (sensitive.contains("notvalid")) {
									sensitive = sensitive.replace("notvalid", "");
								} else
									sensitive = BADDATATAG;

							} else if (sensitive.equalsIgnoreCase("null") || sensitive.equalsIgnoreCase("notvalid")) {

							} else if (sensitive.contains("notvalid")) {
								sensitive = sensitive.replace("notvalid", "");

							}
							encdata = sensitive;

						} else {

							crdp_payload.addProperty(dataKey, sensitive);
							if (mode.equals("reveal")) {
								crdp_payload.addProperty("username", callerStr);
								if (keymetadatalocation.equalsIgnoreCase("external")) {
									crdp_payload.addProperty("external_version", external_version_from_ext_source);
								}
							}
							crdpjsonBody = crdp_payload.toString();
							System.out.println(crdpjsonBody);
							RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

							// String urlStr = "\"http://" + cmip + ":8090/v1/" + mode+ "\"";
							System.out.println(urlStr);
							Request crdp_request = new Request.Builder()
									// .url("http://192.168.159.143:8090/v1/protect").method("POST", body)
									.url(urlStr).method("POST", body).addHeader("Content-Type", "application/json")
									.build();
							Response crdp_response = client.newCall(crdp_request).execute();

							if (crdp_response.isSuccessful()) {

								// Parse JSON response
								String responseBody = crdp_response.body().string();
								Gson gson = new Gson();
								JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);

								if (jsonObject.has(jsonTagForProtectReveal)) {
									protectedData = jsonObject.get(jsonTagForProtectReveal).getAsString();
									if (keymetadatalocation.equalsIgnoreCase("external")
											&& mode.equalsIgnoreCase("protect")) {
										externalkeymetadata = jsonObject.get("external_version").getAsString();
										System.out.println("Protected Data ext key metadata need to store this: "
												+ externalkeymetadata);
									}

									if (keymetadatalocation.equalsIgnoreCase("internal")
											&& mode.equalsIgnoreCase("protect") && !showrevealkeybool) {
										if (protectedData.length() > 7)
											protectedData = protectedData.substring(7);
									}

								} else if (jsonObject.has("error_message")) {
									String errorMessage = jsonObject.get("error_message").getAsString();
									System.out.println("error_message: " + errorMessage);
									bqErrorMap.put(i, errorMessage);
									bad_data = true;
								} else
									System.out.println("unexpected json value from results: ");
							} else {
								System.err.println("Request failed with status code: " + crdp_response.code());
							}

							crdp_response.close();
//test to see if work for just  5
							encdata = protectedData;

						}

						innerDataArray.add(encdata);
						dataArray.add(innerDataArray);
						innerDataArray = new JsonArray();

					} else {
						JsonPrimitive snowflakecolumn = snowflakerow.get(j).getAsJsonPrimitive();
						row_number = snowflakecolumn.getAsInt();
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
			System.out.println(" new data " + snowflakereturnstring);

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

								sensitive = checkValid(snowflakerow);
								if (sensitive.contains("notvalid") || sensitive.equalsIgnoreCase("null")) {
									if (datatype.equalsIgnoreCase("charint") || datatype.equalsIgnoreCase("nbr")) {
										if (sensitive.contains("notvalid")) {
											System.out.println("adding null not charint or nbr");
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
									System.out.println("normal number data" + sensitive);
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
					System.out.println(" new data " + snowflakereturnstring);

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
		System.out.println("results" + snowflakereturnstring);
		// outputStream.write(snowflakereturnstring.getBytes());

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

}