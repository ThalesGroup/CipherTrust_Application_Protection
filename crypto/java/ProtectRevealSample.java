
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import com.centralmanagement.CipherTextData;
import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;

/**
 * This sample shows how to encrypt/decrypt data using protect/reveal API's in
 * CADP for JAVA.
 */
public class ProtectRevealSample {

	public static void main(String[] args) {
		if (args.length != 4) {
			System.err.println(
					"Usage: java ProtectRevealSample keyManagerHost registrationToken protectionPolicyName userName");
			System.exit(-1);
		}
		String keyManagerHost = args[0];
		String registrationToken = args[1];
		String protectionPolicyName = args[2];
		String userName = args[3];

		String plainText = "0123456789012345";
		
		try {

			// Register the Client
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
					registrationToken.toCharArray()).build();

			//creates provider object.
			CentralManagementProvider centralManagementProvider = new CentralManagementProvider(registerClientParams);
			centralManagementProvider.addProvider();
		
			CipherTextData encryptedDataObject = CryptoManager.protect(plainText.getBytes(), protectionPolicyName);
			
			/**
			 * For Internal Version
			 * This will return version header appended to the ciphertext. Thus encryptedDataObject.getVersion() will return null.
			 */
			System.out.println("Encrypted Data: " + new String(encryptedDataObject.getCipherText())); 
			
			/**
			 * For External Version
			 * System.out.println("Encrypted Data: " + new String(encryptedDataObject.getCipherText()));-- This will return ciphertext
			 * System.out.println("Encrypted Data: " + new String(encryptedDataObject.getVersion()));-- This will have version header information
			 */
			byte[] decryptedData = CryptoManager.reveal(encryptedDataObject, protectionPolicyName,userName);
			System.out.println("Decrypted Data: " + new String(decryptedData));
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}