/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard Java and JCE classes. 
import java.security.Security;
import java.util.Set;

import com.ingrian.internal.kmip.api.CryptographicAlgorithms.Algorithm;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;

/**
 * This sample program uses the KMIP Locate operation to get a set of 
 * unique identifiers for server managed keys with attribtues matching
 * a specified set of properties.
 * 
 * A custom attribute named x-int is deleted in a batch operation in the 
 * KMIP Session  for all of the located keys. In accordance with the KMIP 
 * standard, an attribute name beginning "x-" is a custom attribute. 
 * Unlike standard KMIP attributes, which are specified in client Java
 * by specifying a value in the KMIPAttribute Java Enum, a custom KMIP
 * attribute is specified by a String name beginning with "x-".
 *
 * KMIP attributes are roughly equivalent to NAE Custom attributes, except
 * they are specified by the KMIP standards document and that client defined
 * attributes must begin with "x-".
 *
 */

public class KMIPDeleteAttributeSample
{
    
    public static void main( String[] args ) throws Exception
    {
       if (args.length != 2)
        {
                usage();
        } 
 
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        KMIPSession session=null;
        try {
            // create NAE Session: pass in NAE client certificate information - client key and
            // keystore password
            session  = KMIPSession.getSession(new NAEClientCertificate( args[0],  args[1].toCharArray()));

            /* This Set<String> collection will hold the unique identifiers of the keys
             * matching the criteria (algorithm = RSA, length=2048
             */
            Set<String> managedObjectIdentifiers;
            
            /* this KMIPAttributes object will contain the KMIPAttribute(s) and the
             * values to match for the keys being searched for on the server
             * 
             */
            KMIPAttributes locateAttributes = new KMIPAttributes();
            // add CryptographicAlgorithm and length to the attributes to be matched
            locateAttributes.add( KMIPAttribute.CryptographicAlgorithm, Algorithm.rsa );
            locateAttributes.add( KMIPAttribute.CryptographicLength, 2048 );
            
            /* Add a custom KMIP integer attribute at index 0 with the value 1 */
            locateAttributes.add( "x-int1", 0, 1);

            /* this is also the sole attribute to be deleted. */
            KMIPAttributes deleteAttributes = new KMIPAttributes();
            deleteAttributes.add("x-int1", 0, 1);
            
            /* Locate all RSA keys with a length of 2048 and x-int1 = 1 */
            managedObjectIdentifiers = session.locate( locateAttributes );
            
            if (managedObjectIdentifiers != null ) {
                System.out.println("\n\nFound " + managedObjectIdentifiers.size() + " managed objects matching criteria.");                
                System.out.println("\n\nKeys with attributes rsa, 2048 and custom attribute x-int=1");
                
                for (String uid : managedObjectIdentifiers ) {
                    System.out.println("\n\nManaged Object UniqueIdentifier: \t" + uid);
                    Object thingee = session.getManagedObject(uid);

                    /* Convert each key into the proper type of object
                     * representing the managed key */
                    if (( thingee instanceof NAEPublicKey  ) || 
                            ( thingee instanceof NAEPrivateKey ) || 
                            ( thingee instanceof NAESecretKey  ) )
                    {
                        NAEKey key;
                        if ( thingee instanceof NAEPublicKey )
                            key = (NAEPublicKey) thingee;
                        else if ( thingee instanceof NAEPrivateKey )
                            key = (NAEPrivateKey) thingee;
                        else
                            key = (NAESecretKey) thingee;
                        
                        System.out.println("\tName: \t" + key.getName());
                        /* delete the x-int1 attribute */
                        key.deleteKMIPAttributes(deleteAttributes);
                    }
                }
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
        System.err.println("Usage: java KMIPDeleteAttributeSample clientCertAlias keyStorePassword");
        System.exit(-1);
    }

}
