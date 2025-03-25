
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
 * This sample shows how to encrypt/decrypt bulk data using protect/reveal API's in
 * CADP for JAVA.
 */
public class ProtectRevealBulkDataSample {

    public static void main(String[] args) {
        if (args.length != 5) {
            System.err.println(
                    "Usage: java ProtectRevealBulkDataSample keyManagerHost registrationToken protectionPolicyName userName plainText");
            /*
             * Usage: keyManagerHost : keyManager IP
             * Usage: registrationToken : registrationtoken from the keyManager
             * Usage: protectionPolicyName : policy name to perform reprotect operation
             * Usage: userName : Username for reveal operation
             * Usage: plainText : array of data to protect eg. 123456789,123456789999,12345678999
             *
             * Note: Refer to Thales documentation for more information.
             */
            System.exit(-1);
        }
        String keyManagerHost = args[0];
        String registrationToken = args[1];
        String protectionPolicyName = args[2];
        String userName = args[3];
        String[] plainText = args[4].split(",");

        try {

            // Register the Client
            RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
                    registrationToken.toCharArray()).build();

            // Creates provider object.
            CentralManagementProvider centralManagementProvider = new CentralManagementProvider(registerClientParams);
            centralManagementProvider.addProvider();

            CipherTextData[] cipherTextDataObject = protectBulkData(plainText, protectionPolicyName);

            for(int i=0; i<cipherTextDataObject.length; i++) {
                /**
                 * For Internal Version
                 * This will return version header prepended to the ciphertext. Thus cipherTextDataObject.getVersion() will return null.
                 */
                System.out.println("Protected Data for " + plainText[i] + " : " + new String(cipherTextDataObject[i].getCipherText()));

                /**
                 * For External Version
                 * System.out.println("Protected Data for " + plainText[i] + " : " + new String(cipherTextDataObject[i].getCipherText()));//This will return ciphertext
                 * System.out.println("Version Header for " + plainText[i] + " : " + new String(cipherTextDataObject[i].getVersion()));//This will have version header information
                 */
            }

            byte[][] revealedData = revealBulkData(cipherTextDataObject, protectionPolicyName, userName);

            for(int i=0; i< revealedData.length; i++) {
                System.out.println("Revealed Data for " + new String(cipherTextDataObject[i].getCipherText()) + " : " + new String(revealedData[i]));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static CipherTextData[] protectBulkData(String[] plainText, String protectionPolicyName){
        CipherTextData[] cipherTextDataObject = new CipherTextData[plainText.length];
        // Execute protect operation inside loop for every plaintext
        for(int i=0; i< plainText.length; i++) {
            cipherTextDataObject[i] = CryptoManager.protect(plainText[i].getBytes(), protectionPolicyName);
        }
        return cipherTextDataObject;
    }

    private static byte[][] revealBulkData(CipherTextData[] cipherTextDataObject, String protectionPolicyName, String userName){
        byte[][] revealedData = new byte[cipherTextDataObject.length][];
        // Execute reveal operation inside loop for every protected text
        for(int i=0; i< cipherTextDataObject.length; i++) {
            revealedData[i] = CryptoManager.reveal(cipherTextDataObject[i], protectionPolicyName, userName);
        }
        return revealedData;
    }
}