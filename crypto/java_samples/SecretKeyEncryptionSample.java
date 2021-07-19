/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes.
import java.security.Provider;
import java.security.Security;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.security.nae.IngrianProvider;
// CADP JCE specific classes.
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt and decrypt data using CADP JCE.
 */

public class SecretKeyEncryptionSample 
{
    public static void main( String[] args ) throws Exception
    {
	if (args.length != 3)
        {
            System.err.println("Usage: java SecretKeyEncryptionSample user password keyname");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (Provider provider : providers) {
		System.out.println(provider.getInfo());
	}

	String dataToEncrypt = "2D2D2D2D2D424547494E2050455253495354454E54204346EB17960";
	System.out.println("Data to encrypt \"" + dataToEncrypt + "\"");
	NAESession session  = null;
	try {
	    // create NAE Session: pass in Key Manager user name and password
	    session  = 
		NAESession.getSession(username, password.toCharArray());

	    // Get SecretKey (just a handle to it, key data does not leave the Key Manager
	    NAEKey key = NAEKey.getSecretKey(keyName, session);
	    
	    // get IV
	    NAESecureRandom rng = new NAESecureRandom(session);

	    byte[] iv = new byte[16];
	    rng.nextBytes(iv);
	    IvParameterSpec ivSpec = new IvParameterSpec(iv);
	    
	    // get a cipher
	    Cipher encryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
	    // initialize cipher to encrypt.
	    encryptCipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
	    // encrypt data
	    byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());
	    
	    // get a cipher for decryption
	    Cipher decryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");

	    // to decrypt data, initialize cipher to decrypt
	    decryptCipher.init(Cipher.DECRYPT_MODE, key, ivSpec);
	    // decrypt data
	    byte[] newbuf = decryptCipher.doFinal(outbuf);
	    System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");

	    // to encrypt data in the loop
	    Cipher loopEncryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
	    // initialize cipher to encrypt.
	    loopEncryptCipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
	    byte[] outbuffer = null;
	    for (int i = 0; i < 10; i++) {
		// encrypt data in the loop 
		outbuffer = loopEncryptCipher.doFinal(dataToEncrypt.getBytes());
	    }

	    // to encrypt data in the loop
	    Cipher loopDecryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
	    // to decrypt data in the loop
	    // initialize cipher to decrypt.
	    loopDecryptCipher.init(Cipher.DECRYPT_MODE, key, ivSpec);
	    byte[] decrBuffer = null;
	    for (int i = 0; i < 10; i++) {
		// decrypt data in the loop 
		decrBuffer = loopDecryptCipher.doFinal(outbuffer);
	    }

	} catch (Exception e) {
	    System.out.println("The Cause is " + e.getMessage() + ".");
	    throw e;
	} finally{
		if(session!=null) {
			session.closeSession();
		}
	}
    }
}
    
