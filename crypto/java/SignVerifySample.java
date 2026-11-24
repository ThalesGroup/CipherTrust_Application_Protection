import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;
import com.centralmanagement.SignatureData;

/**
 * A sample class to demonstrate the end-to-end workflow for signing and verifying data
 * using the locally implemented, policy-driven CentralManagement JCE provider.
 */
public class SignVerifySample {

    public static void main(String[] args) {
        if (args.length != 3) {
            System.err.println(
                    "Usage: java SignVerify keyManagerHost registrationToken signingPolicyName");
            /*
             * Usage: keyManagerHost : keyManager IP
             * Usage: registrationToken : registrationtoken from the keyManager
             * Usage: signingPolicyName : signingPolicy name to perform sign and verify operation
             *
             * Note: Refer to Thales documentation for more information.
             */
            System.exit(-1);
        }
        String keyManagerHost = args[0];
        String registrationToken = args[1];
        String signingPolicyName = args[2];

        String plainText = "dataToSigndataToSigndataToSigndataToSigndataToSign";

        try {

            // Register the Client
            RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
                    registrationToken.toCharArray()).build();

            // Creates provider object
            CentralManagementProvider centralManagementProvider = new CentralManagementProvider(registerClientParams);
            centralManagementProvider.addProvider();

            SignatureData signedData = CryptoManager.sign(plainText.getBytes(), signingPolicyName);

            
			/**
			 * For Internal Version
			 * This will return version header prepended to the signature. Thus signedData.getVersion() will return null.
			 */

            System.out.println("Signed Data: " + new String(signedData.getSignature()));
			
			/**
			 * For External Version
			 * System.out.println("Signed Data: " + new String(signedData.getSignature()));-- This will return signature
			 * System.out.println("External Version: " + new String(signedData.getVersion()));-- This will have version header information
			 */

            boolean verify = CryptoManager.verify(plainText.getBytes(), signedData, signingPolicyName);

            if (verify)
                System.out.println("Signature verified.");
            else
                System.out.println("Signature verification failed.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
