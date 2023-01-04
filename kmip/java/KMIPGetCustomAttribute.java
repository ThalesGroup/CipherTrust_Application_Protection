/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.text.SimpleDateFormat;
import java.util.Set;

import com.ingrian.internal.kmip.api.Attribute;
import com.ingrian.internal.kmip.api.CryptographicAlgorithms.Algorithm;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;

/**
 * This KMIP CADP for JAVA sample shows how to Locate keys matching a particular criteria 
 * and access the values  of the supplied custom KMIP attributes.This sample will only work for RSA - 2048 keys * 
 * In this sample we are fetching only user's defined CustomAttribute of key using KMIP session.
 */

public class KMIPGetCustomAttribute {

	static SimpleDateFormat sdf = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss");

	public static void main(String[] args) throws Exception {

		if (args.length != 4) {
			usage();

		}
		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());
KMIPSession session=null;
		try {

			// Create session to KMIP port based on authentication by an
			// NAEClientCertificate
			session = KMIPSession
					.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));

			// KMIPAttribute set to hold unique Key Manager identifiers for
			// located keys
			Set<String> managedObjectIdentifiers;

			// This instance of KMIPAttributes will be used as the KMIP
			// attributes and
			// values to be searched for
			KMIPAttributes locateAttributes = new KMIPAttributes();
			locateAttributes.add(KMIPAttribute.CryptographicAlgorithm,
					Algorithm.rsa);
			locateAttributes.add(KMIPAttribute.CryptographicLength, 2048);

			// This instance of KMIPAttributes will specify the set of KMIP
			// attributes
			// to be returned from the Key Manager
			// KMIPAttributes addAttributes = new KMIPAttributes();
			// addAttributes.add("x-String", 1, "Hello");
			KMIPAttributes getAttributes = new KMIPAttributes();
			getAttributes.add(KMIPAttribute.ApplicationSpecificInformation);
			getAttributes.add(KMIPAttribute.CryptographicAlgorithm); // implied
																		// null
																		// value
			getAttributes.add(KMIPAttribute.CryptographicLength);
			getAttributes.add(KMIPAttribute.ObjectType);
			getAttributes.add(KMIPAttribute.ContactInformation);
			getAttributes.add(KMIPAttribute.Digest);
			getAttributes.add(KMIPAttribute.InitialDate);
			getAttributes.add(KMIPAttribute.Link);
			getAttributes.add(KMIPAttribute.ObjectGroup);
		
			String custattrib = args[3];
		
			if (custattrib.contains("#"))
			{
			String[] attrs = custattrib.split("#");
			for (String atr : attrs) {
				getAttributes.add(atr);
			}
			}
			else
			{
				getAttributes.add(custattrib);
			}

			// Locate the keys with matching attributes
			managedObjectIdentifiers = session.locate(locateAttributes);

			if (managedObjectIdentifiers != null) {

				// for each object found, query all the non-custom attributes
				for (String uid : managedObjectIdentifiers) {
				
					Object serverManagedObject = session.getManagedObject(uid);
					if (serverManagedObject == null)
						continue; // not a key
					if (isKey(serverManagedObject)) {
						// NAEKey is the superclass of public/private and secret
						// keys
						NAEKey key;
						if (serverManagedObject instanceof NAEPublicKey)
							key = (NAEPublicKey) serverManagedObject;
						else if (serverManagedObject instanceof NAEPrivateKey)
							key = (NAEPrivateKey) serverManagedObject;
						else
							key = (NAESecretKey) serverManagedObject;

						locateAttributes.getAttributes();
						// retrieve and print the key's attributes
						if (key.getName().equals(args[2])) {
							// key.addKMIPAttributes(addAttributes);
							System.out.println("\tName: \t" + key.getName());
							
							KMIPAttributes returnedAttributes = getAttrs(key,
									getAttributes);
							// printKeyInfo(returnedAttributes);
							printCustomAttribute(returnedAttributes);
						}
					} else if (serverManagedObject instanceof KMIPSecretData) {

						// KMIPSecretData managed objects do not inherit from
						// NAEKey
						// coerce to a KMIPSecretData and print the name of the
						// object
						System.out
								.println(((KMIPSecretData) serverManagedObject)
										.getName());

					}
				}
			}
		} 
		catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			e.printStackTrace();
                        throw e;
		}
		finally {
        	if(session!=null)
        		session.closeSession();
		}
	}

	private static boolean isKey(Object serverManagedObject) {
		return (serverManagedObject instanceof NAEPublicKey)
				|| (serverManagedObject instanceof NAEPrivateKey)
				|| (serverManagedObject instanceof NAESecretKey);
	}

	private static void printCustomAttribute(KMIPAttributes returnedAttributes) {

		for (Attribute a : returnedAttributes.attributes) {
			if (a.getAttributeName().getCustomName() != null) {
				System.out.println("CustomAttribute: "
						+ a.getAttributeName().getCustomName()
						+ " "
						+ a.getAttributeIndex().getAttributeIndex()
						+ " "
						+ returnedAttributes.getCustomAttributeType(a
								.getAttributeName().getCustomName()));
				String customDataTypes = returnedAttributes
						.getCustomAttributeType(
								a.getAttributeName().getCustomName())
						.toString();
				if (customDataTypes.equals("TextString"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeTextString(a
									.getAttributeName().getCustomName(), a
									.getAttributeIndex().getAttributeIndex()));
				else if (customDataTypes.equals("DateTime"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeCalendar(
									a.getAttributeName().getCustomName(),
									a.getAttributeIndex().getAttributeIndex())
									.getTimeInMillis());
				else if (customDataTypes.equals("Integer"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeInt(a
									.getAttributeName().getCustomName(), a
									.getAttributeIndex().getAttributeIndex()));
				else if (customDataTypes.equals("Boolean"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeBoolean(a
									.getAttributeName().getCustomName(), a
									.getAttributeIndex().getAttributeIndex()));

			}
		}

	}

	private static KMIPAttributes getAttrs(NAEKey key, KMIPAttributes attributes)
			throws NAEException, Exception {

		return key.getKMIPAttributes(attributes);
	}

	private static void usage() {
		System.err
				.println("Usage: java KMIPGetCustomAttribute clientCertAlias keyStorePassword keyname customAttribute1|customAttribute2|customAttribute2");
		System.exit(-1);
	}
}
