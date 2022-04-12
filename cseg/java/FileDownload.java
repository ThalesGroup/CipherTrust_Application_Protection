/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpRequestBase;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

/**
 * This sample shows how to download file from AWS(Amazon web server) S3 server
 * using Safenet cloud web services. In this sample we show how to use using
 * Http Client. User can use any other client it wants to.
 * 
 * User should take care of the parameter used in this sample. If any other
 * client is used then parameter name should be same.
 * 
 * Note: To run the samples, download and add the following jars as well as CADP for JAVA jars into the java classpath:
 *	     a) httpclient-4.5.1.jar
 *	     b) httpcore-4.4.4.jar
 *	     c) httpmime-4.5.1.jar
 *	     d) commons-logging-1.1.1.jar
 * 
 */
public class FileDownload {

	public static void main(String[] args) {
		Map<String, String> inputs = readArguments(args);
		validateProperties(inputs);
		CloseableHttpClient httpClient = HttpClients.createDefault();
		HttpGet httpget = new HttpGet(inputs.get("url"));
		String destinationFile = null;

		try {
			URI uri = null;
			uri = new URIBuilder(httpget.getURI())
					.setParameter("accessKey", inputs.get("awsKey"))
					// AWS access key
					.setParameter("secretKey", inputs.get("awsSecretKey"))
					// AWS secret key
					.setParameter("bucketName", inputs.get("bucket"))
					// bucket on the
					// AWS
					.setParameter("region", inputs.get("region"))
					// AWS region
					.setParameter("ksUserName", inputs.get("user"))
					// Key Manager user name
					.setParameter("ksPassword", inputs.get("password"))
					// Key Manager password
					.setParameter("keyName", inputs.get("key"))
					// Key name on the Key Manager
					.setParameter("name", inputs.get("fileName"))
					// name of the file to download
					// true if client side encryption or false for server
					// side operation
					.setParameter("isClientSide", inputs.get("clientSide"))
					// for client side transformation either AES or RSA
					.setParameter("transformation",
							inputs.get("transformation"))
					.setParameter("certAlias", inputs.get("alias"))
					// cert alias for
					// SSL connection towards Key Manager
					.setParameter("certPassword", inputs.get("certPassword"))
					.setParameter("version", inputs.get("version")).build();
			// absolute path of destination including file name (ex:
			// "C://user//downloads//text.txt")
			destinationFile = inputs.get("destination");

			((HttpRequestBase) httpget).setURI(uri);
			HttpResponse response = httpClient.execute(httpget);
			HttpEntity resEntity = response.getEntity();

			if (response.getStatusLine().getStatusCode() == 200) {
				FileOutputStream out = new FileOutputStream(new File(
						destinationFile));
				resEntity.writeTo(out);
				out.close();
				System.out.println("File downloaded successfully at location: "
						+ destinationFile);
			} else {
				System.out.println("File not downloaded due to "
						+ EntityUtils.toString(resEntity));
			}
		} catch (URISyntaxException e) {
			e.printStackTrace();
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
		
		if (input.get("destination") == null) {
			buffer.append("destination");
			buffer.append(", ");
		}
		
		if (buffer.length() != 0) {
			System.err.println("java FileDownload url=webserviceurl awsKey=accessKey awsSecretKey=secretKey"
			 + " bucket=bucketName region=region user=KeyManagerUserName password=KeyManagerPassword"
			 + " key=keyName fileName=filename destination=destinationFile  [clientSide=isClientSide] [transformation=transformation] [alias=certalias]"
			 + " [certPassword=certPassword] [version=version]");
			System.exit(-1);
		}
	}
}

