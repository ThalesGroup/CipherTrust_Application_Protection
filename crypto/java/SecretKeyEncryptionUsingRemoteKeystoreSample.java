/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes.
import java.io.InputStream;
import java.net.URL;
import java.security.KeyStore;
import java.security.Provider;
import java.security.Security;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEException;
// CADP for JAVA specific classes.
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt/decrypt data in CADP for JAVA using keystore placed at remote URL.
 */

public class SecretKeyEncryptionUsingRemoteKeystoreSample 
{
    public static void main( String[] args ) throws Exception {
		if (args.length != 5)
			{
				System.err.println("Usage: java SecretKeyEncryptionUsingRemoteKeystoreSample username password keyname remoteKeystoreURL keystorePassword");
				System.exit(-1);
		}

		String username  = args[0];
		String password  = args[1];
		String keyName   = args[2];
		String remoteKeystoreURL = args[3];
		String keystorePassword = args[4];

		InputStream inputStream = null;
		KeyStore keystore = null;
		try {
			inputStream = new URL(remoteKeystoreURL).openStream();
			keystore = KeyStore.getInstance("JKS");
			keystore.load(inputStream, keystorePassword.toCharArray());
		} catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			throw e;
		} finally {
			if (inputStream != null)
				inputStream.close();
		}

		// add Ingrian provider to the list of providers
		Security.addProvider(new IngrianProvider.Builder().addKeyStore(keystore).build());

		// get the list of all registered providers
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

			// Get SecretKey
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			// get IV
			NAESecureRandom rng = new NAESecureRandom(session);

			byte[] iv = new byte[16];
			rng.nextBytes(iv);
			IvParameterSpec ivSpec = new IvParameterSpec(iv);

			// get a cipher for encryption
			Cipher encryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
			// initialize cipher to encrypt
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
			// encrypt data
			byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());
			System.out.println("Encrypted data  \""+IngrianProvider.byteArray2Hex(outbuf) + "\"");

			// get a cipher for decryption
			Cipher decryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");

			// initialize cipher to decrypt
			decryptCipher.init(Cipher.DECRYPT_MODE, key, ivSpec);
			// decrypt data
			byte[] newbuf = decryptCipher.doFinal(outbuf);
			System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");

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
    
