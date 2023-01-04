/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Set;

import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;

/*
 * Sample KMIP program to demonstrate CADP for JAVA support for 

 * KMIP managed object lifecycle using the KMIP State
 * attribute and associated date attributes. 
 * 
 * A key is created with a 256-bit AES Symmetric Key with the
 * given name from the command line. NOTE: If it already exists
 * it will be deleted.
 * 
 * The key will shown to be in Pre-Active state with only 
 * an initial date attribute.
 * 
 * The Key will then be activated via the KMIP Activate 
 * client-to-server operation. The State is shown to be 
 * Active and the attributes include an Activation Date
 * KMIP attribute.
 * 
 * The Key is then deactivated by adding a Deactivation
 * Date equal to the Activation Date. The state is shown
 * to be Deactivated and the list of attributes includes
 * a Deactivation Date KMIP attribute.
 */

public class KMIPDatesAndStatesSample
{
    static SimpleDateFormat sdf = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss");
    
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
            // create key custom attributes

            NAEKey key = null;
                        
            deleteIfExists(keyName, session, key);
            
            /* create a secret key using JCE key generator */
            NAEParameterSpec spec = new NAEParameterSpec( keyName, keyLength, 
                    (KMIPAttributes) null, session);
            KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
            kg.init(spec); 
            SecretKey secretKey = kg.generateKey();
            System.out.println("Created new key " + ((NAEKey) secretKey).getName());
            
            /* cast to NAEKey and list the default attribute names */
            Set<String> defaultAttributes = ((NAEKey) secretKey).listKMIPAttributes();
            System.out.println(defaultAttributes);

            key = ((NAEKey) secretKey);
            KMIPAttributes getState = new KMIPAttributes();
            getState.add(KMIPAttribute.State);
            getState.add(KMIPAttribute.ActivationDate);
            getState.add(KMIPAttribute.InitialDate);
            getState.add(KMIPAttribute.DeactivationDate);
            
            KMIPAttributes gotState = key.getKMIPAttributes(getState);
            System.out.println("State = " + gotState.getState());
            System.out.println("InitialDate  = " + sdf.format(gotState.getDate(KMIPAttribute.InitialDate).getTime()));
            System.out.println("ActivationDate  = " + ( ( gotState.getDate(KMIPAttribute.ActivationDate) != null ) ? 
                           sdf.format(gotState.getDate(KMIPAttribute.ActivationDate).getTime()) : "null"));
 
            key = ((NAEKey) secretKey);
            
            System.out.println("Activating:");

            key.activate();
            gotState = key.getKMIPAttributes(getState);
            defaultAttributes = ((NAEKey) secretKey).listKMIPAttributes();
            System.out.println(defaultAttributes);
            System.out.println("State = " + gotState.getState());
            System.out.println("ActivationDate  = " + ( ( gotState.getDate(KMIPAttribute.ActivationDate) != null ) ? 
                    sdf.format(gotState.getDate(KMIPAttribute.ActivationDate).getTime()) : "null"));

// now deactivate it

            Calendar c = Calendar.getInstance();
            c.setTimeInMillis((gotState.getDate(KMIPAttribute.ActivationDate)).getTime().getTime());
            
            System.out.println("Deactivating as of " + sdf.format(c.getTime()));
            KMIPAttributes modDates = new KMIPAttributes();
            modDates.addDate(KMIPAttribute.DeactivationDate, c);
            key.addKMIPAttributes(modDates);;
            
            defaultAttributes = ((NAEKey) secretKey).listKMIPAttributes();
            System.out.println(defaultAttributes);
            gotState = key.getKMIPAttributes(getState);
            System.out.println("State = " + gotState.getState());
            System.out.println("Dectivation Date  = " + ( ( gotState.getDate(KMIPAttribute.DeactivationDate) != null ) ? 
                    sdf.format(gotState.getDate(KMIPAttribute.ActivationDate).getTime()) : "null"));
  
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

    private static NAEKey deleteIfExists(String keyName, KMIPSession session,
            NAEKey key) throws Exception {
        /* does the key exist? if so, delete it */
        /* get..Key method is merely a placeholder for a managed object 
         * with that name. */
        key = NAEKey.getSecretKey(keyName, session);
        /* getUID() will throw an exception if the key does not exist */
        if ( key.getUID() != null ) {
            System.out.println("Deleting key " + keyName + " with UID=" + key.getUID());
            key.delete();
        }
        return key;
    }
    
    private static void usage() {
        System.err.println("Usage: java KMIPDatesAndStatesSample clientCertAlias keyStorePassword keyName");
        System.exit(-1);
    }
}
