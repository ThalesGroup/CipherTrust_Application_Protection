/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URL;

import javax.xml.namespace.QName;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.ws.client.Protectappws_Service;
import com.ingrian.ws.core.Protectappws;
import com.ingrian.ws.core.SessionFPEDecrypt;
import com.ingrian.ws.core.SessionFPEEncrypt;
import com.ingrian.ws.core.SessionOpen;

/**
 * This sample shows how to encrypt a data using a FPE SOAP stateful web
 * service. This sample assumes that server is running on localhost on port 8080
 * 
 */
public class Session_FPEEncryptSample {
	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");

	public static void main(String[] args) throws MalformedURLException,
			UnsupportedEncodingException {
		if (!(args.length == 5 || args.length == 7)) {
			System.err
					.println("Usage: java Session_FPEEncryptSample user password keyname plaintext tweakData tweakAlgo(optional) keyIv(optional), If optional attributes are used then both must be specified.");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String plaintext = args[3];
		String tweakData = args[4];
		String keyIv = null;
		String tweakAlgo = "None";
		if (args.length > 5) {
			tweakAlgo = args[5];
			keyIv = args[6];
		}

		String wsdl = "http://localhost:8080/protectappws/services/ProtectappwsImpl?wsdl";
		URL wsdlURL = new URL(wsdl);

		/* 1. Call the CXF client stub for remote method invocation */
		Protectappws_Service ss = new Protectappws_Service(wsdlURL,
				SERVICE_NAME);
		Protectappws port = ss.getProtectappwsSOAP();

		/* 2. Open the HTTP session to perform stateful operations */
		SessionOpen open = new SessionOpen();
		open.setPassword(password);
		open.setUsername(username);
		boolean result = port.sessionOpen(open);
		if (!result)
			throw new RuntimeException("Could not get NAE Session");

		/* 3. Perform encryption operation */
		SessionFPEEncrypt encrypt = new SessionFPEEncrypt();
		if (keyIv != null)
			encrypt.setKeyiv(keyIv);
		encrypt.setKeyname(keyName);
		encrypt.setPlaintext(plaintext);
		if (tweakData != null)
			encrypt.setTweakData(tweakData);
		if (tweakAlgo != null)
			encrypt.setTweakAlgo(tweakAlgo);
		String encrypted = port.sessionFPEEncrypt(encrypt);
		System.out.println("Cipher Text : " + encrypted);
		

		/* 4. Perform decryption operation */
		SessionFPEDecrypt decrypt = new SessionFPEDecrypt();
		if (keyIv != null)
			decrypt.setKeyiv(keyIv);
		decrypt.setKeyname(keyName);
		decrypt.setCiphertext(encrypted);
		if (tweakData != null)
			decrypt.setTweakData(tweakData);
		if (tweakAlgo != null)
			decrypt.setTweakAlgo(tweakAlgo);
		String decrypted = port.sessionFPEDecrypt(decrypt);
		System.out.println("Plain text: " + decrypted);
	}

}
