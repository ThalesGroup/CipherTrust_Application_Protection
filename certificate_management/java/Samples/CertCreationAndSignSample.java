/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.IOException;
import java.security.Provider;
import java.security.Security;

import com.ingrian.internal.xml.XMLException;
import com.ingrian.security.nae.CSRInformation;
import com.ingrian.security.nae.CSRSigningInfo;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.LoadKeystore;
import com.ingrian.security.nae.NAECertificate;
import com.ingrian.security.nae.NAESession;

/**
 *This example show how CSR feature can be used.
 *This example provides end to end functionality. It provides 2 type of 
 *function. 
 *   1) To create a CSR from already existing key pair on the Key Manager.
 *   2) Only send sign request to the Key Manager. User created its own private key
 *      and CSR request.
 *
 * This example shows 1st case:
 * In this we will first create a CSR request on the Key Manager with the existing
 * key pair then use CSR data received from the Key Manager to get it signed by
 * the CA authority present on the Key Manager itself. Demo also shows user can
 * add private key and signed certificate into the keystore as well. 
 * This will store all the files in the default directory. To store files
 * into any other location please see API explanation in Javadocs.
 *
 * Please check Javadoc for more explanation of each type of field.
 * @date: Dec 9, 2014
 */
public class CertCreationAndSignSample {

	public static void main(String[] args) {

		 if (args.length != 11) {
			 System.out.println("Usage: java CertCreationAndSignSample username password"
			 		+ " keyname -cn cnName -country countryName -ca caName"
			 		+ " -expiry expiryTime");
			 System.exit(0);
		 }
		 
		 String userName =  args[0];
		 String password = args[1];
		 String keyName = args[2];
		 String cnName = null;
		 String country = null;
		 String ca = null;
		 int expiry = 0;
		 
		 for (int i = 0; i < args.length; i++) {
			 if (args[i].equals("-cn")) {
				 cnName = args[i+1];
			 } else if (args[i].equals("-country")) {
				 country = args[i+1];
			 } else if (args[i].equals("-ca")) {
				 ca = args[i+1];
			 } else if (args[i].equals("-expiry")) {
				 expiry = Integer.parseInt(args[i+1]);
			 }
			 
		 }
		 
		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());

        NAESession session = null;
		String csrInfo = null;

		try {
			session = NAESession.getSession(userName,password.toCharArray());
			csrInfo = createCSR(session, keyName, cnName, country); 
			System.out.println("Certificate signing request");
			System.out.println(csrInfo);
				
		    String signedData =  signedData(session, csrInfo, ca, expiry);	      
		    System.out.println("Signed certificate:");
		    System.out.println(signedData);
		    
		    loadKeyAndCertificateInKeyStore(session, signedData, keyName, ca);
		} catch (Exception e) {
			e.printStackTrace();
		} finally{
			session.closeSession();
		}
	 
	}

	private static void loadKeyAndCertificateInKeyStore(NAESession session,
			String signedData, String keyName, String ca) {
		
		//This will create a keystore from default values and at default 
		//location. Please see Javadoc for explanation.
	    LoadKeystore loadKeyStore = new LoadKeystore();
	    
	    //this will extract the private key from the Key Manager, convert it into
	    //PKCS#8 format. It then create the X.509 certificate from the signed
	    //certificate and add to the keystore mentioned with the given alias
	    //if alias is not already present. In case if already present then
	    //check the user wish to replace it or not.you can also use byte version.
	    //user can also set client certificate password by replacing null with
	    //appropriate password.
	    loadKeyStore.storeKeyAndCertificateInPKCS8Format(session,
	    		keyName, null, signedData.getBytes(), true);
	    
	    //you can also add CA authority certificate into the keystore. You
	    //need to provide full path or else default location is choose.
	    //It will extract the CA name from this as well. If mentioned file
	    //is not present at the current path then it will fetch it from
	    //the Key Manager and store it at given path or default path if not full
	    //path is mentioned.
	    loadKeyStore.addCACertificateToKeyStore(ca, session, false);    
	}

	private static String signedData(NAESession session, String csrInfo,
				String ca, int expiry) throws IOException, XMLException {
		
		//this will represent information required to generate sign request
		CSRSigningInfo csrSign = new  CSRSigningInfo(
				ca, expiry, csrInfo.getBytes());
			
		//this will create a signed certificate using information provided by
		//user.This will also store the data into the file mentioned by the
		//user. Full path is recommended else it will store in the user's home
		//directory. User can also left it blank in that case default file is
		//created at user's home directory.
		return NAECertificate.signCSR(session, csrSign);
	}
	
	private static String createCSR(NAESession session, String keyName,
			String cnName, String country) throws XMLException, IOException {
	
		//User can also pass optional value by creating map. Please see
		//javadoc for more details.
		CSRInformation csr = new CSRInformation(keyName, cnName, country);
		
		//this will create a CSR request using information provided by user.
		//This will also store the data into the file mentioned by the user.
		//full path is recommended else it will store in the user's home directory.
		//if file name is not given then default name and path will be considered.
		return NAECertificate.createCSR(session, csr);
	}
}


