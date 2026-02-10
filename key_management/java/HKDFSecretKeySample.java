/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Provider;
import java.security.Security;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.Mac;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.internal.enums.DerivationAlgo;
import com.ingrian.security.nae.HKDFParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.MACValue;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to create AES and HmacSHA256 key by key derivation function (KDF) based on a hash-based message 
 * authentication code (HMAC) using a Master Key present on Key Manager. It illustrates that two keys created using HKDF 
 * have same key data using Encryption/Decryption and MAC/MACVerfiy operations. 
 * 
 */
public class HKDFSecretKeySample {
	public static void main(String[] args) throws Exception {
		
		if (args.length != 7) {
			System.err.println("Usage: java HKDFSecretKeySample user password masterKeyName aesKeyName_1 aesKeyName_2 hmacKeyName_1 hmacKeyName_2 ");
			System.exit(-1);
			/*
			 * Usage description: 
			 * masterKeyName: Master key to create the AES and Hmac keys.
			 * aesKeyName_1 and aesKeyName_2: AES key names to be created. These are used to determine that their key data is same 
			 * using Encryption/Decryption operation.  
			 * hmacKeyName_1 and hmacKeyName_2: Hmac key names to be created. These are used to determine that their key data is same
			 * using MAC/MACVerify operation. 
			 * 
			 */
		}
		
		String username = args[0];
		String password = args[1];
		String masterKeyName = args[2];
		String aesKeyName_1 =args[3];
		String aesKeyName_2 =args[4];	
		String hmacKeyName_1 =args[5];
		String hmacKeyName_2 =args[6];
		
		String dataToMac = "2D2D2D2D2D424547494E2050455253495354454E54204346EB17960";
		
		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());

		NAESession session = null;

		try {
	 		//Creates NAE Session: pass in NAE user name and password
			session = NAESession.getSession(username, password.toCharArray());
			byte[] salt = "010203".getBytes();
			byte[] info = "010203".getBytes();
			int size = 256;
			
			//Creates HKDFParameterSpec for AES key which is deletable and exportable using a master key that is available on Key Manager
			HKDFParameterSpec aesSpec = new HKDFParameterSpec(aesKeyName_1, size, masterKeyName, salt, info, session,
					DerivationAlgo.SHA256);
			
			KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
			
			//Initializes key generator with parameter spec to generate the AES key
			kg.init(aesSpec);
			
			//Creates AES Key on Key Manager
			NAEKey nae_key_aes_1 = (NAEKey) kg.generateKey();
			
			System.out.println("AES Key: " + aesKeyName_1 + " generated Successfully");
			
		    //Creates HKDFParameterSpec for AES key which is deletable and exportable using a master key that is available on Key Manager
			HKDFParameterSpec aesSpec_2 = new HKDFParameterSpec(aesKeyName_2, size, masterKeyName, salt, info, session,
					DerivationAlgo.SHA256);
			
			//Initializes key generator with parameter spec to generate the AES key
			kg.init(aesSpec_2);
			
			//Creates AES Key on Key Manager
			NAEKey nae_key_aes_2 = (NAEKey) kg.generateKey();
			
			System.out.println("AES Key: " + aesKeyName_2 + " generated Successfully");
			
			//Below code illustrates that two keys created using HKDF have same key data using Encryption/Decryption operation

			String dataToEncrypt = "2D2D2D2D2D424547494E2050455253495354454E54204346EB17960";
			
            //Note: HKDF generates same key data on Key Manager but they have different default IV
            //That is why we are passing the external iv when using AES in CBC mode
		    byte[] iv = "1234567812345678".getBytes();
		  
		    IvParameterSpec ivSpec = new IvParameterSpec(iv);
			
		    //Get a cipher
		    Cipher encryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
		    
		    //Initialize cipher to encrypt
		    encryptCipher.init(Cipher.ENCRYPT_MODE, nae_key_aes_1, ivSpec);
		    
		    //Encrypt data
		    byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());
		    
		    //Get a cipher for decryption
		    Cipher decryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");

		    //To decrypt data, initialize cipher to decrypt
		    decryptCipher.init(Cipher.DECRYPT_MODE, nae_key_aes_2, ivSpec);
		   
		    //Decrypt data
		    byte[] newbuf = decryptCipher.doFinal(outbuf);
		    
		    if(dataToEncrypt.equals(new String(newbuf))) {
		    	System.out.println("AES keys generated have same key data.");	
		    } else {
		    	System.out.println("AES keys generated doesn't have same key data, Hence deleting both keys from Key Manager.");
		    	nae_key_aes_1.delete();  
		    	nae_key_aes_2.delete();
		    }
		    
		    //Below code illustrates that two keys created using HKDF have same key data using MAC/MACVerify operation
			//Creates HKDFParameterSpec for HmacSHA256 key which is deletable and exportable using a master key that is available on Key Manager
			HKDFParameterSpec hamcSpec_1 = new HKDFParameterSpec(hmacKeyName_1, size, masterKeyName, salt, info, session,
					DerivationAlgo.SHA256);
			
			KeyGenerator kg1 = KeyGenerator.getInstance("HmacSHA256", "IngrianProvider");
			
			//Initializes key generator with parameter spec to generate the HmacSHA256 key
			kg1.init(hamcSpec_1);
			
			//Creates HmacSHA256 key on Key Manager
			NAEKey nae_key_hmac_1 = (NAEKey) kg1.generateKey();
			
			System.out.println("Hmac Key: " + hmacKeyName_1 + " generated Successfully");
			
			//Creates HKDFParameterSpec for HmacSHA256 key which is deletable and exportable using a master key that is available on Key Manager
			HKDFParameterSpec hamcSpec_2 = new HKDFParameterSpec(hmacKeyName_2, size, masterKeyName, salt, info, session,
					DerivationAlgo.SHA256);
			
			//Initializes key generator with parameter spec to generate the HmacSHA256 key
			kg1.init(hamcSpec_2);
			
			//To illustrate two key bytes generated by HKDF are same
			//Creates HmacSHA256 key on Key Manager
			NAEKey nae_key_hmac_2 = (NAEKey) kg1.generateKey();
			
			System.out.println("Hmac Key: " + hmacKeyName_2 + " generated Successfully");
			
			//Creates MAC instance to get the message authentication code using first key
		    Mac mac = Mac.getInstance("HmacSHA256", "IngrianProvider");
		    mac.init(nae_key_hmac_1);
		    byte[] macValue = mac.doFinal(dataToMac.getBytes());

		    //Creates MAC instance to verify the message authentication code using second key
		    Mac macV = Mac.getInstance("HmacSHA256Verify", "IngrianProvider");
		    macV.init(nae_key_hmac_2, new MACValue(macValue));
		    byte[] result = macV.doFinal(dataToMac.getBytes());
		    
		    //Check verification result 
		    if (result.length != 1 || result[0] != 1) {
			System.out.println("HMAC256 keys generated doesn't have same key data, Hence deleting both keys from Key Manager.");
			nae_key_hmac_1.delete();
			nae_key_hmac_2.delete();
		    } else {
			System.out.println("HMAC256 Keys generated have same key data.");
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