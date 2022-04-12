/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.io.IOException;
import java.security.Security;
import java.util.ArrayList;
import java.util.Set;

import javax.crypto.KeyGenerator;

import com.ingrian.internal.kmip.api.CryptographicAlgorithms.Algorithm;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPBatchItemResult;
import com.ingrian.security.nae.KMIPBatchResults;
import com.ingrian.security.nae.KMIPResultStatuses.Statuses;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAESecretKey;

/**
 * Sample KMIP program to to demonstrate the KMIP Session Batch feature
 * in the CADP for JAVA
 * This sample shows how to create, manipulate and delete keys using a KMIP 
 * Batch Session.
 * The keys will be a 256-bit AES Symmetric Key.
 * Ten keys are created in a single batch request to the Key Manager.
 * The keys are located and ContactInformation attribute is added.
 * The program pauses for a CRLF, so you may see the keys and attributes
 * on the server.
 * Continuing the program, a batch modification is made to the Contact Information
 * attribute for all of the created keys in another single request.
 * The program again pauses so you may see the keys and modified attributes
 * on the server.
 * Then the keys are deleted in a single deleteAll() request.
 */

public class KMIPBatchSample
{
    public static void main( String[] args ) throws Exception
    {

        KMIPSession session = null;

        int keyLength = 256;
        if (args.length != 3)
        {
                usage();
        } 

        String keyName = args[2];
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());

        try {

            // create KMIP Session - specify client X.509 certificate and keystore password
            session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));
            // create key custom attributes
            session.startBatching();
            System.out.println("Batching set to " + session.isBatching());

            for (int i=0; i<10; i++) {

                /* create a secret key using JCE key generator */
                NAEParameterSpec spec = new NAEParameterSpec( keyName+"-"+i, keyLength, 
                        (KMIPAttributes) null, session);
                KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
                kg.init(spec); 
                kg.generateKey();
            }

            KMIPBatchResults kbr = session.flushBatch();
            for (KMIPBatchItemResult batchResult : kbr.values()) {
                if (batchResult.getStatus() == Statuses.Success ) {
                System.out.println(batchResult.getOperation().getPrintName() + " : " + 
                        batchResult.getStatus().getPrintName());
                System.out.println("UIDs affected: " + batchResult.getUIDs());
                }
                else {
                    System.out.println(batchResult.getOperation().getPrintName() + " OPERATION FAILED: " + 
                            batchResult.getStatusMessage());
                }
            }
            System.out.println("Batching set to " + session.isBatching());
            // the KMIPsession is now not in batching mode. KMIP Operations will be sent
            // to the server when the line of code is executed. Operations are shown
            // which add, modify, or delete attributes in one request, with the KMIP CADP for JAVA
            // session utilizing KMIP batching implicitly based on sets of UIDs
            
            KMIPAttributes queryAttributes = new KMIPAttributes();
            queryAttributes.add(KMIPAttribute.CryptographicAlgorithm, Algorithm.aes);
            queryAttributes.add(KMIPAttribute.CryptographicLength, 256);
            
            // Have the session locate the keys matching the queryAttributes:
            
            Set<String> managedObjectIdentifiers = session.locate( queryAttributes );

            // loop through the UIDs of the matching managed objects
            KMIPAttributes addAttrs = new KMIPAttributes();
            addAttrs.add(KMIPAttribute.ContactInformation,0,"Contact Information");
            for (String uid : managedObjectIdentifiers ) {
                System.out.println("Managed object Unique Identifier: " + uid);

                // get the objects as Java client NAEKeys or KMIPSecretData objects
                // (Note: Secret Data doesn't have KMIP attributes of  
                // algorithm or length, and will not be found by this query,
                // but is included here for completeness.
                
                Object managedObject = session.getManagedObject(uid);
                if ( managedObject instanceof NAESecretKey ) {
                    NAESecretKey nsk = (NAESecretKey) managedObject;
                    nsk.refreshKMIPInfo();
                    if (nsk.getName().startsWith("KMIPBatch")) {
                        System.out.println(((NAESecretKey)managedObject).getName());

                    }
                    nsk.addKMIPAttributes(addAttrs);
                }
            }
            waitForInput();
            KMIPAttributes modAttrs = new KMIPAttributes();
            modAttrs.add(KMIPAttribute.ContactInformation, 0,"Modified Contact Information");
            Set<String> modUIDs = session.modifyAllAttributes(managedObjectIdentifiers, modAttrs);
            System.out.println("Modified " + modUIDs.size() +" attributes in a single request."); 
            waitForInput();
            Set<String> delUIDs = session.deleteAll(new ArrayList<String>(managedObjectIdentifiers));
            System.out.println("Deleted " + delUIDs.size() + " managed objects in a single request.");
        }  catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
        }
	     finally{
        	if(session!=null)
        		session.closeSession();
	     }
        
       
    }
    
    private static void waitForInput() {
        byte[] discard = new byte[2];
        System.out.println("Press a key to continue");
        try {
            System.in.read(discard);
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
    
    private static void usage() {
        System.err.println("Usage: java KMIPBatchSample clientCertAlias keyStorePassword keyName");
        System.err.println("keyName is the base name for created keys. A key number is appended");
        System.err.println("when the key is created i.e. testkey-0, testkey-1, testkey-2, etc.");
        System.exit(-1);
    }
    
}
