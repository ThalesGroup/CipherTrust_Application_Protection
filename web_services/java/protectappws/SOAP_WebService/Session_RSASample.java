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
import com.ingrian.ws.core.SessionOpen;
import com.ingrian.ws.core.SessionRSASign;
import com.ingrian.ws.core.SessionRSAVerify;

/**
 * This sample shows how to sign and verify data using RSA.This sample assumes
 * that server is running on localhost on port 8080
 */
public class Session_RSASample {

	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");

	public static void main(String[] args) throws MalformedURLException {
		if (args.length != 5) {
			System.err
					.println("Usage: java Session_RSASample user password keyname messageText transformation");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String messageText = args[3];
		String transformation=args[4];

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

		try {
			/* 3. Sign with RSA key */
			SessionRSASign rsa = new SessionRSASign();
			rsa.setKeyname(keyName);
			rsa.setMessagetext(messageText);
			rsa.setTransformation(transformation);
			String signed = port.sessionRSASign(rsa);
			System.out.println("RSA signature of " + messageText + " is : "
					+ signed);

			if (signed == null)
				return;
			/* 4. Verify the signature */
			SessionRSAVerify rsav = new SessionRSAVerify();
			rsav.setKeyname(keyName);
			rsav.setMessagetext(messageText);
			rsav.setSignature(signed);
			rsav.setTransformation(transformation);
			System.out.println("Signature verify result : "
					+ port.sessionRSAVerify(rsav));
		} catch (Exception ex) {
			ex.printStackTrace();
		}

	}

}
