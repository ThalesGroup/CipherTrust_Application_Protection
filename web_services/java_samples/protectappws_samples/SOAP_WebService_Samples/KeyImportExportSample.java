/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.net.MalformedURLException;
import java.net.URL;

import javax.xml.namespace.QName;

import com.ingrian.ws.client.Protectappws_Service;
import com.ingrian.ws.core.KeyExport;
import com.ingrian.ws.core.KeyImport;
import com.ingrian.ws.core.Protectappws;

/**
 * This samples shows how to import and export the key to Key Manager SOAP web services
 * This sample assumes that server is running on localhost on port 8080
 */
public class KeyImportExportSample {
	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");

	public static void main(String[] args) throws MalformedURLException {
		if (args.length != 7) {
			System.err
					.println("Usage: java KeyImportExportSample user password keyname algo keyBytes isDeletable(Boolean) isexportable(Boolean)");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String algo = args[3];
		String keyBytes = args[4];
		Boolean isDeletable = Boolean.parseBoolean(args[5]);
		Boolean isexportable = Boolean.parseBoolean(args[6]);
		String wsdl = "http://localhost:8080/protectappws/services/ProtectappwsImpl?wsdl";
		URL wsdlURL = new URL(wsdl);

		/* 1. Call the CXF client stub for remote method invocation */
		Protectappws_Service ss = new Protectappws_Service(wsdlURL,
				SERVICE_NAME);
		Protectappws port = ss.getProtectappwsSOAP();

		/* 2. Call the key import SOAP API */
		KeyImport imp = new KeyImport();
		imp.setKeyalgorithm(algo);
		imp.setKeybytes(keyBytes);
		imp.setKeyisdeletable(isDeletable);
		imp.setKeyisexportable(isexportable);
		imp.setKeyname(keyName);
		imp.setPassword(password);
		imp.setUsername(username);
		try {

			boolean result = port.keyImport(imp);
			System.out.println("Key Created :" + result);
		} catch (Exception e) {
			if (e.getMessage().contains("Key already exists"))
				System.err
						.println("testKey_Import output : This Key already exists at Key Manager");
			throw new RuntimeException(e);
		}

		if (!isexportable)
			return;
		/* 3. Export the created key */
		KeyExport exp = new KeyExport();
		exp.setKeyname(keyName);
		exp.setPassword(password);
		exp.setUsername(username);

		try {
			System.out.println("Exported key "+port.keyExport(exp));
		} catch (Exception ex) {
			ex.printStackTrace();
		}
	}

}
