
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.RegisterClientParameters;

/**
 * This sample shows how to register client in CADP for JAVA.
 */
public class CADPClientRegistrationSample {

	public static void main(String[] args) {
		if (args.length != 2) {
			System.err.println("Usage: java CADPClientRegistrationSample keyManagerHost registrationToken");
			/*
			 * Usage: keyManagerHost : keyManager IP 
			 * Usage: registrationToken : registration token from the keyManager 
			 *
			 * Note: Refer to Thales documentation for more information.
			 */
			System.exit(-1);
		}

		try {
			String keyManagerHost = args[0];
			String registrationToken = args[1];

			// Creates RegisterClientParameters object - key manager default web port 443 is used
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
					registrationToken.toCharArray()).build();

			// Creates CentralManagementProvider object
			CentralManagementProvider centralManagementProvider = new CentralManagementProvider(registerClientParams);

			// Register the Client
			centralManagementProvider.addProvider();

		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}