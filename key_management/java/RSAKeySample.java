/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.Provider;
import java.security.PublicKey;
import java.security.Security;
import java.security.KeyPairGenerator;
import java.security.KeyPair;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
//CADP for JAVA specific classes.
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPermission;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import java.security.PublicKey;
import java.security.PrivateKey;

/**
 * This sample shows how to use different key operations for asymmetric keys:
 * create an RSA key pair with the group permissions; export public key data; 
 * export private key data; delete the key pair from Key Manager;
 * import the key pair back to Key Manager.
 */
public class RSAKeySample {
    public static void main( String[] args ) throws Exception 
    {
	if (args.length != 4)
        {
            System.err.println("Usage: java RSAKeySample user password keyname group");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];
        String group     = args[3];

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (int i = 0; i < providers.length; i++)
	    System.out.println(providers[i].getInfo());

	 NAESession session =null;
	try { 
	    // create NAE Session: pass in Key Manager user name and password
	    session = NAESession.getSession(username, password.toCharArray());

	    //Configure the key permissions to be granted to NAE group.
	    NAEPermission permission = new NAEPermission(group);
	    // add permission to sign
	    permission.setSign (true);
	    // add permission to verify signature
	    permission.setSignV (true);
	    NAEPermission[] permissions = {permission};

	    // create key pair which is exportable and deletable
	    // key owner is Key Manager user, default key length 1024 bits and 
	    // permissions granted to sign and verify
	    NAEParameterSpec rsaParamSpec = 
		new NAEParameterSpec(keyName, true, true, session, permissions);
	    KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA", "IngrianProvider");
	    kpg.initialize(rsaParamSpec);
	    KeyPair pair = kpg.generateKeyPair();

	    // Get public key data from Key Manager
	    NAEPublicKey pubKey = NAEKey.getPublicKey(keyName, session );
	    byte[] pubKeyData = pubKey.export();
	    System.out.println("Exported public key: " + pubKey.getName());

	    // Export private key data (contains both public and private key data)
	    NAEPrivateKey privKey = NAEKey.getPrivateKey(keyName, session);
	    byte[] privKeyData = privKey.export();

	    // Delete the key pair from Key Manager
	    pubKey.delete();

	    // Import the key pair back to the Key Manager
	    // key pair name is keyName+"Dup", keys are exportable and not deletable
	    NAEParameterSpec spec_dup =
		 new NAEParameterSpec(keyName + "Dup", true, false, session);
	    // private key contains both public and private key data
	    privKey.importKey (privKeyData, "RSA", spec_dup);
	    System.out.println("Imported key data; Duplicate Key pair " + privKey.getName() +
			       " is created on NAE Server.");
	    
	    // Export private key data in PKCS#8 format and create JCE key
	    NAEPrivateKey prKey = NAEKey.getPrivateKey(keyName + "Dup", session);
	    PrivateKey jcePrivateKey = prKey.exportJCEKey();

	    // Export public key data in PKCS#5 format and create JCE key
	    NAEPublicKey publKey = NAEKey.getPublicKey(keyName + "Dup", session);
	    PublicKey jcePublicKey = publKey.exportJCEKey();
	    
	} catch (Exception e) {
		e.printStackTrace();
		throw e;
	} finally {
		if(session!=null)
			//Close NAESession
			session.closeSession();
	}
    }
}


	
