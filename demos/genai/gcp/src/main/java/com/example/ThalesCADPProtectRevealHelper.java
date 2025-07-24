package com.example;



import com.centralmanagement.CipherTextData;
import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/


/**
 * This sample shows how to encrypt/decrypt data using protect/reveal API's in
 * CADP for JAVA.
 */
public class ThalesCADPProtectRevealHelper extends ThalesProtectRevealHelper {


	public ThalesCADPProtectRevealHelper(String keymanagerhost, String registrationToken, String metadata,
			String policyType, boolean showmetadata)

	{
		try {

			// Register the Client
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keymanagerhost,
					registrationToken.toCharArray()).build();

			// creates provider object.
			CentralManagementProvider clientManagementProvider = new CentralManagementProvider(registerClientParams);
			clientManagementProvider.addProvider();
			this.metadata = metadata;
			this.policyType = policyType;
			this.showmetadata = showmetadata;

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public ThalesCADPProtectRevealHelper(String keyManagerHost, String registrationToken)

	{
		try {

			// Register the Client
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
					registrationToken.toCharArray()).build();

			// creates provider object.
			CentralManagementProvider clientManagementProvider = new CentralManagementProvider(registerClientParams);
			clientManagementProvider.addProvider();

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void main(String[] args) {
		if (args.length != 7) {
			System.err.println(
					"Usage: java ProtectRevealSample keyManagerHost registrationToken protectionPolicyName userName policyType showmetadata operation");
			System.exit(-1);
		}
		String keyManagerHost = args[0];
		String registrationToken = args[1];
		String protectionPolicyName = args[2];
		String userName = args[3];
		String policyType = args[4];
		String showmetadataarg = args[5];
		String reprotectinput = args[6];
		
		

		boolean showmetadata = showmetadataarg.equalsIgnoreCase("true");


		String plainText = "DVM Altenwerth Run North Wadeville NV 66427-5919";
		//String plainText = "10100004yj-XU-Adh3";

		// String plainText = "96";

		ThalesCADPProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keyManagerHost, registrationToken, null,
				policyType, showmetadata);
		tprh.policyName = protectionPolicyName;
		tprh.revealUser = userName;
		String revealdata = null;
		
		switch (reprotectinput) {
		
		case "reprotect":

			String[] reprotect = { plainText };
			if (policyType.equalsIgnoreCase("external"))
				tprh.metadata = "1010000";
			tprh.reprotectData(reprotect, protectionPolicyName, showmetadata, policyType);

			for (int i = 0; i < reprotect.length; i++) {
				System.out.println("reprotected data " + reprotect[i]);
			}
			break;
		case "protect":

			String encryptedData = tprh.protectData(plainText, protectionPolicyName, policyType);

			System.out.println("Protected Data :" + encryptedData);
			break;
		case "reveal":
			encryptedData = plainText;		
			if (!tprh.showmetadata) {
				System.out.println("metadata " + tprh.metadata);
				revealdata = tprh.revealData(tprh.metadata + encryptedData, protectionPolicyName, policyType);
			} else
				revealdata = tprh.revealData(encryptedData, protectionPolicyName, policyType);
			System.out.println("Reveal Data :" + revealdata);
			break;
		default:
			encryptedData = tprh.protectData(plainText, protectionPolicyName, policyType);

			System.out.println("Protected Data :" + encryptedData);
			 revealdata = null;
			if (!tprh.showmetadata) {
				System.out.println("metadata " + tprh.metadata);
				revealdata = tprh.revealData(tprh.metadata + encryptedData, protectionPolicyName, policyType);
			} else
				revealdata = tprh.revealData(encryptedData, protectionPolicyName, policyType);
			System.out.println("Reveal Data :" + revealdata);
			break;

		}
		

	}

	public String revealData(String encryptedData, String protectionPolicyName,  String policyType) {


	//	System.out.println("username is in reveal " + this.revealUser);
		CipherTextData encryptedDataObject = new CipherTextData();
		if (policyType.equalsIgnoreCase("external"))
			encryptedDataObject.setVersion(metadata.getBytes());

		encryptedDataObject.setCipherText(encryptedData.getBytes());

		byte[] decryptedData = CryptoManager.reveal(encryptedDataObject, protectionPolicyName, this.revealUser);

		String return_value = new String(decryptedData);
	 

		return return_value;  
	}

	public String protectData(String plainText, String protectionPolicyName, String policyType) {

		String return_value = plainText;

		this.policyType = policyType;

		if (isValid(plainText)) {
			CipherTextData encryptedDataObject = CryptoManager.protect(plainText.getBytes(), protectionPolicyName);

			return_value = new String(encryptedDataObject.getCipherText());


			if (policyType.equalsIgnoreCase("internal")) {
				if (!this.showmetadata) {
					return_value = parseString(return_value);
				}
				this.metadata = return_value.substring(0, 7);
			} else {
				this.metadata = new String(encryptedDataObject.getVersion());

			}

		}

		return return_value; 
	}

	public String[] reprotectData(String[] plainText, String protectionPolicyName, boolean showkey, String policyType) {

		String[] return_value = plainText;
		this.policyType = policyType;

		CipherTextData[] cipherTextDataObject = new CipherTextData[plainText.length];

		try {

			for (int i = 0; i < cipherTextDataObject.length; i++) {

				cipherTextDataObject[i] = new CipherTextData();
				cipherTextDataObject[i].setCipherText(plainText[i].getBytes());
				if (policyType.equalsIgnoreCase("external"))
					cipherTextDataObject[i].setVersion(metadata.getBytes());

				if (cipherTextDataObject[i].getErrorMessage() != null) {
					System.out
							.println("Error Message for item " + i + " : " + cipherTextDataObject[i].getErrorMessage());
				} else {
					System.out.println("Protected data for item from args " + i + " : "
							+ new String(cipherTextDataObject[i].getCipherText()));
				}
			}

			// perform reprotect operation
			cipherTextDataObject = CryptoManager.reprotect(cipherTextDataObject, protectionPolicyName);

			for (int i = 0; i < cipherTextDataObject.length; i++) {
				if (cipherTextDataObject[i].getErrorMessage() != null) {
					System.out
							.println("Error Message for item " + i + " : " + cipherTextDataObject[i].getErrorMessage());
				} else {
					return_value[i] = new String(cipherTextDataObject[i].getCipherText());
					System.out.println("Re protected data for item " + i + " : " + return_value[i]);
				}

			}

		} catch (Exception e) {
			e.printStackTrace();
		}

		return return_value; 
	}

}