/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.apache.cxf.jaxrs.client.WebClient;

import com.ingrian.ws.rest.request.EncryptREST;
import com.ingrian.ws.rest.response.EncryptResponse;

/**
 * This sample shows how to encrypt a data using a restful web service. This
 * sample assumes that server is running on localhost port 8080
 *  
 * Note: To run Restful_EncryptSample, download and add the following jar files 
 * along with protectappwsClientStub.jar and CADP JCE Jar files to the java classpath:
 *
 * a) cxf-rt-rs-client-3.4.3.jar
 * b) cxf-core-3.4.3.jar
 * c) cxf-rt-frontend-jaxrs-3.4.3.jar
 * d) javax.ws.rs-api-2.1.1.jar
 * e) cxf-rt-transports-http-3.4.3.jar
 * f) stax2-api-4.2.1.jar
 * g) woodstox-core-6.2.4.jar
 * h) jettison-1.4.1.jar
 * i) cxf-rt-rs-json-basic-3.4.3.jar
 * j) cxf-rt-rs-extension-providers-3.4.3.jar
 */
public class Restful_EncryptSample {
	public static void main(String[] args) {
		if (args.length < 4) {
			System.err
					.println("Usage: java Restful_EncryptSample user password keyname plaintext transformation(optional) key_iv(optional)");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String plaintext = args[3];
		String serverip = "localhost";
		String port = "8080";
		String transformation = null;
		String keyIv = null;
		if (args.length == 6) {
			transformation = args[4];
			keyIv = args[5];
		} else if (args.length == 5) {
			transformation = args[4];
			System.out.println("Default key iv will be used for key");
		} else {
			System.out
					.println("Default Transformation AES/CBC/PKCS5Padding will be used");
			System.out.println("Default iv will be used for key");

		}

		String baseAddress = "http://" + serverip + ":" + port
				+ "/protectappws/services/rest/encrypt";

		WebClient client = WebClient.create(baseAddress);
		client.accept(MediaType.APPLICATION_JSON);
		client.header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON);

		/* Prepare a encrypt object to post to */
		EncryptREST body = new EncryptREST();
		body.setKeyname(keyName);
		body.setPassword(password);
		body.setPlaintext(plaintext);
		body.setUsername(username);
		if (transformation != null)
			body.setTransformation(transformation);
		if (keyIv != null)
			body.setKeyiv(keyIv);

		/* Bind the object and post it to server and post data in XML */
		Response r = client.post(body);

		if (r == null)
			throw new RuntimeException("Could not get Response from server");

		EncryptResponse res = r.readEntity(EncryptResponse.class);

		if (r.getStatus() == 200) {

			System.out
					.println("Restful_EncryptSample output \nplain text : "
							+ res.getCipherText() + "  | HTTP status: "
							+ r.getStatus());
		} else {
			System.err.println("Server encountered error : "
					+ res.getErrorDesString() + "| HTTP status: "
					+ r.getStatus());

		}

	}
}
