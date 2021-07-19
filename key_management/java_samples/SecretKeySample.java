/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;

import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPermission;
import com.ingrian.security.nae.NAESession;
 
/**
 * This sample shows how to use different key operations for symmetric keys:
 * create an AES key; export this key data from Key Manager;  clone the key;
 * delete this key from Key Manager; import that key back to Key Manager.
 */

public class SecretKeySample
{
    public static void main( String[] args ) throws Exception
    {
	if (args.length != 4)
	{
            System.err.println("Usage: java SecretKeySample user password keyname group");
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

	NAESession session  =null;
	try {
	    // Create AES key on Key Manager

	    // create NAE Session: pass in Key Manager user name and password
	    session  = NAESession.getSession(username, password.toCharArray());
	    // create key which is exportable and deletable,
	    // key owner is passed in Key Manager user and default key length 128 bits
	    NAEParameterSpec spec = new NAEParameterSpec( keyName, true, true, session);
	    
	    KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
	    kg.init(spec); 
            SecretKey secret_key = kg.generateKey();

	    // Export key data
	    NAEKey key = NAEKey.getSecretKey(keyName, session);
	    byte[] keyData = key.export();
	    System.out.println("Key " + key.getName() + " was created on Key Manager.");

	    // Clone that key.
	    key.cloneKey(keyName+"Cloned");
	    key = NAEKey.getSecretKey(keyName + "Cloned", session);
	    System.out.println("Key " + key.getName() + " was cloned on Key Manager.");

	    // Delete that key from Key Manager
	    key.delete();

	    // Import that key back to the Key Manager

	    // set the key permissions to the set of permissions granted to 
	    // NAE group.
	    NAEPermission permission = new NAEPermission(group);
	    // add permission to encrypt
	    permission.setEncrypt (true);
	    NAEPermission[] permissions = {permission};

	    NAEParameterSpec spec_dup =
		new NAEParameterSpec(keyName + "Dup", true, true, session, permissions);
	    NAEKey.importKey (keyData, "AES", spec_dup);

	    key = NAEKey.getSecretKey(keyName + "Dup", session);
	    System.out.println("Imported key data; Duplicate Key " + key.getName() + " was created on Key Manager.");
	  
	} catch (Exception e) {
	    e.printStackTrace();
	} finally{
		if(session!=null)
			session.closeSession();
	}
    }
}


	
