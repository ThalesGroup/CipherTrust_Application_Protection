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

import com.ingrian.security.nae.FPEFormat;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider;
//CADP for JAVA specific classes.
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt and decrypt Email using CADP for JAVA.
 *
 */
public class FPEEncryptionDecryptionEmailSample 
{
    public static void main( String[] args ) throws Exception
    {
	 if (args.length != 5)
        {
            System.err.println("Usage: java FPEEncryptionDecryptionEmailSample username password keyname TweakAlgorithm(Optional) TweakData(Optional)");
            System.err.println("Mention null for optional parameter if you don't want to pass it");
            /*
             * Usage: keyname Supports AES Non-versioned key
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
        
        String tweakAlgo = null;
        if(!args[3].contains("null")) {
			tweakAlgo  = args[3];
		}
        
        String tweakData = null;
        if(!args[4].contains("null")) {
			tweakData   = args[4];
		}

	String dataToEncryptEmail = "fpe_encrypt_654321_decrypt@sample.com";
	System.out.println("Data to encrypt - Email : " + dataToEncryptEmail + "\"");
	
	// Add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// Get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (int i = 0; i < providers.length; i++)
		System.out.println(providers[i].getInfo());

	NAESession session  = null;
	try {
	    // create NAE Session: pass in Key Manager user name and password
	    session  = 
		NAESession.getSession(username, password.toCharArray());

	    // Get SecretKey (just a handle to it, key data does not leave the Key Manager
	    NAEKey key = NAEKey.getSecretKey(keyName, session);
	    
	    /**
	     * For using Email format, Create FPEFormat to fetch the Email Domain format ,can set numberOfElementsFromStart and numberOfElementsBeforeEnd.
	     */
	    
		FPEFormat formatEmail = FPEFormat.getEmailDomainFormat();
		//initialize start and end values
		formatEmail.setNumberOfElementsBeforeEnd(2);
		formatEmail.setNumberOfElementsFromStart(2);
		
		// Initializes spec with tweak parameters and format
		FPEParameterAndFormatSpec paramSpec = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
				.setFpeFormat(formatEmail).build();
		
		// get a cipher
	    Cipher encryptCipher = Cipher.getInstance("FPE/AES/CARD62", "IngrianProvider");
	    
		// initialize cipher to encrypt.
		encryptCipher.init(Cipher.ENCRYPT_MODE, key, paramSpec);

		// encrypt data
		byte[] outbuf = encryptCipher.doFinal(dataToEncryptEmail.getBytes());

		System.out.println("Encrypted data  \"" + new String(outbuf) + "\"");
		
		Cipher decryptCipher = Cipher.getInstance("FPE/AES/CARD62", "IngrianProvider");
		// to decrypt data, initialize cipher to decrypt
		decryptCipher.init(Cipher.DECRYPT_MODE, key, paramSpec);

		// decrypt data
		byte[]  newbuf = decryptCipher.doFinal(outbuf);
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
    
