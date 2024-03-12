

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import javax.crypto.Cipher;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;

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

/* This test app to test the logic for a Snowflake Database User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
 * data so applications or business intelligence tools do not have to change in order to use these columns.  There is no need to deploy a function to run it.
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.11 & CADP 8.13
*  For more information on CADP see link below. 
https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
*  For more information on Snowflake External Functions see link below. 
https://docs.snowflake.com/en/sql-reference/external-functions-creating-aws
 * 
 */

public class AWSLambdaTester implements  RequestStreamHandler {
//	private static final Logger logger = Logger.getLogger(LambdaRequestStreamHandlerCharEncryptFPE.class.getName());
	private static final Gson gson = new Gson();

public static void main(String[] args) throws Exception
	
	{
	AWSLambdaTester nw2 = new AWSLambdaTester();
		String request = "{\r\n" + 
				"  \"resource\": \"/snowflake_proxy\",\r\n" + 
				"  \"path\": \"/snowflake_proxy\",\r\n" + 
				"  \"httpMethod\": \"POST\",\r\n" + 
				"  \"headers\": {\r\n" + 
				"    \"Accept\": \"*/*\",\r\n" + 
				"    \"Accept-Encoding\": \"gzip\",\r\n" + 
				"    \"Content-Encoding\": \"gzip\",\r\n" + 
				"    \"Content-Type\": \"application/json\",\r\n" + 
				"    \"Host\": \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\",\r\n" + 
				"    \"sf-external-function-current-query-id\": \"01b02bdf-0001-7b58-0003-27d60056b5a6\",\r\n" + 
				"    \"sf-external-function-format\": \"json\",\r\n" + 
				"    \"sf-external-function-format-version\": \"1.0\",\r\n" + 
				"    \"sf-external-function-name\": \"thales-aws-lambda-snow-cadp-encrypt-nbr\",\r\n" + 
				"    \"sf-external-function-name-base64\": \"VEhBTEVTX0NBRFBfQVdTX1RPS0VOSVpFQ0hBUg==\",\r\n" + 
				"    \"sf-external-function-query-batch-id\": \"01b02bdf-0001-7b58-0003-27d60056b5a6:1:1:0:0\",\r\n" + 
				"    \"sf-external-function-return-type\": \"VARIANT\",\r\n" + 
				"    \"sf-external-function-return-type-base64\": \"VkFSSUFOVA==\",\r\n" + 
				"    \"sf-external-function-signature\": \"(B VARCHAR)\",\r\n" + 
				"    \"sf-external-function-signature-base64\": \"KEIgVkFSQ0hBUik=\",\r\n" + 
				"    \"User-Agent\": \"snowflake/1.0\",\r\n" + 
				"    \"x-amz-content-sha256\": \"550cead700c849cd6f159aca9dd81083306bb5c919939c1e2c4f3f909f32332b\",\r\n" + 
				"    \"x-amz-date\": \"20231107T142353Z\",\r\n" + 
				"    \"x-amz-security-token\": \"YOURTOKENLDqXfMA==\",\r\n" + 
				"    \"X-Amzn-Trace-Id\": \"Root=1-654a4879-4aa55d5e4a5648a0268543d1\",\r\n" + 
				"    \"X-Forwarded-For\": \"3.33.33.35\",\r\n" + 
				"    \"X-Forwarded-Port\": \"443\",\r\n" + 
				"    \"X-Forwarded-Proto\": \"https\"\r\n" + 
				"  },\r\n" + 
				"  \"multiValueHeaders\": {\r\n" + 
				"    \"Accept\": [\r\n" + 
				"      \"*/*\"\r\n" + 
				"    ],\r\n" + 
				"    \"Accept-Encoding\": [\r\n" + 
				"      \"gzip\"\r\n" + 
				"    ],\r\n" + 
				"    \"Content-Encoding\": [\r\n" + 
				"      \"gzip\"\r\n" + 
				"    ],\r\n" + 
				"    \"Content-Type\": [\r\n" + 
				"      \"application/json\"\r\n" + 
				"    ],\r\n" + 
				"    \"Host\": [\r\n" + 
				"      \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-current-query-id\": [\r\n" + 
				"      \"sdfsdfsdff-27d60056b5a6\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-format\": [\r\n" + 
				"      \"json\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-format-version\": [\r\n" + 
				"      \"1.0\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-name\": [\r\n" + 
				"      \"THALES_CADP_AWS_R\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-name-base64\": [\r\n" + 
				"      \"wewewewewewe==\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-query-batch-id\": [\r\n" + 
				"      \"01b02bdf-0001-7b58-0003-27d60056b5a6:1:1:0:0\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-return-type\": [\r\n" + 
				"      \"VARIANT\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-return-type-base64\": [\r\n" + 
				"      \"VkFSSUFOVA==\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-signature\": [\r\n" + 
				"      \"(B VARCHAR)\"\r\n" + 
				"    ],\r\n" + 
				"    \"sf-external-function-signature-base64\": [\r\n" + 
				"      \"KEIgVkFSQ0hBUik=\"\r\n" + 
				"    ],\r\n" + 
				"    \"User-Agent\": [\r\n" + 
				"      \"snowflake/1.0\"\r\n" + 
				"    ],\r\n" + 
				"    \"x-amz-content-sha256\": [\r\n" + 
				"      \"550cead70rtrtrtrtb5c919939c1e2c4f3f909f32332b\"\r\n" + 
				"    ],\r\n" + 
				"    \"x-amz-date\": [\r\n" + 
				"      \"20231107T142353Z\"\r\n" + 
				"    ],\r\n" + 
				"    \"x-amz-security-token\": [\r\n" + 
				"      \"YOURTOKENLDqXfMA==\"\r\n" + 
				"    ],\r\n" + 
				"    \"X-Amzn-Trace-Id\": [\r\n" + 
				"      \"Root=1-654a4879-4aa55d5e4a5648a0268543d1\"\r\n" + 
				"    ],\r\n" + 
				"    \"X-Forwarded-For\": [\r\n" + 
				"      \"3.34.44.35\"\r\n" + 
				"    ],\r\n" + 
				"    \"X-Forwarded-Port\": [\r\n" + 
				"      \"443\"\r\n" + 
				"    ],\r\n" + 
				"    \"X-Forwarded-Proto\": [\r\n" + 
				"      \"https\"\r\n" + 
				"    ]\r\n" + 
				"  },\r\n" + 
				"  \"queryStringParameters\": null,\r\n" + 
				"  \"multiValueQueryStringParameters\": null,\r\n" + 
				"  \"pathParameters\": null,\r\n" + 
				"  \"stageVariables\": null,\r\n" + 
				"  \"requestContext\": {\r\n" + 
				"    \"resourceId\": \"erw8lc\",\r\n" + 
				"    \"resourcePath\": \"/snowflake_proxy\",\r\n" + 
				"    \"httpMethod\": \"POST\",\r\n" + 
				"    \"extendedRequestId\": \"OCBC9FLtiYcEThQ=\",\r\n" + 
				"    \"requestTime\": \"07/Nov/2023:14:23:53 +0000\",\r\n" + 
				"    \"path\": \"/test/snowflake_proxy\",\r\n" + 
				"    \"accountId\": \"455555555564\",\r\n" + 
				"    \"protocol\": \"HTTP/1.1\",\r\n" + 
				"    \"stage\": \"test\",\r\n" + 
				"    \"domainPrefix\": \"asdfsdfsfff\",\r\n" + 
				"    \"requestTimeEpoch\": 1699367033023,\r\n" + 
				"    \"requestId\": \"f53460af-d302-4e3a-b837-f5a9785badcb\",\r\n" + 
				"    \"identity\": {\r\n" + 
				"      \"cognitoIdentityPoolId\": null,\r\n" + 
				"      \"accountId\": \"34343434\",\r\n" + 
				"      \"cognitoIdentityId\": null,\r\n" + 
				"      \"caller\": \"ARODFDFDFFDFDFX7G:snowflake\",\r\n" + 
				"      \"sourceIp\": \"3.33.44.35\",\r\n" + 
				"      \"principalOrgId\": null,\r\n" + 
				"      \"accessKey\": \"FAKE\",\r\n" + 
				"      \"cognitoAuthenticationType\": null,\r\n" + 
				"      \"cognitoAuthenticationProvider\": null,\r\n" + 
				"      \"userArn\": \"arn:aws:sts::496484342764:assumed-role/snowflakerole/snowflake\",\r\n" + 
				"      \"userAgent\": \"snowflake/1.0\",\r\n" + 
				"      \"user\": \"ADFDFDFFG:snowflake\"\r\n" + 
				"    },\r\n" + 
				"    \"domainName\": \"asdfsdfsfff.execute-api.us-east-2.amazonaws.com\",\r\n" + 
				"    \"apiId\": \"asdfsdfsfff\"\r\n" + 
				"  },\r\n" + 
				"  \"body\": \"{\\n\\\"data\\\":[\\n[0,\\\"4545554545675\\\"]\\n]\\n}\",\r\n" + 
				"  \"isBase64Encoded\": false\r\n" + 
				"}";

		String response = null;
		nw2.handleRequest(request, null,null);

	}

	public void handleRequest(String inputStream, OutputStream outputStream, Context context) throws IOException {

		String input = inputStream;
		String encdata = "";
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
		NAESession session = null;
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
					//System.out.println("bodystr before replace" + bodystr );
					bodystr = bodystr.replaceAll("\\\\", "");
					//System.out.println("bodystr after replace" + bodystr );
					body = gson.fromJson(bodystr, JsonObject.class);
					snowflakedata = body.getAsJsonArray("data");
				} else {
					System.out.println("eerror");

				}
			}


			//System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

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
	//		ivSpec = param;
			Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");

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
						encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
						// encrypt data
						byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());
						encdata = new String(outbuf);

						snowflakereturndatasc.append(encdata);

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
		finally{
			if(session!=null) {
				session.closeSession();
			}
		}
		System.out.println("results" + snowflakereturnstring);
			//outputStream.write(snowflakereturnstring.getBytes());

	}

	@Override
	public void handleRequest(InputStream input, OutputStream output, Context context) throws IOException {
		// TODO Auto-generated method stub
		
	}
}