/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes.
import java.lang.Character.UnicodeBlock;
import java.security.Provider;
import java.security.Security;

import javax.crypto.Cipher;

//CADP for JAVA specific classes.
import com.ingrian.security.nae.FPECharset;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt and decrypt data using FF1 algorithm.
 *
 */
public class FF1EncryptionDecryptionSample 
{
	public static void main( String[] args ) throws Exception
	{
		if (args.length != 5)
		{
			System.err.println("Usage: java FF1EncryptionDecryptionSample user password keyname TweakAlgorithm(Optional) TweakData(Optional)");
			System.err.println("Mention null for optional parameter if you don't want to pass it");
			/*
			 * Usage: keyname Supports AES Non-versioned key
			 * Usage: TweakAlgorithm(Optional) must be from SHA1, SHA256 or None
			 * Usage: TweakData(Optional) If, tweak data algorithm is 'None' or absent, 
           	 	    the value must be HEX encoded string. In case of valid tweak Algorithm,
            		the tweak data value can be any ASCII string (not necessarily HEX). 
            		Tweak Data is generated using Tweak Hash Algorithm.
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
			
			
			// For legacy CADP for JAVA clients uncomment following.
			//String algorithm = "FPE/FF1/CARD10";
			// FF1 algorithm which supports both ACVP and NIST test vectors.
			String algorithm = "FPE/FF1v2/CARD10";

			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
			// get a cipher
			Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// initialize cipher to encrypt.
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);

			// encrypt data
			byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());
			System.out.println("FF1 sample 1: ");
			System.out.println("encrypted data data  \"" + new String(outbuf) + "\"");

			Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// to decrypt data, initialize cipher to decrypt
			decryptCipher.init(Cipher.DECRYPT_MODE, key, param);

			// decrypt data
			byte[] newbuf = decryptCipher.doFinal(outbuf);
			System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");


			//sample 2 custom character set
			// For legacy CADP for JAVA clients uncomment following.
			//String algorithm = "FPE/FF1/UNICODE";
			// FF1 algorithm which supports both ACVP and NIST test vectors.
			algorithm = "FPE/FF1v2/UNICODE";
			//Define custom character set by providing list of code points. list can have single hex code point like "20" or hex code point range like "30-39".
			FPECharset charset = FPECharset.getUnicodeRangeCharset("20","30-39","41-5A");  //space, digits, upper case A-Z
			//Create character set from characters in LATIN_EXTENDED_A Unicode block. Equivalent to FPECharset.getUnicodeRangeCharset("0100-017F"), where 0100-017F is code point range for LATIN_EXTENDED_A
			//FPECharset charset = FPECharset.getUnicodeBlockCharset(UnicodeBlock.LATIN_EXTENDED_A);
			
			FPEParameterAndFormatSpec tweakCharsetParam = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).set_charset(charset).build();

			encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// initialize cipher to encrypt.
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, tweakCharsetParam);
			outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());

			System.out.println("FF1 sample 2: ");
			System.out.println("encrypted data data  \"" + new String(outbuf) + "\"");

			decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// to decrypt data, initialize cipher to decrypt
			decryptCipher.init(Cipher.DECRYPT_MODE, key, tweakCharsetParam);

			// decrypt data 
			newbuf = decryptCipher.doFinal(outbuf);
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

