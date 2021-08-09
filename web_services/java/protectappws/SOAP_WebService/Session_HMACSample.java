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
import com.ingrian.ws.core.SessionHMAC;
import com.ingrian.ws.core.SessionHMACVerify;
import com.ingrian.ws.core.SessionOpen;

/**
 * This sample shows how to calculate hmac of data using a SOAP stateful web service.
 * This sample assumes that server is running on localhost on port 8080 
 */
public class Session_HMACSample {
	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");
	/**
	 * @param args
	 * @throws MalformedURLException 
	 */
	public static void main(String[] args) throws MalformedURLException {
		if (args.length != 4)
		{
			System.err.println("Usage: java Session_HMACSample user password keyname messageText");
			System.exit(-1);
		} 
		String username  = args[0];
		String password  = args[1];
		String keyName   = args[2];
		String messageText	= args[3];
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
		
		/*3. Now perform HMAC operation */
		SessionHMAC hmac = new SessionHMAC();
		hmac.setKeyname(keyName);
		hmac.setMessagetext(messageText);
		String mac =port.sessionHMAC(hmac);
		System.out.println("HMAC of text "+messageText +" is : "+mac);
		
		/* 4. Verify the HMAC result */
		SessionHMACVerify hverify = new SessionHMACVerify();
		hverify.setKeyname(keyName);
		hverify.setMac(mac);
		hverify.setMessagetext(messageText);
		
		System.out.println("HMAC verify result : "+port.sessionHMACVerify(hverify));
		

	}

}
