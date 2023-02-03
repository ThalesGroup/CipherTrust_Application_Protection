/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Import standard Java and JCE classes. 
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Security;

import com.ingrian.internal.kmip.api.CryptographicUsageMask.UsageMask;
// CADP for JAVA class imports
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPKeyFormatTypes.KeyFormatType;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;

/**
 * This sample shows how to generate asymmetric public/private key pairs 
 * on the client and then register the keys on the Key Manager via KMIP. 
 * The keys are generated and registered as RSA-2048
 */

public class KMIPKeyPairSample
{
    static String algorithm = "RSA";
    static int length = 2048;
    static KeyFormatType keyFormat = KeyFormatType.PKCS1;
    
    public static void main( String[] args ) throws Exception
    {
	    if (args.length != 4)
        {
                usage();
        } 

        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        String privateKeyName = args[2];
        String publicKeyName = args[3];
        KMIPSession session=null;
        try {
            
	        // generate the public/private key pairs with client-side provider
	        
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance(algorithm);
            System.out.println("Provider: " + keyGen.getProvider().getName());
            keyGen.initialize(length);
            KeyPair generatedKeyPair = keyGen.generateKeyPair();
            
            // get the key material
            PrivateKey priv = generatedKeyPair.getPrivate();
            PublicKey pub = generatedKeyPair.getPublic();
            byte[] privKeyMaterial = priv.getEncoded();
            byte[] pubKeyMaterial = pub.getEncoded();
           
            // Register keys on the Key Manager

            // create NAE Session using a client certificate
            
           session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));
            
            // create a spec for the public key
            KMIPAttributes initialAttributes = new KMIPAttributes();
            initialAttributes.add(KMIPAttribute.CryptographicUsageMask, (int)
                    ( UsageMask.Verify.getValue() ));

            NAEParameterSpec spec = new NAEParameterSpec( publicKeyName, length,
                                   (KMIPAttributes) initialAttributes, session);
            
            // create a public key - note: names must match
            NAEPublicKey naePub = NAEKey.getPublicKey( publicKeyName, session);
            
            // register the key
            String pubUID = naePub.registerKey(pubKeyMaterial, algorithm, keyFormat, spec);
            // print the Key Manager unique identifier for the key
            System.out.println("Created public key: " + pubUID);
            
            // do the same for the private key
            initialAttributes = new KMIPAttributes();
            initialAttributes.add(KMIPAttribute.CryptographicUsageMask, (int)
                    ( UsageMask.Sign.getValue() ));

            spec = new NAEParameterSpec( privateKeyName,length, 
                    (KMIPAttributes) initialAttributes, session);
            NAEPrivateKey naePriv = NAEKey.getPrivateKey( privateKeyName, session);

            // remove PKCS#8 header from the key material
            byte[] truncatedKeyMaterial = new byte[privKeyMaterial.length-26];
            System.arraycopy(privKeyMaterial, 26, truncatedKeyMaterial, 0, privKeyMaterial.length-26);
            
            String privUID = naePriv.registerKey(truncatedKeyMaterial, algorithm, keyFormat, spec);
            System.out.println("Created private key: " + privUID);
            
            // Set the link attribute for the keys on the Key Manager
            
            naePriv.link(naePub);
            naePub.link(naePriv);
            System.out.println("Linked keys");

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
        System.err.println("Usage: java KMIPKeyPairSample clientCertAlias keyStorePassword privateKeyName publicKeyName");
        System.exit(-1);
    }
    
}
