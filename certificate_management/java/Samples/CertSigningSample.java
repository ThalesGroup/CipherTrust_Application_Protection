/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.IOException;
import java.security.Security;

import com.ingrian.internal.xml.XMLException;
import com.ingrian.security.nae.CSRSigningInfo;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECertificate;
import com.ingrian.security.nae.NAESession;

/**
 *This example show how CSR feature can be used.
 *This example provides end to end functionality. It provides 2 type of 
 *function. 
 * 1) To create a CSR from already existing key pair on the Key Manager.
 * 2) Only send sign request to the Key Manager. User created its own private key
 *    and CSR request.
 *
 * This example shows 2nd case:
 * User uses Key Manager only to sign its CSR which may be generated using its
 * own private key pair. In this user has to pass the CSR either the
 * complete file path or bytes, CA name which use to sign the CSR and
 * the expire time. Once all the necessary inputs are provided Key Manager will sign
 * the request and reture signed document. This will store all the files in
 * the default directory. To store files into any other location please see
 * API explanation in Javadocs.
 *
 * Please check Javadoc for more explanation of each type of field.
 * 
 * @date: Dec 9, 2014
 */
public class CertSigningSample {

	static {
	 	Security.addProvider(new IngrianProvider());
	}

	public static void main(String[] args) {

		 if (args.length != 8) {
			 System.out.println("Usage: java CertSigningSample userName password "
			 	+ "-csr csrFilePath" + "-ca caName" + " -expiry expiryTime");
			 System.exit(0);
		 }
		 
		 String userName =  args[0];
		 String password = args[1];
		 
		 String ca = null;
		 String csrFilePath = null;
		 
		 int expiry = 0;
		 
		 for (int i = 0; i < args.length; i++) {
			 if (args[i].equals("-ca")) {
				 ca = args[i+1];
			 } else if (args[i].equals("-expiry")) {
				 expiry = Integer.parseInt(args[i+1]);
			 }  else if (args[i].equals("-csr")) {
				 csrFilePath = args[i+1];
			 }
			 
		 }

         NAESession session = null;
		try {
			session = NAESession.getSession(userName,password.toCharArray());
		    String signedData =  signedData(session, csrFilePath, ca, expiry);	      
		    System.out.println("Signed certificate:");
		    System.out.println(signedData);

		} catch (Exception e) {
			e.printStackTrace();
		} finally{
			if (session!=null) 
				session.closeSession();
		}
	}

	private static String signedData(NAESession session, String csrInfo,
				String ca, int expiry) throws IOException, XMLException {
		
		//this will represent information required to generate sign request
		CSRSigningInfo csrSign = new  CSRSigningInfo(
				ca, expiry, csrInfo);
			
		//this will create a signed certificate using information provided by
		//user.This will also store the data into the file mentioned by the
		//user. Full path is recommended else it will store in the user's home
		//directory. User can also left it blank in that case default file is
		//created at user's home directory.
		return NAECertificate.signCSR(session, csrSign);
	}

}


