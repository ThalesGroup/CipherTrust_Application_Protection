/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;
import java.security.Signature;
import java.security.spec.AlgorithmParameterSpec;
import com.ingrian.security.nae.Format;
import com.ingrian.security.nae.CertList;
import com.ingrian.security.nae.SignVerifySpec;
// CADP for JAVA specific classes.
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to CMS sign data and verify signature using CADP for JAVA.
 */

public class CMSSignSample {    
    public static void main( String[] args ) throws Exception 
    {
	if (args.length != 4)
        {
            System.err.println("Usage: java CMSSignSample user password keyname caName");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];
        String caName    = args[3];
	// data to sign
	byte[] data = "dataToSign".getBytes();

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (int i = 0; i < providers.length; i++)
	    System.out.println(providers[i].getInfo());
	
	NAESession session = null;
	try { 
	    // create NAE Session: pass in Key Manager user name and password
	    session = NAESession.getSession(username, password.toCharArray());

	    // Create Signature object
	    Signature sig = Signature.getInstance("SHA1withRSA", "IngrianProvider");
         SignVerifySpec signVerifySpec = new SignVerifySpec(new Format("cms/detached/smime/enveloped"), new CertList(caName));
	    sig.setParameter((AlgorithmParameterSpec) signVerifySpec);

	    // Sign data
	    // Get private key
	    NAEPrivateKey privKey = NAEKey.getPrivateKey(keyName, session);

	    // Initialize Signature object for signing
	    sig.initSign(privKey);
	    sig.update (data);
	    byte[] signature = sig.sign();

	    // Verify signature
	    // Get public key
	    NAEPublicKey pubKey = NAEKey.getPublicKey(keyName, session );

	    // Initialize Signature object for signature verification
	    sig.initVerify(pubKey);
	    sig.update (data);
	    if (sig.verify(signature))
		System.out.println("Signature verified.");
	    else
		System.out.println("Signature verification failed.");

	    // close NAE session
	    session.closeSession();
	} catch (Exception e) {
	    e.printStackTrace();
	} finally{
		if(session!=null)
			session.closeSession();
	}
    }
}
