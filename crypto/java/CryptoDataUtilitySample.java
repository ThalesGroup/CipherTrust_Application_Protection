/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Provider;
import java.security.Security;
import java.util.Random;

import com.gemalto.ps.keysecure.crypto.CryptoDataUtility;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAESession;

/**
 ** This class will do a sample test on the encryption utility.
**/
public class CryptoDataUtilitySample {

	public static void main(String[] args) throws Exception {
		if (args.length != 5) {
			System.out.println("Usage: java CryptoDataUtilitySample <username>" + " <password>" + " <keyname>" + "<transformation>" + "<text>");
			System.exit(-1);
		}
		
		String userName = args[0];
		String password = args[1];
		String keyName = args[2];
		String transformation = args[3];
		String text = args[4];		
		byte[] plaintext = text.getBytes("UTF-8");
		
		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());
		
		NAESession session = NAESession.getSession(userName, password.toCharArray()); // change as needed

		// this constructor defaults to using SecureRandom for IV generation which is slow but more secure
		CryptoDataUtility utility = new CryptoDataUtility(session); 
		
		// method will generate a random IV for you
		byte[] ciphertext = utility.encrypt(plaintext, keyName, transformation);
		
		System.out.println("Encrypted: " + new String(ciphertext, "UTF-8"));
		
		byte[] decrypted = utility.decrypt(ciphertext);
		
		System.out.println("Decrypted: " + new String(decrypted, "UTF-8"));
		
			
	}

}
