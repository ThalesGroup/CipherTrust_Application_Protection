/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Provider;
import java.security.Security;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;

/**
 * 
 * 
 * This sample use to identify KMIP Protocol versions supported on Key Manager
 * 
 */
public class KMIPDiscoverVersionSample {


	public static void main(String[] args) {
		if (args.length != 2)
		{
			usage();
		} 
		
		// version array to check their support on Key Manager
		String[] checkversions = {"1.2","1.3"};

		// add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        // get the list of all registered JCE providers
        Provider[] providers = Security.getProviders();
        for (int i = 0; i < providers.length; i++)
            System.out.println(providers[i].getInfo());
        
		KMIPSession session = null;
		try{
			//initiate KMIP session
			session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));
		
			String[] responsefromKS = session.KMIPDiscoverVersions(checkversions);
			if(null != responsefromKS && responsefromKS.length > 0)
			for(String version : responsefromKS){
				System.out.println("version supported on Key Manager " + version);
			}
		}
		finally{		
			session.closeSession();
		}
	}

	private static void usage() {
		System.err.println("Usage: java KMIPDiscoverVersionSample clientCertAlias keyStorePassword ");
		System.exit(-1);
	}

}
