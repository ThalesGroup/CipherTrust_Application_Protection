/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 

import java.security.Security;

import com.ingrian.internal.kmip.api.Attribute;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPSecretData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;

/**
 * This sample shows how to get Secret data custom attribute object from the Key Manager.
 */

public class KMIPSecretDataGetCustomAttributeSample {
	public static void main(String[] args) throws Exception {
		if (args.length != 4) {
			usage();

		}
		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());
		String secretDataName =   args[2];
		String custattrib =  args[3];
		// create NAE Session: pass in Key Manager user name and password
		KMIPSession session = KMIPSession.getSession(new NAEClientCertificate( args[0],  args[1].toCharArray()));
		KMIPAttributes getAttributes = new KMIPAttributes();
		if (custattrib.contains("#")) {
			String[] attrs = custattrib.split("#");
			for (String atr : attrs) {
				getAttributes.add(atr);
			}
		} else {
			getAttributes.add(custattrib);
		}
		try {

			// create the secret data object as a KMIP secret data Password type
			KMIPSecretData secretDataManagedObject = new KMIPSecretData(
					secretDataName, KMIPSecretData.SecretDataType.Password,
					session);
			KMIPAttributes returnedAttributes = secretDataManagedObject.getKMIPAttributes(getAttributes);
			printCustomAttribute(returnedAttributes);
			
		} catch (Exception e) {
			e.printStackTrace();
                       System.out.println("The Cause is " + e.getMessage() + ".");
	               throw e;
		}
		finally{
        	if(session!=null)
        		session.closeSession();
        }
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
				else if (customDataTypes.equals("Interval"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeInt(a
									.getAttributeName().getCustomName(), a
									.getAttributeIndex().getAttributeIndex()));
				else if (customDataTypes.equals("Boolean"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeBoolean(a
									.getAttributeName().getCustomName(), a
									.getAttributeIndex().getAttributeIndex()));
				else if (customDataTypes.equals("BigInteger"))
					System.out.println("CustomAttribute value: "
							+ returnedAttributes.getCustomAttributeBigInteger(a
									.getAttributeName().getCustomName(), a
									.getAttributeIndex().getAttributeIndex()));

			}
		}

	}

	private static void usage() {
		System.err
				.println("Usage: java KMIPSecretDataGetCustomAttributeSample clientCertAlias ClientcertPassword secretDataName customAttribute");
		System.exit(-1);
	}
}
