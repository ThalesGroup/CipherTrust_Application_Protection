/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;

import javax.crypto.KeyGenerator;
import javax.crypto.Mac;
import javax.crypto.SecretKey;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.MACValue;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to create the message authentication code and
 * how to verify it using CADP JCE.
 */

public class HMACSample 
{
    public static void main( String[] args ) throws Exception
    {
	if (args.length != 3)
	{
            System.err.println("Usage: java HMACSample user password hmacKeyName");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (int i = 0; i < providers.length; i++)
	    System.out.println(providers[i].getInfo());
	
	String dataToMac = "2D2D2D2D2D424547494E2050455253495354454E54204346EB17960";
	System.out.println("Data to mac \"" + dataToMac + "\"");
	NAESession session  =null;
	try {
	    // create HMAC key on the server
	    // create NAE Session: pass in Key Manager user name and password
	    session  = NAESession.getSession(username, password.toCharArray());

	    // create key which is exportable and deletable,
	    // key owner is passed in Key Manager user.
	    // For HmacSHA1 key length 160 bits 
	    // For HmacSHA256 key length is 256 bits
	    // For HmacSHA384 key length is 384 bits
	    // For HmacSHA512 key length is 512 bits
	    NAEParameterSpec spec = new NAEParameterSpec( keyName, true, true, 160, session);

	    KeyGenerator kg = KeyGenerator.getInstance("HmacSHA1", "IngrianProvider");
	    kg.init(spec); 
            SecretKey secret_key = kg.generateKey();

	    // get the handle to created key
	    NAEKey key = NAEKey.getSecretKey(keyName, session);

	    // create MAC instance to get the message authentication code
	    Mac mac = Mac.getInstance("HmacSHA1", "IngrianProvider");
	    mac.init(key);
	    byte[] macValue = mac.doFinal(dataToMac.getBytes());

	    // create MAC instance to verify the message authentication code
	    Mac macV = Mac.getInstance("HmacSHA1Verify", "IngrianProvider");
	    macV.init(key, new MACValue(macValue));
	    byte[] result = macV.doFinal(dataToMac.getBytes());
        
	    // check verification result 
	    if (result.length != 1 || result[0] != 1) {
		System.out.println("Invalid MAC.");
	    } else {
		System.out.println("MAC Verified OK.");
	    }
	} catch (Exception e) {
	    System.out.println("The Cause is " + e.getMessage() + ".");
	    throw e;
	} finally{
		if(session!=null)
			session.closeSession();
	}
    }
}
