/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.Security;
import java.util.Arrays;

import com.ingrian.internal.ttlv.TTLVUtil;
import com.ingrian.internal.kmip.api.CryptographicUsageMask.UsageMask;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEParameterSpec;

/**
 * This sample shows how to register and export a KMIPSecretData
 * managed object to and from the Key Manager.
 *
 * - The secret data is the public key of a dynamically generated
 * public/private key pair(in practice the secret data can be 
 * array of bytes) 
 * - The KMIPSecretData object is created and then the array of 
 * bytes is registered with the Key Manager
 * - The KMIPSecretData object export() method brings a copy of the 
 * data for this named Secret Data managedObject back from the Key Manager
 * as a byte array.
 * - The original and exported byte arrays are compared 
 *
 */

public class KMIPSecretDataSample
{
    public static void main( String[] args ) throws Exception
    {
        if (args.length < 2)
        {
             usage();
        } 
        
        String keyName =  args.length == 3 ? args[2] : "KMIPSecretData";
        
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
       KMIPSession session  = KMIPSession.getSession(new NAEClientCertificate( args[0],  args[1].toCharArray()));
        try {
            // generate the secret data (the bytes of a public key)
			// For IBM java ,use the IBMJCE provider instead of SUN/SunRsaSign.
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA", "SunRsaSign");
            SecureRandom random = SecureRandom.getInstance("SHA1PRNG", "SUN");
            keyGen.initialize(1024, random);
            KeyPair sunPair = keyGen.generateKeyPair();
            PublicKey pub = sunPair.getPublic();

            byte[] data = pub.getEncoded();

            // create NAE Session: pass in Key Manager user name and password
           // KMIPSession session  = KMIPSession.getSession(new NAEClientCertificate( args[0],  args[1]));
            // create secret data managed object ParameterSpec
            KMIPAttributes initialAttributes = new KMIPAttributes();
            initialAttributes.add(KMIPAttribute.CryptographicUsageMask, (int)
                    ( UsageMask.Verify.getValue() ));

            NAEParameterSpec spec = new NAEParameterSpec(keyName, 1024, 
                    (KMIPAttributes) initialAttributes, session);
            //create the secret data object as a KMIP secret data Password type
            KMIPSecretData secretDataManagedObject = new KMIPSecretData(keyName, 
                    KMIPSecretData.SecretDataType.Password, session);
            // register the secret data bytes
            secretDataManagedObject.register(data, spec);

            // now export() a copy of the secret data back from the Key Manager
            
            byte[] exportedSecretData = secretDataManagedObject.export();
            
            // compare the original and exported bytes
            if ( ( exportedSecretData != null ) && Arrays.equals( exportedSecretData,data ) ) 
                System.out.println("Exported secret data equals original");
            else {
                System.out.println("Uh-oh!");
            }
            
            // print the bytes and close the session
            System.out.println("original: " + TTLVUtil.toHexString(data));
            System.out.println("exported: " + TTLVUtil.toHexString(exportedSecretData));
        	}  
        catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
        }
        	finally{
        		if(session!=null)
        		session.closeSession();
    }
    }
    	
    
    private static void usage() {
        System.err.println("Usage: java KMIPSecretDataSample clientCertAlias keyStorePassword [keyName]");
        System.exit(-1);
    }
}
