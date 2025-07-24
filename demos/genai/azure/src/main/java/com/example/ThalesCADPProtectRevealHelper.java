package com.example;
import com.centralmanagement.CipherTextData;
import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;

/**
 * ThalesCADPProtectRevealHelper extends ThalesProtectRevealHelper to provide
 * data protection and revelation functionalities specifically using the
 * Thales CipherTrust Application Data Protection (CADP) Java SDK.
 * It handles client registration with the CipherTrust Manager and performs
 * cryptographic operations.
 */
public class ThalesCADPProtectRevealHelper extends ThalesProtectRevealHelper {

	/**
	 * Constructor for ThalesCADPProtectRevealHelper.
	 * Initializes the helper and registers the client with the CipherTrust Manager.
	 *
	 * @param keymanagerhost The hostname or IP address of the CipherTrust Manager.
	 * @param registrationToken The registration token for client authentication.
	 * @param metadata Optional metadata string.
	 * @param policyType The type of policy ("internal" or "external").
	 * @param showmetadata A boolean indicating whether metadata should be shown.
	 */
	public ThalesCADPProtectRevealHelper(String keymanagerhost, String registrationToken, String metadata,
			String policyType, boolean showmetadata) {
		try {
			// Build registration parameters for the client
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keymanagerhost,
					registrationToken.toCharArray()).build();

			// Create a CentralManagementProvider object and add it to the security providers.
			// This registers the CADP client with the JVM.
			CentralManagementProvider clientManagementProvider = new CentralManagementProvider(registerClientParams);
			clientManagementProvider.addProvider();

			// Initialize instance variables from constructor parameters
			this.metadata = metadata;
			this.policyType = policyType;
			this.showmetadata = showmetadata;

		} catch (Exception e) {
			// Print stack trace if any error occurs during initialization/registration
			e.printStackTrace();
		}
	}

	/**
	 * Overloaded constructor for ThalesCADPProtectRevealHelper.
	 * Initializes the helper and registers the client with the CipherTrust Manager
	 * without specifying metadata or policy type initially.
	 *
	 * @param keyManagerHost The hostname or IP address of the CipherTrust Manager.
	 * @param registrationToken The registration token for client authentication.
	 */
	public ThalesCADPProtectRevealHelper(String keyManagerHost, String registrationToken) {
		try {
			// Build registration parameters for the client
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
					registrationToken.toCharArray()).build();

			// Create a CentralManagementProvider object and add it to the security providers.
			CentralManagementProvider clientManagementProvider = new CentralManagementProvider(registerClientParams);
			clientManagementProvider.addProvider();

		} catch (Exception e) {
			// Print stack trace if any error occurs during initialization/registration
			e.printStackTrace();
		}
	}

	/**
	 * Main method for demonstrating the functionality of ThalesCADPProtectRevealHelper.
	 * It allows running protection, revelation, or reprotection operations from the command line.
	 *
	 * @param args Command-line arguments:
	 * args[0]: keyManagerHost (CipherTrust Manager hostname/IP)
	 * args[1]: registrationToken
	 * args[2]: protectionPolicyName
	 * args[3]: userName (for reveal operations)
	 * args[4]: policyType ("internal" or "external")
	 * args[5]: showmetadataarg ("true" or "false")
	 * args[6]: operation ("protect", "reveal", "reprotect")
	 */
	public static void main(String[] args) {
		// Validate the number of command-line arguments
		if (args.length != 7) {
			System.err.println(
					"Usage: java ProtectRevealSample keyManagerHost registrationToken protectionPolicyName userName policyType showmetadata operation");
			System.exit(-1);
		}

		// Parse command-line arguments
		String keyManagerHost = args[0];
		String registrationToken = args[1];
		String protectionPolicyName = args[2];
		String userName = args[3];
		String policyType = args[4];
		String showmetadataarg = args[5];
		String reprotectinput = args[6]; // The operation to perform

		// Convert showmetadata argument to boolean
		boolean showmetadata = showmetadataarg.equalsIgnoreCase("true");

		// Sample plain text data for demonstration
		String plainText = "DVM Altenwerth Run North Wadeville NV 66427-5919";

		// Create an instance of ThalesCADPProtectRevealHelper
		ThalesCADPProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keyManagerHost, registrationToken, null,
				policyType, showmetadata);
		tprh.policyName = protectionPolicyName; // Set the policy name
		tprh.revealUser = userName; // Set the user for revelation

		String revealdata = null; // Variable to store revealed data

		// Perform the specified operation based on the 'reprotectinput' argument
		switch (reprotectinput) {
		case "reprotect":
			// Reprotect operation: re-encrypts already protected data (or plain text for demonstration)
			String[] reprotect = { plainText }; // Array of data to reprotect
			if (policyType.equalsIgnoreCase("external"))
				tprh.metadata = "1010000"; // Set dummy metadata for external policy reprotect example
			tprh.reprotectData(reprotect, protectionPolicyName, showmetadata, policyType);

			for (int i = 0; i < reprotect.length; i++) {
				System.out.println("reprotected data " + reprotect[i]);
			}
			break;
		case "protect":
			// Protect operation: encrypts plain text
			String encryptedData = tprh.protectData(plainText, protectionPolicyName, policyType);
			System.out.println("Protected Data :" + encryptedData);
			break;
		case "reveal":
			// Reveal operation: decrypts encrypted data
			encryptedData = plainText; // For this example, assuming plainText is already encrypted for reveal
			if (!tprh.showmetadata) {
				// If metadata is not shown, it needs to be prepended to the encrypted data for revelation
				System.out.println("metadata " + tprh.metadata);
				revealdata = tprh.revealData(tprh.metadata + encryptedData, protectionPolicyName, policyType);
			} else {
				// If metadata is shown (or not applicable for external policies), reveal directly
				revealdata = tprh.revealData(encryptedData, protectionPolicyName, policyType);
			}
			System.out.println("Reveal Data :" + revealdata);
			break;
		default:
			// Default case: perform both protect and reveal operations
			encryptedData = tprh.protectData(plainText, protectionPolicyName, policyType);
			System.out.println("Protected Data :" + encryptedData);
			revealdata = null;
			if (!tprh.showmetadata) {
				System.out.println("metadata " + tprh.metadata);
				revealdata = tprh.revealData(tprh.metadata + encryptedData, protectionPolicyName, policyType);
			} else {
				revealdata = tprh.revealData(encryptedData, protectionPolicyName, policyType);
			}
			System.out.println("Reveal Data :" + revealdata);
			break;
		}
	}

	/**
	 * Reveals (decrypts) encrypted data using the Thales CADP CryptoManager.
	 *
	 * @param encryptedData The encrypted data string to be revealed.
	 * @param protectionPolicyName The name of the policy under which the data was protected.
	 * @param policyType The type of policy ("internal" or "external").
	 * @return The decrypted plain text string.
	 */
	@Override
	public String revealData(String encryptedData, String protectionPolicyName, String policyType) {
		// Create a CipherTextData object to hold the encrypted data
		CipherTextData encryptedDataObject = new CipherTextData();
		// If policy type is external, set the version (metadata) in the CipherTextData object
		if (policyType.equalsIgnoreCase("external"))
			encryptedDataObject.setVersion(metadata.getBytes());

		// Set the actual ciphertext bytes
		encryptedDataObject.setCipherText(encryptedData.getBytes());

		// Call CryptoManager.reveal to decrypt the data
		byte[] decryptedData = CryptoManager.reveal(encryptedDataObject, protectionPolicyName, this.revealUser);

		// Convert the decrypted byte array back to a string
		String return_value = new String(decryptedData);
		return return_value;
	}

	/**
	 * Protects (encrypts) plain text data using the Thales CADP CryptoManager.
	 *
	 * @param plainText The plain text data string to be protected.
	 * @param protectionPolicyName The name of the policy to apply for protection.
	 * @param policyType The type of policy ("internal" or "external").
	 * @return The protected (encrypted) string.
	 */
	@Override
	public String protectData(String plainText, String protectionPolicyName, String policyType) {
		String return_value = plainText; // Initialize return value with plain text
		this.policyType = policyType; // Set the policy type

		// Validate the input plain text
		if (isValid(plainText)) {
			// Call CryptoManager.protect to encrypt the data
			CipherTextData encryptedDataObject = CryptoManager.protect(plainText.getBytes(), protectionPolicyName);

			// Get the ciphertext from the encrypted object
			return_value = new String(encryptedDataObject.getCipherText());

			// Handle metadata based on policy type and showmetadata flag
			if (policyType.equalsIgnoreCase("internal")) {
				if (!this.showmetadata) {
					// If metadata is not to be shown, parse it out from the beginning of the ciphertext
					return_value = parseString(return_value);
				}
				// Store the metadata (first 7 characters for internal policy)
				this.metadata = return_value.substring(0, 7);
			} else { // External policy
				// For external policy, metadata (version) is obtained from the encrypted object
				this.metadata = new String(encryptedDataObject.getVersion());
			}
		}
		return return_value;
	}

	/**
	 * Reprotects (re-encrypts) an array of data strings using the Thales CADP CryptoManager.
	 * This is useful for key rotation or policy changes.
	 *
	 * @param plainText An array of data strings (can be plain or already protected).
	 * @param protectionPolicyName The name of the policy to apply for reprotection.
	 * @param showkey A boolean flag (not directly used for key display in this method, but passed along).
	 * @param policyType The type of policy ("internal" or "external").
	 * @return An array of reprotected data strings.
	 */
	public String[] reprotectData(String[] plainText, String protectionPolicyName, boolean showkey, String policyType) {
		String[] return_value = plainText; // Initialize return value with input array
		this.policyType = policyType; // Set the policy type

		// Create an array of CipherTextData objects
		CipherTextData[] cipherTextDataObject = new CipherTextData[plainText.length];

		try {
			// Populate CipherTextData objects from the input array
			for (int i = 0; i < cipherTextDataObject.length; i++) {
				cipherTextDataObject[i] = new CipherTextData();
				cipherTextDataObject[i].setCipherText(plainText[i].getBytes());
				// If external policy, set the version (metadata)
				if (policyType.equalsIgnoreCase("external"))
					cipherTextDataObject[i].setVersion(metadata.getBytes());

				// Check for errors during CipherTextData object creation
				if (cipherTextDataObject[i].getErrorMessage() != null) {
					System.out
							.println("Error Message for item " + i + " : " + cipherTextDataObject[i].getErrorMessage());
				} else {
					System.out.println("Protected data for item from args " + i + " : "
							+ new String(cipherTextDataObject[i].getCipherText()));
				}
			}

			// Perform the reprotect operation using CryptoManager
			cipherTextDataObject = CryptoManager.reprotect(cipherTextDataObject, protectionPolicyName);

			// Update the return_value array with the reprotected data
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
			// Print stack trace for any exceptions during reprotection
			e.printStackTrace();
		}
		return return_value;
	}
}