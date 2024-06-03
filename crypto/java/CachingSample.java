/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes.
import java.security.Provider;
import java.security.Security;
import java.util.Iterator;
import java.util.Set;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.internal.cache.ConcurrentPersistantEncryptingHashMap;
import com.ingrian.internal.cache.NAECachedKey;
import com.ingrian.internal.cache.PersistentCache;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.LocalKey;
//CADP for JAVA-specific classes.
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEKeyCachePassphrase;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.NAESessionInterface;


/**
 * This sample shows how to encrypt and decrypt data using CADP for JAVA in local mode.
 * Note: 1.) Persistent and symmetric cache should be enabled in the IngrainNAE.properties file.
 * 	 2.) This sample can be used for version and non-version keys passed in the argument.
 */

public class CachingSample 
{
    public static void main( String[] args ) throws Exception
    {
	if (args.length != 3)
        {
            System.err.println("Usage: java CachingSample user password keyname");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];
        CachingSample sample = new CachingSample();

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (Provider provider : providers) {
		System.out.println(provider.getInfo());
	}

	String dataToEncrypt = "1234567812345678";
	System.out.println("Data to encrypt \"" + dataToEncrypt + "\"");
	 // create NAE Session: pass in Key Manager user name and password
    
    MyNAEKeyCachePassphrase m = sample.new MyNAEKeyCachePassphrase();
    
    NAESession session  = null;
	try {
		session  = NAESession.getSession(username, password.toCharArray(), m.getPassphrase(null));
	    // Get SecretKey (just a handle to it, key data does not leave the Key Manager

            System.out.println("KEYNAME === " + keyName);
            sample.oneShotEncrypt(session, keyName, "AES/CBC/NoPadding",dataToEncrypt, "1234567812345678" );
            sample.oneShotEncrypt(session, keyName, "AES/CBC/PKCS5Padding",dataToEncrypt, "1234567812345678" );
            sample.oneShotEncrypt(session, keyName, "AES/CBC/PKCS5Padding",dataToEncrypt, null );
            sample.oneShotEncrypt(session, keyName, "AES/ECB/PKCS5Padding",dataToEncrypt, null );
            sample.oneShotEncrypt(session, keyName, "AES/ECB/NoPadding",dataToEncrypt, null );
		
	    session.printCachingDetails();
            Thread.sleep(1000);

            System.out.println("Reading cache from disk to read");
            PersistentCache p = new PersistentCache();
            ConcurrentPersistantEncryptingHashMap map = 
                p.readFromDisk(username, session.getPassphrase());
            if (map != null) {
                System.out.println("Size cache from disk is = " + map.size());
                Set set = map.keySet();
                Iterator<String> iter = set.iterator();
                while (iter.hasNext()) {
                    String o = iter.next();
                    System.out.println("Key cache from disk = " + o);
                    NAECachedKey n = (NAECachedKey)map.get(o);
                }   
            } else {
                System.out.println("Map from disk is null");  
            }
            
	} catch (Exception e) {
            e.printStackTrace();
	    System.out.println("The Cause is " + e.getMessage() + ".");
	    throw e;
	} finally{
		if(session!=null) {
			session.closeSession();
		}
	}
    }

    public void oneShotEncrypt(
       NAESession session,
       String keyname,
       String algorithm,
       String plainText,
       String ivStr) throws Exception 
    {
       Cipher encryptCipher = null;
       Cipher decryptCipher = null;
       try {
           NAEKey pkey = NAEKey.getSecretKey(keyname, session);
           encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
           if (ivStr == null) {
               encryptCipher.init(Cipher.ENCRYPT_MODE, pkey);
               byte[] outbuf = encryptCipher.doFinal(plainText.getBytes());
               
           decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");  
           decryptCipher.init(Cipher.DECRYPT_MODE, pkey);
	       byte[] newbuf = decryptCipher.doFinal(outbuf);
	       System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");
           } else {
              byte [] iv = ivStr.getBytes();
              IvParameterSpec ivSpec = new IvParameterSpec(iv);
              encryptCipher.init(Cipher.ENCRYPT_MODE, pkey, ivSpec);
              byte[] outbuf = encryptCipher.doFinal(plainText.getBytes());
              
              decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");  
              decryptCipher.init(Cipher.DECRYPT_MODE, pkey, ivSpec);
              byte[] newbuf = decryptCipher.doFinal(outbuf);
              System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");
           }
       } catch (Exception e) {
           e.printStackTrace();
            System.out.println("The Cause is " + e.getMessage() + ".");
	    throw e;
       }

    }

    class MyNAEKeyCachePassphrase implements NAEKeyCachePassphrase {

        @Override
		public char[] getPassphrase(NAESessionInterface session) {
            char[] passPhrase = new char[8];

            passPhrase[0] = 'a';
            passPhrase[1] = 'b';
            passPhrase[2] = 'b';
            passPhrase[3] = '1';
            passPhrase[4] = '2';
            passPhrase[5] = '4';
            passPhrase[6] = '7';
            passPhrase[7] = 'z';
            return passPhrase;
        }
    }
}       
    }
}       
