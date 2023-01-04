/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Security;
import java.util.Arrays;
import java.util.Set;

import org.apache.commons.codec.binary.Hex;

import com.ingrian.internal.kmip.api.ObjectType.ObjectTypes;
import com.ingrian.internal.ttlv.TTLVUtil;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPCertificateIdentifier;
import com.ingrian.security.nae.KMIPCertificateIssuer;
import com.ingrian.security.nae.KMIPCertificateSubject;
import com.ingrian.security.nae.KMIPCertificateTypes;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAECertificate;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEParameterSpec;

/**
 * This sample shows how to register and export an NAECertificate 
 * managed object to and from the Key Manager via KMIP.
 * 
 * - The certificate managed object is registered via NAECertificate
 * in combination with a KMIPSession NAEParameter from an array of 
 * bytes 
 * - The following KMIP Certificate attributes are queried for the
 * just-created certificate:
 * 
 * KMIPAttribute.CertificateIdentifier
 * KMIPAttribute.ObjectType
 * KMIPAttribute.CertificateIssuer
 * KMIPAttribute.CertificateType
 * KMIPAttribute.CertificateSubject
 * 
 * - The NAECertificate object export() method brings a copy of the 
 * data for this named Certificate managedObject back from the Key Manager
 * as a byte array.
 * - The original and exported byte arrays are compared 
 *
 */

public class KMIPCertificateSample
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
        KMIPSession session=null;
        try {
            // create NAE Session: pass in Key Manager user name and password
             session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));
            // create certificate managed object ParameterSpec

            NAEParameterSpec spec = new NAEParameterSpec( args[2], 1024, 
                    (KMIPAttributes)null, session);
            //import the certificate
            byte[] c = Hex.decodeHex(certBytes.toCharArray());
            NAECertificate.importCertificate(c, null, spec);

            // query the certificate attributes via KMIP
            
            session.getUID(args[2]);
            Set<String> attrNames = session.listKMIPAttributes(args[2]);
            System.out.println("Attributes: " + attrNames );

            NAECertificate cert = new NAECertificate(args[2], session );

            KMIPAttributes getAttributes = new KMIPAttributes();
            getAttributes.add(KMIPAttribute.CertificateIdentifier);
            getAttributes.add(KMIPAttribute.ObjectType);
            getAttributes.add(KMIPAttribute.CertificateIssuer);
            getAttributes.add(KMIPAttribute.CertificateType);
            getAttributes.add(KMIPAttribute.CertificateSubject);
            KMIPAttributes gotAttributes = cert.getKMIPAttributes(getAttributes);
            
            KMIPCertificateIdentifier certIdentifier = gotAttributes.getCertificateIdentifier();
            KMIPCertificateSubject subject = gotAttributes.getCertificateSubject();
            KMIPCertificateTypes certType = gotAttributes.getCertificateType();
            KMIPCertificateIssuer issuer = gotAttributes.getCertificateIssuer();
            ObjectTypes ot = gotAttributes.getObjectType();
            
            if (ot != null ) {
                System.out.println("Object Type KMIP Attribute: " + ot.getPrintName());
            } else {
                System.err.println("Object Type KMIP Attribute is null.");
            }
            
            if ( certType != null ) {
                System.out.println("Certificate Type KMIP Attribute: " + certType.getPrintName());
            } else {
                System.err.println("Certificate Type KMIP Attribute is null.");
            }
            
            if ( certIdentifier == null ) {
                System.err.println( "Certificate Identifier KMIP Attribute is null." );
            }
            else {
                System.out.println( "Certificate Identifier KMIP Attribute:");
                System.out.println( "\tIssuer = " + certIdentifier.getIssuer());
                System.out.println( "\tSerial Number" + certIdentifier.getSerialNumber());
            }

            if ( issuer == null ) {
                System.err.println( "Certificate Issuer is null." );
            } else {
                System.out.println( "Certificate Issuer:");
                System.out.println( "\tIssuer Distinguished Name = " + issuer.getCertificateIssuerDistinguishedName());
                if ( issuer.getCertificateIssuerAlternativeName() != null ) {
                    System.out.println( "\tIssuer Alternative Name = " + issuer.getCertificateIssuerAlternativeName());
                }
            }

            if ( subject == null ) {
                System.err.println( "Certificate Subject is null." );
            } else {
                System.out.println( "Certificate Subject:");
                System.out.println( "\tSubject Distinguished Name = " +  subject.getCertificateSubjectDistinguishedName());
                if ( subject.getCertificateSubjectAlternativeName() != null ) {
                    System.out.println( "\tSubject Alternative Name = " + subject.getCertificateSubjectAlternativeName());
                }
            }
            
            // now export() a copy of the certificate back from the Key Manager
            byte[] exportedCert = cert.certificateExport();

            // compare the original and exported bytes
            if ( ( exportedCert != null ) &&
                    Arrays.equals(Hex.decodeHex(certBytes.toCharArray()), exportedCert) 
                    ) 
                System.out.println("Exported Certificate material equals original");
            else {
                System.out.println("Uh-oh!");
            }

            // print the bytes
            System.out.println("original: " + certBytes.toUpperCase());
            System.out.println("exported: " + TTLVUtil.toHexString(exportedCert));
            // delete the test cert and close the session
            cert.delete();
            
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
        System.err.println("Usage: java KMIPCertificateSample clientCertAlias keyStorePassword certName");
        System.exit(-1);
    }
}
