/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import com.ingrian.security.nae.ConjunctiveOperator;
import com.ingrian.security.nae.CustomAttributes;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.UserKeysDetail;

/**
 * This sample shows how to fetch owner keys and global keys.
 * 
 */
public class KeyNameSample {

	public static void main(String[] args) {
		
		/**
		 * KeyName api if used with valid Key Manager user name and password then it
		 * fetches all the keys names belongs to the user and global keys
		 * as per the attribute passed. Please read Javadoc for their value.
		 */
		if (args.length > 14) {
			System.err
					.println("Usage: java KeyNameSample -user [userName] -password [password] -attr [attributName]"
							+ "-attrV [attributeValue] -fingerprint [fingerprint] -offset [keyOffset] -max [maxKeys]");
			System.exit(-1);
		}
		
		String username = null;
		String password = null;
		String attributeName = null;
		String attributeValue = null;
		String fingerprint = null;
		int offset = 0;
		int max = 1; //maximum key needs to be fetched should be atleast 1

		// extracting values from the given input argument. May have null values.
		for (int i = 0; i < args.length; i++) {
			if ("-user".equals(args[i]))
				username = args[i + 1];
			else if ("-password".equals(args[i]))
				password =  args[i + 1];
			else if ("-attr".equals(args[i]))
				attributeName =  args[i + 1];
			else if ("-attrV".equals(args[i]))
				attributeValue =  args[i + 1];
			else if ("-fingerprint".equals(args[i]))
				fingerprint =  args[i + 1];
			else if ("-offset".equals(args[i]))
				offset = Integer.parseInt( args[i + 1]);
			else if ("-max".equals(args[i]))
				max = Integer.parseInt( args[i + 1]);
		}

		if (username != null && password != null) {
			NAESession session = null;
			try {
				session = NAESession.getSession(username,
						password.toCharArray());

				CustomAttributes attr = new CustomAttributes();
				if(attributeValue != null){
				attr.addAttributeForKeyName(attributeName, attributeValue);
				attr.addAttributeForKeyName(attributeName + "-1", attributeValue);
				}	
				UserKeysDetail keyNames = NAEKey.getKeyNames(attr, fingerprint, offset, max, session, ConjunctiveOperator.OR);
				System.out.println("Key count: " + keyNames.getKeyCount());
				System.out.println("Total Keys: " + keyNames.getTotalKeys());
				System.out.println("KeyNames: " + keyNames.getKeyNames());
				System.out.println("#####################");
			} finally {
				if (session != null)
					session.closeSession();
			}
		} else {
			// In this case all the global keys are fetched through global
			// session.
			System.out.println("Global Keys are: ");
			UserKeysDetail keyNames = NAEKey.getKeyNames(null);
			System.out.println("Key count: " + keyNames.getKeyCount());
			System.out.println("Total Keys: " + keyNames.getTotalKeys());
			System.out.println("KeyNames: " + keyNames.getKeyNames());
		}

	}
}

