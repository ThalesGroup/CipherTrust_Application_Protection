/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.util.Set;

import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.internal.kmip.api.CryptographicUsageMask.UsageMask;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;

/**
 * This sample shows how to create a Symmetric key using
 * KMIP.
 * The key created will be a 256-bit AES Symmetric Key with the
 * given name.
 *
 * If the key already exists, the sample will first delete it, 
 * then re-create it. Finally, the default attribute names for 
 * the new key are listed.
 *  
 */

public class KMIPCreateSymmetricKeySample
{
    public static void main( String[] args ) throws Exception
    {
        String keyName = null;
        int keyLength = 256;
        if (args.length != 3)
        {
                usage();
        } 

        keyName = args[2];
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        KMIPSession session=null;
        try {

            // create KMIP Session - specify client X.509 certificate and keystore password
           session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));

            NAEKey key;
                        
            try { /* does the key exist? if so, delete it */
               /* get..Key method is merely a placeholder for a managed object 
                * with that name. */
               key = NAEKey.getSecretKey(keyName, session);
               /* getUID() will throw an exception if the key does not exist */
               if ( key.getUID() != null ) { 
	               // exists if Unique Identifier is not null
                   System.out.println("Deleting key " + keyName + " with UID=" + key.getUID());
                   key.delete();
               }
            }
            catch( Exception notFound ) {

            }
            /* create a secret key on the Key Manager using JCE key generator */

            KMIPAttributes initialAttributes = new KMIPAttributes();
            initialAttributes.add(KMIPAttribute.CryptographicUsageMask, (int)
                    (
                     UsageMask.Encrypt.getValue() |
                     UsageMask.Decrypt.getValue() )
                    );


            NAEParameterSpec spec = new NAEParameterSpec( keyName, keyLength, 
                    (KMIPAttributes) initialAttributes, session);
            KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
            kg.init(spec); 
            SecretKey secretKey = kg.generateKey();
            System.out.println("Created key " + ((NAEKey) secretKey).getName());
            
            /* cast to NAEKey and list the default attribute names */
            Set<String> defaultAttributes = ((NAEKey) secretKey).listKMIPAttributes();
            System.out.println(defaultAttributes);
  
        }  catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
            throw e;
        }
        	finally {
        	if(session!=null)
        		session.closeSession();
		}
    }
    
    private static void usage() {
        System.err.println("Usage: java KMIPCreateSymmetricKeySample clientCertAlias keyStorePassword keyName");
        System.exit(-1);
    }
}
