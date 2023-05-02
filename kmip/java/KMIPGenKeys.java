/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.KeyPair;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Security;
import java.util.ArrayList;
import java.util.Map;

import com.ingrian.internal.config.Config;
import com.ingrian.internal.kmip.api.OperationTypes.OperationType;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPQueryFunction.Query;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.RSAKeyPairGenerator;

/**
 * This sample shows how to requesting a Key Manager to
 * generate a public/private RSA key pair via the KMIP
 * Create Key Pair operation.
 * 
 * The key created will be an RSA key pair with the
 * given name and length. The names need to be unique
 * for KMIP so the CADP for JAVA adds "Public" and "Private"
 * suffixes to make the key names unique.
 * 
 * The keys for this test case are then deleted.
 *  
 */

public class KMIPGenKeys
{
    static String format = "RSA";
    public static void main( String[] args )throws Exception
    {
        
        if (args.length != 4)
        {
            usage();
        }
        int length = Integer.valueOf( args[3]);

        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        // create KMIP Session - specify client X.509 certificate and keystore password
        KMIPSession session  = KMIPSession.getSession(new NAEClientCertificate( args[0],args[1].toCharArray()));

        KeyPair sunPair = null;
        try {
            // verify Key Manager supports key pair generation
            if (!queryKeyGen(session)) {
                System.err.println("Key Manager does not support key pair generation");
                System.exit(0);
            }
            
            deleteIfNecessary( NAEKey.getPublicKey(  args[2].trim() + Config.s_publicKeyGenSuffix, session) );
            deleteIfNecessary( NAEKey.getPrivateKey(  args[2].trim() + Config.s_privateKeyGenSuffix, session ) );
            
            RSAKeyPairGenerator keyGen = new RSAKeyPairGenerator();

            NAEParameterSpec spec = new NAEParameterSpec(  args[2].trim(), length, 
                    (KMIPAttributes) null, session);
            keyGen.initialize(spec, null);
            sunPair = keyGen.generateKeyPair();

            PrivateKey priv = sunPair.getPrivate();
            PublicKey pub = sunPair.getPublic();

            NAEPrivateKey naePriv = (NAEPrivateKey) priv;
            NAEPublicKey naePub = (NAEPublicKey) pub;

            System.out.println("\n\n----------------------------\n");
            System.out.println("Key length = " + length);
            System.out.println("Private key name           : " + naePriv.getName());
            System.out.println("Private key format         : " + naePriv.getFormat());
            System.out.println("Private key algorithm      : " + naePriv.getAlgorithm() );
            System.out.println("Private key encoded length : " + naePriv.getKeySize() );
            System.out.println("Public key name            : " + naePub.getName());
            System.out.println("Public key format          : " + naePub.getFormat());
            System.out.println("Public key algorithm      : "
            		+ ""  + naePub.getAlgorithm());
            System.out.println("Public key encoded length  : " + naePub.getKeySize());
           /* ((NAEPrivateKey)priv).delete();
            ((NAEPublicKey)pub).delete();*/


        }  catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
            throw e;
        }
        	finally{
        	if(session!=null)
        		session.closeSession();
        }
    }

    public static String toHexString(byte[] bytes) {
        String result = "";
        for (byte b : bytes) {
            result += (((b & 0xFF) < 0x10) ? "0" : "")
                    + Integer.toHexString(b & 0xFF).toUpperCase();
        }
        return result;
    }

    public static boolean queryKeyGen(KMIPSession session) {
        // create list of Key Manager properties to query
        ArrayList<Query> query = new ArrayList<Query>();
        query.add(Query.QueryOperations);

        /* execute the query on the session */
        Map<Query, ArrayList<String>> queryResult2 = session.query(query);
        ArrayList<String> operations = queryResult2.get(Query.QueryOperations);
        return operations.contains( OperationType.Create.getPrintName() );
    }

    private static void deleteIfNecessary( NAEKey key ) {
        // delete key if present;
        try {
           key.delete();
        }
        catch( NAEException ignore ) {
            
        }
        
    }
    
    private static void usage() {
        System.err.println("Usage: java KMIPGenKeys clientCertAlias keyStorePassword keyName length");
        System.exit(-1);
    }
}
