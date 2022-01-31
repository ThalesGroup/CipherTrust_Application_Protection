/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.net.MalformedURLException;
import java.net.URL;

import javax.xml.namespace.QName;
import javax.xml.ws.BindingProvider;

import com.ingrian.ws.core.Protectappws;
import com.ingrian.ws.core.Protectappws_Service;
import com.ingrian.ws.core.SessionAllUserInfo;
import com.ingrian.ws.core.SessionOpen;


public class Session_GetAllUsersInfo {
	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");
	
	public static void main(String[] args) throws MalformedURLException {
		if (args.length < 2) {
			System.err
					.println("Usage: java Session_GetAllUsersInfo user password");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		 
		
		String wsdl = "http://localhost:8080/protectappws/services/ProtectappwsImpl?wsdl";
		URL wsdlURL = new URL(wsdl);
		
		/*1. Call the CXF client stub for remote method invocation*/
		Protectappws_Service ss = new Protectappws_Service(wsdlURL,
				SERVICE_NAME);
		Protectappws port = ss.getProtectappwsSOAP();
		
		/* For reading the session set in cookie. */
		((BindingProvider)port).getRequestContext().put(BindingProvider.SESSION_MAINTAIN_PROPERTY, true);
		
		/*2. Open the HTTP session to perform stateful operations*/
		SessionOpen open = new SessionOpen();
		open.setPassword(password);
		open.setUsername(username);
		boolean result = port.sessionOpen(open);
		if (!result) {
			throw new RuntimeException("Could not get NAE Session");
		}
		
		SessionAllUserInfo info = new SessionAllUserInfo();
		String allDetails = port.sessionAllUserInfo(info);
		
		System.out.println("******* All User Info **************");
		System.out.println(allDetails);
	}
}
