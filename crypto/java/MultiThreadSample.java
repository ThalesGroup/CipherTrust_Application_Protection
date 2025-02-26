/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;
import javax.crypto.SecretKey;
import javax.crypto.Cipher;
import java.security.SecureRandom;
import javax.crypto.spec.IvParameterSpec;

// CADP for JAVA specific classes.
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
/**
 * This sample shows how to use multiple threads that share
 * the same session using CADP for JAVA.
 */

public class MultiThreadSample extends Thread{ 

    // key to encrypt data
    private SecretKey _key = null;
    // data to encrypt
    byte[] data = "dataToEncrypt".getBytes();

    public static void main( String[] args ) throws Exception 
    {
	if (args.length != 3)
        {
            System.err.println("Usage: java MultiThreadSample user password keyname");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];

	// this sample will create 5 threads
	int threadCount = 5;

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (int i = 0; i < providers.length; i++)
	    System.out.println(providers[i].getInfo());

	MultiThreadSample[] list = new MultiThreadSample[threadCount];
	NAESession session =null;
	try { 
	    // create NAE Session: pass in Key Manager user name and password
	    session = NAESession.getSession(username, password.toCharArray());

	    // get the key
	    SecretKey key = NAEKey.getSecretKey(keyName, session);

	    for (int i=0; i<threadCount; i++)
	    {
		list[i] = new MultiThreadSample(key);
	    }

	    for (int i=0; i<threadCount; i++)
	    {
        	list[i].start();
    	    } 

	    // wait for all threads to finish before closing sesson.
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


    public MultiThreadSample(SecretKey key)
    {
        _key = key;
    }

    public void run()
    {
      try
      {
	   System.out.println("[" + Thread.currentThread().getName() + "] starting sample.");
	  // get IV
	  SecureRandom rng = 
	      SecureRandom.getInstance("IngrianRNG", "IngrianProvider");
	  byte[] iv = new byte[16];
	  rng.nextBytes(iv);
	  IvParameterSpec ivSpec = new IvParameterSpec(iv);
	  NAECipher cipher = NAECipher.getNAECipherInstance("AES/CBC/PKCS5Padding", "IngrianProvider");   
	  cipher.init(Cipher.ENCRYPT_MODE, _key, ivSpec);
	  
	  int inputSize = data.length;
	  int outputSize = cipher.getOutputSize(inputSize);
	  byte[] outbuf = new byte[outputSize];
	  cipher.setMessage("Thread " + Thread.currentThread().getName());
	  int numBytes = cipher.doFinal(data, 0, inputSize, outbuf);
      } catch (Exception e) {
	  System.out.println("Got exception: " + e);
	  e.printStackTrace();
      }
    }
}
