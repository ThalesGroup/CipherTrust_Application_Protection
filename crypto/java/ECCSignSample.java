/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import java.security.Provider;
import java.security.Security;
import java.security.Signature;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample demonstrates how to perform Sign and SignVerify operations using ECC key.
 *
 */
public class ECCSignSample {
	public static void main(String[] args) throws Exception {

		if (args.length != 3) {
			System.err.println("Usage: java ECCSignSample user password keyname");
			System.exit(-1);
		}
		
		String userName = args[0];
		String password = args[1];
		String keyName =  args[2];
		
		//Data to sign
		String dataForSignature = "testdata for ECC Sign Test";
		String signAlgo = "SHA256withECDSA";
		
		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());

		NAESession session = null;
		try {
			
			//Creates NAESession: pass in NAE user and password
			session = NAESession.getSession(userName, password.toCharArray());
			
			//Creates a signature object for sign operation
			Signature sig = Signature.getInstance(signAlgo, "IngrianProvider");
			
			// Sign data
			//Creates NAEPrivateKey object
			NAEPrivateKey privKey = NAEKey.getPrivateKey(keyName, session);
			
			//Initializes the signature object for signing 
			sig.initSign(privKey);
			sig.update(dataForSignature.getBytes());
			byte[] signature = sig.sign();

			System.out.println("ECCKey Sign Operation: SUCCESS");
			
			//Creates a signature object for signVerify operation
			Signature sigVer = Signature.getInstance(signAlgo, "IngrianProvider");
			
             //Verify signature
		    //Get NAEPublicKey
			NAEPublicKey pubKey = NAEKey.getPublicKey(keyName, session);
			
			//Initializes Signature object for signature verification 
			sigVer.initVerify(pubKey);
			sigVer.update(dataForSignature.getBytes());

			if (!sigVer.verify(signature)) {
				System.out.println("Signature Verification: FAILED");
			} else {
				System.out.println("Signature Verification: SUCCESS");
			}

		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		} finally {
			if (session != null)
				//Close NAESession
				session.closeSession();
		}
	}

}
