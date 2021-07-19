/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.util.Set;

import org.apache.commons.codec.binary.Hex;

import com.ingrian.internal.kmip.api.ObjectType;
import com.ingrian.security.nae.IngrianProvider;
import static com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.KMIPTemplate;
import com.ingrian.security.nae.NAECertificate;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;

/**
 * This sample shows how to locate certificates matching specified KMIP Attribute criteria, 
 * find the managed obejct's name and type of object from the server.
 */

public class KMIPCertLocateSample
{
    static final String certBytes = "30820312308201faa003020102020101300d06092a864886f70d0101050500303b310b3009060355040613025553310d300b060355040a130454455354310e300c060355040b13054f41534953310d300b060355040313044b4d4950301e170d3130313130313233353935395a170d3230313130313233353935395a303b310b3009060355040613025553310d300b060355040a130454455354310e300c060355040b13054f41534953310d300b060355040313044b4d495030820122300d06092a864886f70d01010105000382010f003082010a0282010100ab7f161c0042496ccd6c6d4dadb919973435357776003acf54b7af1e440afb80b64a8755f8002cfeba6b184540a2d66086d74648346d75b8d71812b205387c0f6583bc4d7dc7ec114f3b176b7957c422e7d03fc6267fa2a6f89b9bee9e60a1d7c2d833e5a5f4bb0b1434f4e795a41100f8aa214900df8b65089f98135b1c67b701675abdbc7d5721aac9d14a7f081fcec80b64e8a0ecc8295353c795328abf70e1b42e7bb8b7f4e8ac8c810cdb66e3d21126eba8da7d0ca34142cb76f91f013da809e9c1b7ae64c54130fbc21d80e9c2cb06c5c8d7cce8946a9ac99b1c2815c3612a29a82d73a1f99374fe30e54951662a6eda29c6fc411335d5dc7426b0f6050203010001a321301f301d0603551d0e0416041404e57bd2c431b2e816e180a19823fac858273f6b300d06092a864886f70d01010505000382010100a876adbc6c8e0ff017216e195fea76bff61a567c9a13dc50d13fec12a4273c441547cfabcb5d61d991e966319df72c0d41ba826a45112ff26089a2344f4d71cf7c921b4bdfaef1600d1baaa15336057e014b8b496d4fae9e8a6c1da9aeb6cbc960cbf2fae77f587ec4bb282045338845b88dd9aeea53e482a36e734e4f5f03b9d0dfc4cafc6bb34ea9053e52bd609ee01e86d9b09fb51120c19834a997b09ce08d79e81311762f974bb1c8c09186c4d78933e0db38e905084877e147c78af52fae07192ff166d19fa94a11cc11b27ed050f7a27fae13b205a574c4ee00aa8bd65d0d7057c985c839ef336a441ed53a53c6b6b696f1bdeb5f7ea811ebb25a7f86";

    public static void main( String[] args ) throws Exception
    {
        if ( args.length != 3 )
        {
            usage();
        } 

        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        KMIPSession session  =null;
        try {

            // create NAE Session: pass in NAE Client Certificate clicnt key and keystore password
            session  = KMIPSession.getSession(new NAEClientCertificate( args[0], args[1].toCharArray()));
            //import the certificate
            NAEParameterSpec spec = new NAEParameterSpec( args[2], 1024, 
                    (KMIPAttributes)null, session);
            byte[] c = Hex.decodeHex(certBytes.toCharArray());
            NAECertificate.importCertificate(c, null, spec);
            //This set holds the managed object unique identifiers (UIDs) 

            Set<String> managedObjectIdentifiers;
            
            // Locate managed objects with ObjectType Certificate and crypto length = 2048
            // and Issuer Distinguished Name = "CN=KMIP,OU=OASIS,O=TEST,C=US"
            // by adding the KMIPAttribute name and the value to a KMIPAttributes 
            // object
            
            KMIPAttributes queryAttributes = new KMIPAttributes();
            queryAttributes.add( KMIPAttribute.CryptographicLength, 2048 );
            queryAttributes.add( KMIPAttribute.ObjectType, ObjectType.ObjectTypes.Certificate );
            
            // Have the session locate the keys matching the queryAttributes:
            
            managedObjectIdentifiers = session.locate( queryAttributes );
            System.out.println("Managed objects with attributes rsa, 2048:");

            // loop through the UIDs of the matching managed objects
            
            for (String uid : managedObjectIdentifiers ) {
                System.out.println("Managed object Unique Identifier: " + uid);

                // get the objects as Java client NAEKeys or KMIPSecretData objects
                // (Note: Secret Data doesn't have KMIP attributes of  
                // algorithm or length, and will not be found by this query,
                // but is included here for completeness.
                
                Object managedObject = session.getManagedObject(uid);
                if ( managedObject instanceof KMIPTemplate ) break;
                if ( managedObject instanceof NAEPublicKey )
                    System.out.println(((NAEPublicKey)managedObject).getName());
                else if ( managedObject instanceof NAEPrivateKey )
                    System.out.println(((NAEPrivateKey)managedObject).getName());
                else if ( managedObject instanceof NAESecretKey )
                    System.out.println(((NAESecretKey)managedObject).getName());
                else if ( managedObject instanceof KMIPSecretData ) {
                    System.out.println(((KMIPSecretData)managedObject).getName());
                }
                else if ( managedObject instanceof NAECertificate ) {
                    System.out.println("Object is a certificate");
                    System.out.println(((NAECertificate) managedObject).getName());
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
        System.err.println("Usage: java KMIPCertLocateSample clientCertAlias keyStorePassword certName");
        System.exit(-1);
    }
}
