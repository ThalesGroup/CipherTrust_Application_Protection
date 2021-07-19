/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

/**
 * This sample shows how to upload file to AWS(Amazon web server) S3 server
 * using Safenet cloud web services. In this sample we show how to use using
 * Http Client. User can use any other client it wants to.
 * 
 * User should take care of the parameter used in this sample. If any other
 * client is used then parameter name should be same.
 * 
 */
public class FileUpload {

	public static void main(String[] args) {
		
		Map<String, String> inputs = readArguments(args);
		validateProperties(inputs);

		CloseableHttpClient httpClient = HttpClients.createDefault();
		HttpPost httppost = new HttpPost(inputs.get("url"));

		try {
			HttpEntity reqEntity = createEntity(inputs);
			
			httppost.setEntity(reqEntity);
			HttpResponse response = httpClient.execute(httppost);
			HttpEntity resEntity = response.getEntity();
			System.out.println(EntityUtils.toString(resEntity));
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (httpClient != null) {
				try {
					httpClient.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}
	
	private static HttpEntity createEntity(Map<String, String> inputs) {
		HttpEntity reqEntity = null;
		if (inputs.get("certPassword") != null && inputs.get("alias") != null) {
			 reqEntity = MultipartEntityBuilder.create()
						.addTextBody("accessKey", inputs.get("awsKey"))
						// AWS access key
						.addTextBody("secretKey", inputs.get("awsSecretKey"))
						// AWS secret key
						.addTextBody("bucketName", inputs.get("bucket"))
						// bucket on the AWS
								.addTextBody("region", inputs.get("region"))
					// AWS region
					.addTextBody("ksUserName", inputs.get("user"))
					// Key Manager user name
					.addTextBody("ksPassword", inputs.get("password"))
					// Key Manager password
					.addTextBody("keyName", inputs.get("key"))
					// Key name on the Key Manager
					.addTextBody("name", inputs.get("fileName"))
						// file will be stored on S3 as per this name
						.addBinaryBody("file", new File(inputs.get("filepath")), // file to be
																	// upload
								ContentType.MULTIPART_FORM_DATA, inputs.get("filepath"))
						//true if client side encryption or false for server side operation
						.addTextBody("isClientSide", inputs.get("isClientSide") == null ? "true" : inputs.get("isClientSide"))
						//for client side transformation either AES or RSA
						.addTextBody("transformation", inputs.get("transformation") == null ? "AES" : inputs.get("transformation"))
						.addTextBody("certAlias", inputs.get("alias"))
						// cert alias for
						// SSL connection towards Key Manager
						.addTextBody("certPassword", inputs.get("certPassword"))
						.addTextBody("canKeyRotate", inputs.get("canKeyRotate") == null ? "true" : inputs.get("canKeyRotate"))
						.build();
		} else {
			 reqEntity = MultipartEntityBuilder.create()
						.addTextBody("accessKey", inputs.get("awsKey"))
						// AWS access key
						.addTextBody("secretKey", inputs.get("awsSecretKey"))
						// AWS secret key
						.addTextBody("bucketName", inputs.get("bucket"))
						// bucket on the AWS
								.addTextBody("region", inputs.get("region"))
					// AWS region
					.addTextBody("ksUserName", inputs.get("user"))
					// Key Manager user name
					.addTextBody("ksPassword", inputs.get("password"))
					// Key Manager password
					.addTextBody("keyName", inputs.get("key"))
					// Key name on the Key Manager
					.addTextBody("name", inputs.get("fileName"))
						// file will be stored on S3 as per this name
						.addBinaryBody("file", new File(inputs.get("filepath")), // file to be
																	// upload
								ContentType.MULTIPART_FORM_DATA, inputs.get("filepath"))
						//true if client side encryption or false for server side operation
						.addTextBody("isClientSide", inputs.get("isClientSide") == null ? "true" : inputs.get("isClientSide"))
						//for client side transformation either AES or RSA
						.addTextBody("transformation", inputs.get("transformation") == null ? "AES" : inputs.get("transformation"))
						.addTextBody("canKeyRotate", inputs.get("canKeyRotate") == null ? "true" : inputs.get("canKeyRotate"))
						.build();
		}
		return reqEntity;
	}

	private static Map<String, String> readArguments(String[] args) {
		Map<String, String> inputs = new HashMap<String, String>();
		for (String arg : args) {
			String[] temp = arg.split("=");
			System.out.println(Arrays.toString(temp));
			inputs.put(temp[0], temp[1]);
		}
		return inputs;
	}
	
	private static void validateProperties(
			Map<String, String> input) {
		StringBuffer buffer = new StringBuffer();
		if (input.get("url") == null) {
			buffer.append("url");
			buffer.append(", ");
		}  

		if (input.get("awsKey") == null) {
			buffer.append("awsKey");
			buffer.append(", ");
		}

		if (input.get("awsSecretKey") == null) {
			buffer.append("awsSecretKey");
			buffer.append(", ");
		}
		if (input.get("bucket") == null) {
			buffer.append("bucket");
			buffer.append(", ");
		}
		if (input.get("region") == null) {
			buffer.append("region");
			buffer.append(", ");
		}
		
		if (input.get("user") == null) {
			buffer.append("user");
			buffer.append(", ");
		}
		
		if (input.get("password") == null) {
			buffer.append("password");
			buffer.append(", ");
		}
		
		if (input.get("key") == null) {
			buffer.append("key");
			buffer.append(", ");
		}
		
		if (input.get("fileName") == null) {
			buffer.append("fileName");
			buffer.append(", ");
		}
		
		if (input.get("filepath") == null) {
			buffer.append("filepath");
			buffer.append(", ");
		}
		
		if (buffer.length() != 0) {
			System.err.println("java -jar FileUpload.jar url=webserviceurl awsKey=accessKey awsSecretKey=secretKey"
			 + " bucket=bucketName region=region user=KeyManagerUserName password=KeyManagerPassword"
			 + " key=keyName fileName=filename filepath=filepath  [clientSide=isClientSide] [transformation=transformation] [alias=certalias]"
			 + " [certPassword=certPassword] [canKeyRotate=canKeyRotate]");
			System.exit(-1);
		}
	}
}
