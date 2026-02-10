/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Provider;
import java.security.Security;

import com.ingrian.security.nae.ConnectionDetails;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAESession;
/**
 * This sample shows how to create connections and fetch number of 
 * available and busy connections of a session.
 */
public class NAEConnectionSample {

	public static void main(String[] args) {
		if (args.length !=3)
		{
			System.err.println("Usage: java NAEConnectionSample userName password numOfConnectionsToCreate");
			/*
			 * Usage: userName key manager user name
			 * Usage: password key manager password
			 * Usage: numOfConnectionsToCreate number of connections to create on each key manager HostName/IP
			 * Note: Refer to Thales documentation for more information.
			 *
			*/
			System.exit(-1);
		}
		
		String userName  = args[0];
		String password  = args[1];
		String numOfConnectionsToCreate = args[2];

		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());

		NAESession session = null;
		try {
			session = NAESession.getSession(userName, password.toCharArray());
			// This will return ConnectionDetails object
			ConnectionDetails connectionDetails = session.getConnectionDetails();
			// This will return total number of available connections of a session
			// When session is created, number of available connection created is 1
			System.out.println("Number of available connections : " + connectionDetails.getTotalAvailableConnections());
			// This will create given number of available connections on key manager HostName/IP's of NAE_IP.1 property.
			// If multiple Key Manager's are present, it will create number of connections, multiple of given Key Manager's.
			session.createConnections(Integer.parseInt(numOfConnectionsToCreate));
			System.out.println("Number of available connections : " + connectionDetails.getTotalAvailableConnections());
			// This will return total number of busy connections of a session
			System.out.println("Number of busy connections : " + connectionDetails.getTotalBusyConnections());
		} catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			e.printStackTrace();
		} finally {
			if (session != null) {
				session.closeSession();
			}
		}
	}
}
