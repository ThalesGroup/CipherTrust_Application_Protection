/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.util.Set;

import com.ingrian.internal.kmip.api.Attribute;
import com.ingrian.internal.kmip.api.CryptographicAlgorithms.Algorithm;
import com.ingrian.internal.ttlv.TTLVUtil;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAECertificate;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;

/**
 * This sample shows how to locate keys matching specified KMIP Attribute criteria, 
 * (in this example Algorithm matching aes and the key length matching 256)
 * find the managed obejct's name and type of object and then to export the key 
 * material associated with the managed object from the server.
 */

public class KMIPLocateSample
{
    public static void main( String[] args ) throws Exception
    {
        if (args.length < 2)
        {
                usage();
        } 
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        KMIPSession session=null;
        try {

            // create NAE Session: pass in NAE Client Certificate clicnt key and keystore password
          session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));

            //This set holds the managed object unique identifiers (UIDs) 

            Set<String> managedObjectIdentifiers;
            
            // Locate keys with crypto algorithm = aes and crypto length = 256
            KMIPAttributes queryAttributes = new KMIPAttributes();
//            queryAttributes.add(KMIPAttribute.CryptographicAlgorithm, Algorithm.aes);
//            queryAttributes.add(KMIPAttribute.CryptographicLength, 256);
            
         // by adding the KMIPAttribute name and the value to a KMIPAttributes
            /* 
             * IMPORTANT-In case of locate by name it is compulsory to pass argument for keyName as below 
             *  [-Name locateKeyName] where locateKeyName will be value of userInput.
             * */
            if(args.length>3) {
                if(args[2]!=null  && "-Name".equals(args[2])) {
                queryAttributes.add(new Attribute(KMIPAttribute.Name, args[3]));  
            }}
            // Have the session locate the keys matching the queryAttributes:
            managedObjectIdentifiers = session.locate( queryAttributes );
            // loop through the UIDs of the matching managed objects
            System.out.println("Total Keys: " + managedObjectIdentifiers.size());
            for (String uid : managedObjectIdentifiers ) {
                System.out.println("Managed object Unique Identifier: " + uid);
                
                // get the objects as Java client NAEKeys or KMIPSecretData objects
                // (Note: Secret Data doesn't have KMIP attributes of  
                // algorithm or length, and will not be found by this query,
                // but is included here for completeness.
                
                byte[] keyMaterial = null;
                Object managedObject = session.getManagedObject(uid);
                if ( managedObject == null ) continue; // not a key
                if ( managedObject instanceof NAEPublicKey ) {
                    System.out.println(((NAEPublicKey)managedObject).getName());
                    keyMaterial = ((NAEKey) managedObject).export();
                }
                else if ( managedObject instanceof NAEPrivateKey ) {
                    System.out.println(((NAEPrivateKey)managedObject).getName());
                    keyMaterial = ((NAEKey) managedObject).export();
                }
                else if ( managedObject instanceof NAESecretKey ) {
                    System.out.println(((NAESecretKey)managedObject).getName());
                    keyMaterial = ((NAEKey) managedObject).export();
                }
                else if ( managedObject instanceof KMIPSecretData ) {
                    System.out.println(((KMIPSecretData)managedObject).getName());
                    keyMaterial = ((KMIPSecretData) managedObject).export();
                }
                else if ( managedObject instanceof NAECertificate ) {
                    System.out.println(((NAECertificate) managedObject).getName());
                    keyMaterial = ((NAECertificate) managedObject).certificateExport();
                }

                System.out.println("Key Material = " + TTLVUtil.toHexString(keyMaterial));
                 
            }
            
     
            
        }  catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
        }
        finally {
        	if(session!=null)
        		session.closeSession();
		}
    }
    
    private static void usage() {
        System.err.println("Usage: java KMIPLocateSample clientCertAlias keyStorePassword  [-Name KeyName]");
        System.exit(-1);
    }
}
