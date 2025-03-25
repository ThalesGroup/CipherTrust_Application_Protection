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
 * This sample shows how to reprotect cipherTextdata array using reprotect API's in
 * CADP for JAVA.
 * 
 */
public class ReprotectSample {

	public static void main(String[] args) {
		
		if (args.length != 4) {
			System.err.println(
					"Usage: java ReprotectSample keyManagerHost registrationToken protectionPolicyName plainTextArray");
			/*
			 * Usage: keyManagerHost : keyManager IP 
			 * Usage: registrationToken : registrationtoken from the keyManager 
			 * Usage: protectionPolicyName : policy name to perform reprotect operation
			 * Usage: plainTextArray : array of data to reprotect eg. 123456789,123456789999,12345678999
			 *
			 * Note: Refer to Thales documentation for more information.
			 */
			System.exit(-1);
		}

		String keyManagerHost = args[0];
		String registrationToken = args[1];
		String protectionPolicyName = args[2];
		String[] plainText = args[3].split(",");
		CipherTextData[] cipherTextDataObject = new CipherTextData[plainText.length];

		try {
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
					registrationToken.toCharArray()).build();

			CentralManagementProvider centralManagementProvider = new CentralManagementProvider(registerClientParams);
			centralManagementProvider.addProvider();

			// To perform reprotect operation first we should have protected data array
			// which we want to reprotect
			for (int i = 0; i < cipherTextDataObject.length; i++) {

				cipherTextDataObject[i] = CryptoManager.protect(plainText[i].getBytes(), protectionPolicyName);

			}

			// perform reprotect operation
			cipherTextDataObject = CryptoManager.reprotect(cipherTextDataObject, protectionPolicyName);

			for (int i = 0; i < cipherTextDataObject.length; i++) {
				if (cipherTextDataObject[i].getErrorMessage() != null) {
					System.out
							.println("Error Message for item " + i + " : " + cipherTextDataObject[i].getErrorMessage());
				} else {
					System.out.println("Re protected data for item " + i + " : "
							+ new String(cipherTextDataObject[i].getCipherText()));
				}

			}

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}