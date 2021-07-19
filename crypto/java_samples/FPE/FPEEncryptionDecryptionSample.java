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
import com.ingrian.security.nae.NAEIvAndTweakDataParameter;
//CADP JCE specific classes.
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt and decrypt data using CADP JCE.
 *
 */
public class FPEEncryptionDecryptionSample 
{
    public static void main( String[] args ) throws Exception
    {
	if (args.length != 6)
        {
            System.err.println("Usage: java FPEEncryptionDecryptionSample user password keyname IV TweakAlgorithm(Optional) TweakData(Optional)");
            System.err.println("Mention null for optional parameter if you don't want to pass it");
            /*
             * Usage: keyname Supports AES Non-versioned key
             * Usage: IV Must be 56 bytes Hex format string for AES key. IV must be of cardinality-10 that means each two characters (byte) of HEX IV must be 00-09
             * 		  IV must be provided when length of the data exceeds 56 bytes. FPE algorithm breaks the long data into 56 s-integer blocks and 
             * 		  uses block chaining algorithm very similar to CBC mode to encrypt and chain the long data.
             * 		  when length of the data does not exceed MAXb value, the IV must be absent.
             * Usage: TweakAlgorithm(Optional) must be from SHA1, SHA256 or None
             * Usage: TweakData(Optional) If, tweak data algorithm is 'None' or absent, 
           	 	    the value must be HEX encoded string representing 64 bit long. In case of valid tweak Algorithm,
            		the tweak data value can be any ASCII string (not necessarily HEX). 
            		Tweak Data is first processed using Tweak Hash Algorithm and the result is truncated to 64 bits
            		for input to the FPE algorithm
            */
            
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];
        String _iv  	 = args[3];
               	
        
        String tweakAlgo = null;
        if(!args[4].contains("null")) {
			tweakAlgo  = args[4];
		}
        
        String tweakData = null;
        if(!args[5].contains("null")) {
			tweakData   = args[5];
		}

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (Provider provider : providers) {
		System.out.println(provider.getInfo());
	}

	String dataToEncrypt = "36253865463254715234987125394785127934571235487631254876512837451827635487123564875216384728347";
	System.out.println("Data to encrypt \"" + dataToEncrypt + "\"");
	NAESession session  = null;
	try {
	    // create NAE Session: pass in Key Manager user name and password
	    session  = 
		NAESession.getSession(username, password.toCharArray());

	    // Get SecretKey (just a handle to it, key data does not leave the Key Manager
	    NAEKey key = NAEKey.getSecretKey(keyName, session);
	    byte[] iv = null;
	    NAESecureRandom rng;
	  
	    iv = IngrianProvider.hex2ByteArray(_iv);
	    
	    IvParameterSpec ivSpec = new IvParameterSpec(iv);
	    // Initializes IV and tweak parameters
	    NAEIvAndTweakDataParameter ivtweak = null;
	    ivtweak = new NAEIvAndTweakDataParameter(ivSpec, tweakData, tweakAlgo);
	    // get a cipher
	    Cipher encryptCipher = Cipher.getInstance("FPE/AES/CARD10", "IngrianProvider");
	    // initialize cipher to encrypt.
	   	encryptCipher.init(Cipher.ENCRYPT_MODE, key, ivtweak);
	    
	    // encrypt data
	    byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());
	    
	    System.out.println("encrypted data data  \"" + new String(outbuf) + "\"");
	    
	    Cipher decryptCipher = Cipher.getInstance("FPE/AES/CARD10", "IngrianProvider");
	    // to decrypt data, initialize cipher to decrypt
	    decryptCipher.init(Cipher.DECRYPT_MODE, key, ivtweak);
	    
	    // decrypt data
	    byte[] newbuf = decryptCipher.doFinal(outbuf);
	    System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");
	    // close the session
	    session.closeSession();
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
    
