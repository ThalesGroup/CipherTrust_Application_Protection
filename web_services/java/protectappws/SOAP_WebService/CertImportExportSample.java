/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.FileInputStream;
import java.net.URL;

import javax.xml.namespace.QName;

import com.ingrian.ws.client.Protectappws_Service;
import com.ingrian.ws.core.CertExport;
import com.ingrian.ws.core.CertImport;
import com.ingrian.ws.core.Protectappws;

/**
 * This sample shows how to use different certificate operations: import and
 * export certificate ; Access sample certificate (cert.pkcs8) file from
 * cert_samples. This sample assumes that server is running on localhost on port
 * 8080
 */
public class CertImportExportSample {
	private static final QName SERVICE_NAME = new QName(
			"http://dsws.org/protectappws/", "protectappws");

	public static void main(String[] args) {

		if (args.length != 6) {
			System.err
					.println("Usage: java CertImportExportSample user password fileName certName certIsDeletable certIsExportable ");
			System.exit(-1);
		}

		String username = args[0];
		String password = args[1];
		String fileName = args[2];
		String certName = args[3];
		Boolean isDeletable = Boolean.parseBoolean(args[4]);
		Boolean isExportable = Boolean.parseBoolean(args[5]);

		try {
			String wsdl = "http://localhost:8080/protectappws/services/ProtectappwsImpl?wsdl";
			URL wsdlURL = new URL(wsdl);

			/* 1. Call the CXF client stub for remote method invocation */
			Protectappws_Service ss = new Protectappws_Service(wsdlURL,
					SERVICE_NAME);
			Protectappws port = ss.getProtectappwsSOAP();

			FileInputStream fis = new FileInputStream(fileName);
			byte[] certData = new byte[fis.available()];
			fis.read(certData);
			fis.close();

			/* 2. Import the Certificate */
			CertImport imp = new CertImport();
			imp.setCertificate(new String(certData, "UTF-8"));
			imp.setCertisdeletable(isDeletable);
			imp.setCertisexportable(isExportable);
			imp.setCertname(certName);
			imp.setPassword(password);
			imp.setUsername(username);
			boolean result = port.certImport(imp);
			System.out.println("Cert import Result : " + result);

			if (!result)
				return;
			
			/* 3. Export the Certificate */
			CertExport export = new CertExport();
			export.setCertname(certName);
			export.setPassword(password);
			export.setUsername(username);

			System.out.println("Cert Export : " + port.certExport(export));

		} catch (Exception ex) {
			ex.printStackTrace();
		}

	}
}
