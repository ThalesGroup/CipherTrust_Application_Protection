/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes.
import java.security.Provider;
import java.security.Security;

import javax.crypto.Cipher;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt and decrypt data using RSA key.
 */
public class RSAEncryptionSample {
    
 public static void main( String[] args ) throws Exception 
    {
	if (args.length != 3)
        {
            System.err.println("Usage: java RSAEncryptionSample user password keyname");
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

	String dataToEncrypt = "dataToEncrypt";
	System.out.println("Data to encrypt \"" + dataToEncrypt + "\"");
	NAESession session = null;
	try { 
	    // create NAE Session: pass in NAE user name and password
	    session = NAESession.getSession(username, password.toCharArray());

	    // get RSA public key to encrypt data 
	    // (just a key handle , key data does not leave the Key Manager)
	    NAEPublicKey pubKey = NAEKey.getPublicKey(keyName, session );
	    
	     // get a cipher
	    Cipher encryptCipher = Cipher.getInstance("RSA", "IngrianProvider");

	    // initialize cipher to encrypt.
	    encryptCipher.init(Cipher.ENCRYPT_MODE, pubKey);

	    // encrypt data
	    byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());

	    // get private key to decrypt data
	    // (just a key handle , key data does not leave the Key Manager)
	    NAEPrivateKey privKey = NAEKey.getPrivateKey(keyName, session);

	    // get a cipher for decryption
	    Cipher decryptCipher = Cipher.getInstance("RSA", "IngrianProvider");
	    
	    // to decrypt data, initialize cipher to decrypt
	    decryptCipher.init(Cipher.DECRYPT_MODE,  privKey);

	    // decrypt data
	    byte[] newbuf = decryptCipher.doFinal(outbuf);
	    System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");

	} catch (Exception e) {
	    e.printStackTrace();
	    throw e;
	} finally{
		if(session!=null) {
			//Close NAESession
			session.closeSession();
		}
	}
    }
}
