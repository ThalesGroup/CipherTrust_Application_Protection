/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;
import java.text.FieldPosition;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Set;

import com.ingrian.internal.kmip.api.CryptographicAlgorithms.Algorithm;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPApplicationSpecificInformation;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPNameAttribute;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;

/**
 * This sample shows how to locate a key via KMIP and modify a standard KMIP
 * attribute.
 *
 * Keys with algorithm = RSA and length = 2048 are found.
 * Get the Name attribute for each matching key and
 * For each matching key, the Application Specific Information is
 * altered on the Key Manager.
 *
 */

public class KMIPModifySample
{
    
    static SimpleDateFormat sdf = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss");
    
    public static void main( String[] args ) throws Exception
    {
       if (args.length != 2)
        {
                usage();
        } 
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        // get the list of all registered JCE providers
        Provider[] providers = Security.getProviders();
        for (int i = 0; i < providers.length; i++)
            System.out.println(providers[i].getInfo());
        KMIPSession session=null;
        try {

            // create a KMIPSession: pass in NAE client X.509 key and keyStore password
           session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));

            // create key KMIPAttribute object with a list of attributes to match

            Set<String> managedObjectIdentifiers;
            KMIPAttributes locateAttributes = new KMIPAttributes();
            locateAttributes.add( KMIPAttribute.CryptographicAlgorithm, Algorithm.rsa );
            locateAttributes.add( KMIPAttribute.CryptographicLength, 2048 );

            KMIPAttributes getAttributes = new KMIPAttributes();
            getAttributes.add(KMIPAttribute.Name);

            managedObjectIdentifiers = session.locate( locateAttributes );
            
            if (managedObjectIdentifiers != null ) {
                System.out.println("\n\nFound " + managedObjectIdentifiers.size() + " managed objects matching criteria.");
                
                System.out.println("\n\nKeys with attributes rsa, 2048 and object group");

                for (String uid : managedObjectIdentifiers ) {
                    System.out.println("\n\nManaged Object UniqueIdentifier: \t" + uid);
                    Object managedObject = session.getManagedObject(uid);
					if ( managedObject == null ) continue; // not a key

                    if (( managedObject instanceof NAEPublicKey  ) || 
                            ( managedObject instanceof NAEPrivateKey ) || 
                            ( managedObject instanceof NAESecretKey  ) )
                    {
                        NAEKey key;
                        if ( managedObject instanceof NAEPublicKey )
                            key = (NAEPublicKey) managedObject;
                        else if ( managedObject instanceof NAEPrivateKey )
                            key = (NAEPrivateKey) managedObject;
                        else
                            key = (NAESecretKey) managedObject;
                        
                        System.out.println("\tName: \t" + key.getName()); 
                        
                        // Retrieve a KMIP attribute - in this case, Name.
                        KMIPAttributes returnedAttributes = key.getKMIPAttributes(getAttributes);
                        KMIPNameAttribute name = returnedAttributes.getNameAttribute();
                        System.out.println("Name attribute: " + name.getNameValue().getNameValue());
                        
                        //Modify the Application Specific Information for this key - if it has any
                        
                        KMIPAttributes modAttributes = new KMIPAttributes();

                        String ts = timestamp();
			 modAttributes.add(
                                new KMIPApplicationSpecificInformation("namespace-"+ts, ts),
                                0);
                        try {       
                           // throws NAE error if the key does not already have attribute being modified
                           key.modifyKMIPAttributes(modAttributes);
                        }
                        catch(NAEException nae) {
                            if (!nae.getMessage().contains("Object does not have the specified attribute"))
                                throw nae;
                        }
                           
                    }
                    else if ( managedObject instanceof KMIPSecretData ) {
                        System.out.println(((KMIPSecretData)managedObject).getName());

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
    
    public static String timestamp() {
        SimpleDateFormat sdf = new SimpleDateFormat("H:m:s");
        StringBuffer ts = new StringBuffer();
        sdf.format(new Date(), ts, new FieldPosition(0) );
        return ts.toString();
    }
    
    private static void usage() {
        System.err.println("Usage: java KMIPModifySample clientCertAlias keyStorePassword");
        System.exit(-1);
    }
}
