/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.InvalidAlgorithmParameterException;
import java.security.Key;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.PrivateKey;
import java.security.Security;
import java.util.Arrays;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPermission;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to wrap a key for export from the Key Manager
 * using the CADP JCE. An AES key is created on the Key Manager
 * which is to be wrapped, and a public and private key pair are
 * generated. The public key is used to wrap the AES key. The
 * private key is exported and the wrapped key is unwrapped (using
 * the SunJE provider). The original key is compared to the unwrapped
 * key.
 */
public class WrapKeySample {
    public static void main(String[] args)  {
        Security.addProvider(new IngrianProvider());  

        if (args.length != 5)
        {
            System.err.println("Usage: java WrapKeySample user password keyToWrapName wrappingKeyName groupName");
            System.exit(-1);
        }

        String userName = args[0];
        String passWord = args[1];
        String keyToWrapName = "WrapSamplePair"+args[2];
        String wrappingKeyName = "WrapSampleKey"+args[3];
        String groupName = args[4];
        NAESession session =null;
		try {
			// Create an NAESession.
			session = NAESession.getSession(userName,
					passWord.toCharArray());
			NAEParameterSpec spec = new NAEParameterSpec(keyToWrapName, true,
					true, 256, session);

			// Delete any existing keys from this sample.
			NAEKey keyToDelete = NAEKey.getSecretKey(keyToWrapName, session);
			deleteExistingKeys(wrappingKeyName, session, keyToDelete);

			// Generate an AES key to be wrapped when exported.
			KeyGenerator generator = KeyGenerator.getInstance("AES",
					"IngrianProvider");
			generator.init(spec); // NAEEParameters to pass session
			NAEKey keyToBeWrapped = (NAEKey) generator.generateKey();

			// Create a public/private RSA key pair to do the key wrapping.
			// The AES key will be wrapped with the RSA Public Key, and
			// later unwrapped using the RSA Private Key.
			KeyPair pair = createKeyPair(session, groupName, wrappingKeyName);

			NAEPublicKey publicKey = NAEKey.getPublicKey(wrappingKeyName,
					session);
			NAEPrivateKey privateKey = NAEKey.getPrivateKey(wrappingKeyName,
					session);

			// Init a JCE Cipher in WRAP_MODE to do the key wrapping.
			Cipher cipher = Cipher.getInstance("RSA", "IngrianProvider");
			cipher.init(Cipher.WRAP_MODE, publicKey, spec);

			// Wrap and export the wrapped AES Key from the Key Manager
			// using the cipher.wrap method.
			// The key is wrapped with the Public key from the key pair
			// on the Key Manager which was generated earlier.
			byte[] wrappedKey = cipher.wrap(keyToBeWrapped);
			System.out.println("wrapped  : "
					+ IngrianProvider.byteArray2Hex(wrappedKey));
			System.out.println("Length   : " + wrappedKey.length);

			// Unwrap the AES key using the private key of the
			// generated key pair using the SunJCE provider.

			// Export the NAEPrivate key as a JCE PrivateKey.
			PrivateKey prKey = privateKey.exportJCEKey();

			// Initialize a Cipher based on the SunJCE provider.
			// Note the use of PKCS1Padding.
			// For IBM java ,use the IBMJCE provider instead of SunJCE.
			Cipher cipher2 = Cipher.getInstance("RSA/ECB/PKCS1Padding",
					"SunJCE");
			cipher2.init(Cipher.UNWRAP_MODE, prKey);

			// Unwrap the wrapped key from the bytes returned from the
			// Key Manager.
			Key unWrappedKey = cipher2.unwrap(wrappedKey, "AES",
					Cipher.SECRET_KEY);

			System.out.println("Unwrapped: "
					+ IngrianProvider.byteArray2Hex(unWrappedKey.getEncoded()));
			System.out.println("Original : "
					+ IngrianProvider.byteArray2Hex(keyToBeWrapped.export()));
			if (Arrays.equals(keyToBeWrapped.export(),
					unWrappedKey.getEncoded()))
				System.out
						.println("Unwrapped key bytes equal original key bytes");

		}catch(Exception e){
        	e.printStackTrace();
        } finally{
        	if(session!=null)
        		session.closeSession();
        }

    }

    private static void deleteExistingKeys(String wrappingKeyName,
            NAESession session, NAEKey keyToDelete) {
        try {
            keyToDelete.delete();
        } catch( Exception ignore) {}
        NAEPublicKey publicKeyToDelete =  NAEKey.getPublicKey(wrappingKeyName,session);

        try {
            publicKeyToDelete.delete();
        } catch( Exception ignore) {}
    }

    private static KeyPair createKeyPair( NAESession session, String group, String keyName ) throws NoSuchAlgorithmException, NoSuchProviderException, InvalidAlgorithmParameterException{

        // Generate an RSA 2048 Public/Private Key pair on the Key Manager.
        
        // Set the key permissions to the set of permissions granted to NAE group.
        NAEPermission permission = new NAEPermission(group);

        // Add permission to sign.
        permission.setSign(true);

        // Add permission to verify signature.
        permission.setSignV(true);
        NAEPermission[] permissions = {permission};

        // Create an exportable and deletable key pair where the  
        // key owner is the Key Manager user, the key length is 2048 bits and 
        // permissions grant sign and sign verify operations.
        NAEParameterSpec rsaParamSpec = 
                new NAEParameterSpec(keyName, true, true, 2048, session, permissions);
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA", "IngrianProvider");
        kpg.initialize(rsaParamSpec);
        KeyPair pair = kpg.generateKeyPair();
        return pair;
    }
}
