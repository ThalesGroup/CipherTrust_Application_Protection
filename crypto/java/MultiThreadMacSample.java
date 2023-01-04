/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;

import java.security.SecureRandom;

// CADP for JAVA specific classes.
import com.ingrian.security.nae.MACValue;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEMac;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.IngrianProvider;
/**
 * This Mac sample shows how to use multiple threads that share
 * the same session using CADP for JAVA.
 */

public class MultiThreadMacSample extends Thread{ 

	// key to Mac data
	private NAEKey _key = null;

	public static void main( String[] args ) throws Exception 
	{
		if (args.length != 3)
		{
			System.err.println("Usage: java MultiThreadMacSample user password mackeyname");
			System.exit(-1);
		} 
		String username  	= args[0];
		String password  	= args[1];
		String mackeyName   = args[2];

		// this sample will create 5 threads
		int threadCount = 5;

		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		MultiThreadMacSample[] list = new MultiThreadMacSample[threadCount];
		NAESession session = null;
		try { 
			// create NAE Session: pass in Key Manager user name and password
			session = NAESession.getSession(username, password.toCharArray());

			// get the key
			NAEKey key = NAEKey.getSecretKey(mackeyName, session);

			for (int i=0; i<threadCount; i++)
			{
				list[i]  = new MultiThreadMacSample(key);
			}

			for (int i=0; i<threadCount; i++)
			{
				list[i].start();
			} 

			// wait for all threads to finish before closing session.
			for (int i=0; i<threadCount; i++)
			{  
				list[i].join();
			}

			session.closeSession();

		} catch (Exception e) {
			System.out.println("Got exception: " + e);
			e.printStackTrace();
		} finally{
			if(session!=null)
				session.closeSession();
		}
	}

	public MultiThreadMacSample(NAEKey key)
	{
		_key = key;
	}

	public void run()
	{
		try
		{
			System.out.println("[" + Thread.currentThread().getName() + "] starting sample.");

			// create and initialize mac object
			NAEMac mac = NAEMac.getNAEMacInstance("HmacSHA512", "IngrianProvider");
			mac.init(_key);

			// Generate random data to mac
			SecureRandom rng = SecureRandom.getInstance("IngrianRNG", "IngrianProvider");
			byte[] randomBytes = new byte[16];
			rng.nextBytes(randomBytes);
			String dataToMac = new String(randomBytes);

			// perform the mac operation and send message string to Key Manager
			mac.setMessage("client is creating mac: " + Thread.currentThread().getName()); 
			byte[] macValue = mac.doFinal(dataToMac.getBytes());

			// create and initialize mac object for verification
			NAEMac macV = NAEMac.getNAEMacInstance("HmacSHA512Verify", "IngrianProvider");
			macV.init(_key, new MACValue (macValue));

			// perform the macV operation and send message string to Key Manager
			macV.setMessage("client is verifying the mac: " + Thread.currentThread().getName());
			byte[] result = macV.doFinal(dataToMac.getBytes());

			// check verification result 
			if (result.length != 1 || result[0] != 1) {
				System.out.println(Thread.currentThread().getName() + " Invalid MAC.");
			} else {
				System.out.println(Thread.currentThread().getName() + " MAC Verified OK.");
			}

		} catch (Exception e) {
			System.out.println("Got exception: " + e);
			e.printStackTrace();
                        throw e;
		}
	}
}
