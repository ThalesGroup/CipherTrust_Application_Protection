/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import java.net.MalformedURLException;
import java.net.URL;

import javax.xml.namespace.QName;

import com.ingrian.ws.client.Protectappws_Service;
import com.ingrian.ws.core.Protectappws;
import com.ingrian.ws.core.SessionDecrypt;
import com.ingrian.ws.core.SessionEncrypt;
import com.ingrian.ws.core.SessionOpen;

/**
 * This sample shows how to encrypt a data using a SOAP stateful web service.
 * This sample assumes that server is running on localhost on port 8080
 * 
 */
public class Session_EncryptSample {
	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");

	public static void main(String[] args) throws MalformedURLException {
		if (args.length < 4) {
			System.err
					.println("Usage: java Session_EncryptSample user password keyname plaintext transformation(optional) key_iv(optional)");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String plaintext = args[3];
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

		String wsdl = "http://localhost:8080/protectappws/services/ProtectappwsImpl?wsdl";
		URL wsdlURL = new URL(wsdl);
		
		/*1. Call the CXF client stub for remote method invocation*/
		Protectappws_Service ss = new Protectappws_Service(wsdlURL,
				SERVICE_NAME);
		Protectappws port = ss.getProtectappwsSOAP();

		/*2. Open the HTTP session to perform stateful operations*/
		SessionOpen open = new SessionOpen();
		open.setPassword(password);
		open.setUsername(username);
		boolean result = port.sessionOpen(open);
		if (!result)
			throw new RuntimeException("Could not get NAE Session");

		/* 3. Perform encryption operation */
		SessionEncrypt encrypt = new SessionEncrypt();
		if (keyIv != null)
			encrypt.setKeyiv(keyIv);
		encrypt.setKeyname(keyName);
		encrypt.setPlaintext(plaintext);
		if (transformation != null)
			encrypt.setTransformation(transformation);
		String encrypted = port.sessionEncrypt(encrypt);
		System.out.println("CipherText: " + encrypted);
		
		/* 4. Perform decryption operation */
		SessionDecrypt decrypt = new SessionDecrypt();
		if (keyIv != null)
			decrypt.setKeyiv(keyIv);
		decrypt.setKeyname(keyName);
		decrypt.setCiphertext(encrypted);
		if (transformation != null)
			decrypt.setTransformation(transformation);
		String decrypted = port.sessionDecrypt(decrypt);
		System.out.println("Decrypt the above cipher text: "+decrypted);
	}

}
