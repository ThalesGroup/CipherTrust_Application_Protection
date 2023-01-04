/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.util.Calendar;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.internal.kmip.api.CryptographicUsageMask.UsageMask;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAESecretKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;

/*
 * This sample shows how to create a Symmetric key using
 
 * KMIP via the CAJ JCE and then use that new 
 * key to encrypt data.
 * 
 * An AES-256 key is created via KMIP.
 * 
 * Then using a separate NAE XML session, the key is used
 * to encrypt data.
 */

public class KMIPCreateAndEncryptSample
{
    public static void main( String[] args ) throws Exception
    {
  
        if (args.length != 5)
        {
                usage();
        } 
        
        String keyName = args[4];
        int keyLength = 256;

        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        KMIPSession kmipSession=null;
        NAESession naeSession=null;
        try {

            // create KMIP Session - specify client X.509 certificate and keystore password
       kmipSession = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));
            // create key custom attributes

            NAEKey key;
                      
            try { /* does the key exist? if so, delete it */
               /* get..Key method is merely a placeholder for a managed object 
                * with that name. */
               key = NAEKey.getSecretKey(keyName, kmipSession);
               /* getUID() will throw an exception if the key does not exist */
               if ( key.getUID() != null ) {
                   System.out.println("Deleting key " + keyName + " with UID=" + key.getUID());
                   key.delete();
               }
               
            }
            catch( NAEException missing ) {
                if ( missing.getMessage().equals("Key not found on server.") ) {
                    System.out.println("Key did not exist");
                }
                else throw missing;
            }
            /* create a secret key using KMIP JCE key generator */

            KMIPAttributes initialAttributes = new KMIPAttributes();
            initialAttributes.add(KMIPAttribute.CryptographicUsageMask, (int)
                    (
                     UsageMask.Encrypt.getValue() | 
                     UsageMask.Decrypt.getValue() )
                    );
            Calendar c=Calendar.getInstance();
            initialAttributes.addDate(KMIPAttribute.ActivationDate, c);

            NAEParameterSpec spec = new NAEParameterSpec( keyName, keyLength, 
                    (KMIPAttributes) initialAttributes, kmipSession);
            KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
            kg.init(spec); 
            SecretKey secretKey = kg.generateKey();
            System.out.println("Created key " + ((NAEKey) secretKey).getName());

            /* Once created, you may operate on the KMIP key. For example, 
             * add a KMIP group attribute to the KMIP - not required, just include 
             * as a sample of KMIP operations on the key */
            
            KMIPAttributes ka = new KMIPAttributes();
            ka.add(KMIPAttribute.ObjectGroup, 0, "group1");
            
            secretKey = NAEKey.getSecretKey(keyName);
            NAESecretKey sk = NAEKey.getSecretKey(keyName, kmipSession);
            sk.addKMIPAttributes(ka);
            
            /* Now use the NAEKey created for encryption using an NAESession
             * to a Key Manager server. Essentially this is the same code as the
             * SecretKeyEncryptionSample.java program
             * Nothing new is required to use the KMIP-created key on the 
             * Key Manager server.
             */
            
            // create NAE XML Session: pass in NAE user name and password
           naeSession  = NAESession.getSession(args[2], args[3].toCharArray());
            // Get SecretKey (just a handle to it, key data does not leave the server
            // Note: KMIP keys objects need to be re-retrieved on the XML session
            
            key = NAEKey.getSecretKey(keyName, naeSession);
            
            // get IV
            NAESecureRandom rng = new NAESecureRandom(naeSession);

            byte[] iv = new byte[16];
            rng.nextBytes(iv);
            IvParameterSpec ivSpec = new IvParameterSpec(iv);
            
            // get a cipher
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
            // initialize cipher to encrypt.
            cipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
            
            String dataToEncrypt = "2D2D2D2D2D424547494E2050455253495354454E54204346EB17960";
            System.out.println("Data to encrypt \"" + dataToEncrypt + "\"");
        
            // encrypt data
            byte[] outbuf = cipher.doFinal(dataToEncrypt.getBytes());

            // to decrypt data, initialize cipher to decrypt
            cipher.init(Cipher.DECRYPT_MODE, key, ivSpec);
            // decrypt data
            byte[] newbuf = cipher.doFinal(outbuf);
            System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");
                    
        }  catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
            throw e;
        }
        finally {
        	if(kmipSession!=null)
        		kmipSession.closeSession();
        	if(naeSession!=null)
        		naeSession.closeSession();
		}
    }
    

    private static void usage() {
        System.err.println("Usage: java KMIPCreateAndEncryptSample clientCertAlias keyStorePassword NAEUserName NAEpassword keyName");
        System.exit(-1);
    }
}
