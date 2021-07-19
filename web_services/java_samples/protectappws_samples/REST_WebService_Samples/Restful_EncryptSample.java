/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import javax.ws.rs.core.Response;

import org.apache.cxf.jaxrs.client.WebClient;

import com.ingrian.ws.rest.request.EncryptREST;
import com.ingrian.ws.rest.response.EncryptResponse;

/**
 * This sample shows how to encrypt a data using a restful web service. This
 * sample assumes that server is running on localhost port 8080
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
		String serverip = "127.0.0.1";
		String port = "8080";
		String transfromation = null;
		String keyIv = null;
		if (args.length == 6) {
			transfromation = args[4];
			keyIv = args[5];
		} else if (args.length == 5) {
			transfromation = args[4];
			System.out.println("Default key iv will be used for key");
		} else {
			System.out
					.println("Default Transformation AES/CBC/PKCS5Padding will be used");
			System.out.println("Default iv will be used for key");

		}

		String baseAddress = "http://" + serverip + ":" + port
				+ "/protectappws/services/rest/encrypt";

		WebClient client = WebClient.create(baseAddress);

		/* Prepare a encrypt object to post to */
		EncryptREST body = new EncryptREST();
		body.setKeyname(keyName);
		body.setPassword(password);
		body.setPlaintext(plaintext);
		body.setUsername(username);
		if (transfromation != null)
			body.setTransformation(transfromation);
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
