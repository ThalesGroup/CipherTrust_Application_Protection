/**
 * Sample code is provided for educational purposes.
 * No warranty of any kind, either expressed or implied by fact or law.
 * Use of this item is not restricted by copyright or license terms.
 */
import java.security.Provider;
import java.security.Security;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEConnectionInfo;
import com.ingrian.security.nae.NAEConnectionStats;
import com.ingrian.security.nae.NAESession;
/**
 * This sample shows how to retrieve connection statistics across all active
 * sessions using NAEConnectionStats.
 *
 * Two sessions are opened in sequence so that the aggregated stats can be
 * observed as each session is added.  This demonstrates that
 * NAEConnectionStats reports the combined view across every live session,
 * not just the most recently opened one.
 *
 * Prerequisites:
 *   Set Enable_NAE_Connection_Stats=yes in CADP_for_JAVA.properties before starting the JVM.
 */
public class NAEConnectionInfoSample {

	public static void main(String[] args) {
		if (args.length != 2)
		{
			System.err.println("Usage: java NAEConnectionInfoSample userName password");
			/*
			 * Usage: userName key manager user name
			 * Usage: password key manager password
			 * Note: Refer to Thales documentation for more information.
			 *
			*/
			System.exit(-1);
		}

		String userName = args[0];
		String password = args[1];

		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());

		NAESession session1 = null;
		NAESession session2 = null;
		try {
			// --- Open first session ---
			System.out.println("\nOpening session 1...");
			session1 = NAESession.getSession(userName, password.toCharArray());

			// NAEConnectionStats aggregates connection info across all active sessions.
			// Enable_NAE_Connection_Stats=yes must be set in CADP_for_JAVA.properties.
			NAEConnectionStats stats = new NAEConnectionStats();

			System.out.println("\n--- Connection stats with 1 active session ---");
			printStats(stats);

			// --- Open second session ---
			System.out.println("\nOpening session 2...");
			session2 = NAESession.getSession(userName, password.toCharArray());

			// Stats now aggregate connection pools from both sessions.
			// The totals and per-CTM breakdown should reflect the combined pool.
			System.out.println("\n--- Connection stats with 2 active sessions ---");
			printStats(stats);

		} catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			e.printStackTrace();
		} finally {
			if (session1 != null) {
				session1.closeSession();
			}
			if (session2 != null) {
				session2.closeSession();
			}
		}
	}

	/**
	 * Prints available and busy connection statistics retrieved from
	 * {@link NAEConnectionStats}.  Each call aggregates data across all
	 * currently active {@link NAESession} instances.
	 *
	 * @param stats the {@link NAEConnectionStats} instance to query
	 * @throws Exception if the underlying stats retrieval fails
	 */
	private static void printStats(NAEConnectionStats stats) throws Exception {
		// Retrieve available (idle) connection statistics
		NAEConnectionInfo available = stats.getTotalAvailableConnections();
		System.out.println("Total available connections  : " + available.getTotal());
		System.out.println("Available connections per CTM: " + available.getPerCTMConnections());

		// Retrieve busy (in-use) connection statistics
		NAEConnectionInfo busy = stats.getTotalBusyConnections();
		System.out.println("Total busy connections       : " + busy.getTotal());
		System.out.println("Busy connections per CTM     : " + busy.getPerCTMConnections());
	}
}
