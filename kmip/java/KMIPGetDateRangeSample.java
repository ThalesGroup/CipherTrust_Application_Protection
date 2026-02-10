/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.Set;

import com.ingrian.internal.kmip.api.CryptographicAlgorithms.Algorithm;
import com.ingrian.internal.ttlv.TTLVUtil;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPLinkAttribute;
import com.ingrian.security.nae.KMIPObjectGroup;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;

/**
 * Sample KMIP program to find all RSA keys with an initial date between a 
 * given set of start and end dates.
 * 
 * This sample shows how to Locate keys matching a particular criteria and access 
 * the values of all of the supported non-custom KMIP attributes.
 * 
 * Keys are found matching algorithm RSA and key length 2048 and for each key located
 * the attributes 
 *          - ApplicationSpecificInformation
 *          - ContactInformation
 *          - CryptographicAlgorithm 
 *          - CryptographicLength
 *          - Digest
 *          - InitialDate
 *          - ObjectGroup
 *          - ObjectType
 *          - Link
 *
 * Note 
 * 1) The KMIPAttributes object is used for both submitting parameter values
 *    to be Located and to return the values for a particular key. It is
 *    analogous to the SQLDA object in JDBC which can be used for query, result set
 *    access and update. 
 * 2) The attributes which are not scalar values return wrapper objects from
 *    which the individual attribute values may be obtained
 * 3) Scalar values are returned as Java scalar values   
 */


public class KMIPGetDateRangeSample
{
    
    static SimpleDateFormat outputDateFormat = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss");
    static SimpleDateFormat inputDateFormat = new SimpleDateFormat("MM.dd.yyyy");
    static Calendar start;
    static Calendar end;
    
    
    public static void main( String[] args ) throws Exception
    {

        if (args.length != 4)
        {
                usage();
        } 
        
        // set the dates
        
        start = Calendar.getInstance();
        end = Calendar.getInstance();
        
        try {
          start.setTime((Date) inputDateFormat.parse(args[2]));
          end.setTime((Date) inputDateFormat.parse(args[3]));;
        }
        catch (ParseException pe ) {
            System.err.println("Problem parsing date argument");
            System.err.println(pe.getMessage());
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

            // Create session to KMIP port based on authentication by an NAEClientCertificate 
            session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));

            // KMIPAttribute set to hold unique Key Manager identifiers for located keys
            Set<String> managedObjectIdentifiers;

            // This instance of KMIPAttributes will be used as the KMIP attributes and 
            // values to be searched for. Note that the date range is indicated by 
            // addding two InitialDate attributes to the locateAttributes
            KMIPAttributes locateAttributes = new KMIPAttributes();
            locateAttributes.add( KMIPAttribute.CryptographicAlgorithm, Algorithm.rsa );
            locateAttributes.add( KMIPAttribute.InitialDate, 0, start);
            locateAttributes.add( KMIPAttribute.InitialDate, 1, end);
            
            // This instance of KMIPAttributes will specify the set of KMIP attributes
            // to be returned from the Key Manager
            KMIPAttributes getAttributes = new KMIPAttributes();
            getAttributes.add(KMIPAttribute.ApplicationSpecificInformation);
            getAttributes.add(KMIPAttribute.CryptographicAlgorithm); // implied null value
            getAttributes.add(KMIPAttribute.CryptographicLength);
            getAttributes.add(KMIPAttribute.ObjectType);
            getAttributes.add(KMIPAttribute.ContactInformation);
            getAttributes.add(KMIPAttribute.Digest);
            getAttributes.add(KMIPAttribute.InitialDate);
            getAttributes.add(KMIPAttribute.Link);
            getAttributes.add(KMIPAttribute.ObjectGroup);

            // Locate the keys with matching attributes
            managedObjectIdentifiers = session.locate( locateAttributes );
            
            if (managedObjectIdentifiers != null ) {
                System.out.println("\n\nFound " + managedObjectIdentifiers.size() + 
                        " managed objects matching key Locate criteria.");
                
                System.out.println("\n\nKeys with attribute rsa and initial date between " +
                        outputDateFormat.format(start.getTime()) + " and " + outputDateFormat.format(end.getTime()));

                // for each object found, query all the non-custom attributes
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
                        KMIPAttributes returnedAttributes = getAttrs(key, getAttributes);
                        printKeyInfo( returnedAttributes );
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
    

    private static void usage() {
        System.err.println("Usage: java KMIPgetDateRangeSample clientCertAlias keyStorePassword startDate endDate");
        System.err.println("Input dates numerically as MM.dd.yyyy");
        System.exit(-1);
    }

    private static void printKeyInfo( KMIPAttributes returnedAttributes ) {
        
        System.out.println("\tAlgorithm: \t" + returnedAttributes.getCryptographicAlgorithm().getPrintName());
        System.out.println("\tLength: \t" + returnedAttributes.getCryptographicLength());
        System.out.println("\tObject Type: \t"+returnedAttributes.getObjectType().getPrintName());
        
        printApplicationSpecificInformation( returnedAttributes );
        
        printContactInformation( returnedAttributes );
        
        printDigest( returnedAttributes );
        
        printInitialDate( returnedAttributes );
        
        printLink( returnedAttributes );
        
        System.out.println("\tObjectGroup(s):");
        ArrayList<KMIPObjectGroup> ogList = (ArrayList<KMIPObjectGroup>) returnedAttributes.getObjectGroupList();
        if ( ogList.size() == 0 ) {
            System.out.println("\t\tNo Object Groups.");
        }
        else {
            for (KMIPObjectGroup og: ogList) {
                System.out.println("\t\tGroup: " + og.getGroup().getObjectGroup());
            }    
        }
        
        printContactInformation( returnedAttributes );
    }

    private static void printLink(KMIPAttributes returnedAttributes) {
        System.out.println("\tLink:");
        KMIPLinkAttribute link = returnedAttributes.getLink();
        if ( link != null ) {
            System.out.println("\t\t Link Type: " + link.getLinkName());
            System.out.println("\t\t Linked Object Identifier: " + link.getLinkedObjectIdentifier());
        }
        else System.out.println("\t\tNo linked object.");
    }

    private static void printInitialDate(KMIPAttributes returnedAttributes) {
        if (returnedAttributes.getInitialDate() != null) {
            System.out.println("\tInitial Date: \t" + outputDateFormat.format(returnedAttributes.getInitialDate().getTime()));
        }
        else System.out.println("\t\t\tNo initial date.");
    }

    private static void printDigest(KMIPAttributes returnedAttributes) {
        System.out.println("\tDigest:");
        if (returnedAttributes.getDigest() != null ) {
            System.out.println("\t\t Hashing algorithm: \t" + 
                    returnedAttributes.getDigest().getHashingAlgorithm());
            System.out.println("\t\t Digest: " + 
                    TTLVUtil.toHexString(returnedAttributes.getDigest().getDigestValue()));
        }
        else System.out.println("\t\t\tNo managed object digest.");
    }

    private static void printContactInformation(KMIPAttributes returnedAttributes) {
        System.out.println("\tContact information:");
        if (returnedAttributes.getContactInformation() != null ) {
            System.out.println("\t\tContact information: \t" + returnedAttributes.getContactInformation());
         }
         else System.out.println("\t\tNo contact information");
    }

    private static void printApplicationSpecificInformation(
            KMIPAttributes returnedAttributes) {
        System.out.println("\tApplication Specific Information: ");
        if (returnedAttributes.getApplicationSpecificInformation() != null ) {
           System.out.println("\t\t Application Namespace: \t" + returnedAttributes.getApplicationSpecificInformation().getApplicationNamespace().getNameValue());
           System.out.println("\t\t Application Data: \t" + returnedAttributes.getApplicationSpecificInformation().getApplicationData().getDataValue());
        }
        else System.out.println("\t\t\tNo application specific information");
    }

    private static KMIPAttributes getAttrs( NAEKey key, KMIPAttributes attributes ) 
            throws NAEException, Exception {

        return key.getKMIPAttributes(attributes);
    }
}
