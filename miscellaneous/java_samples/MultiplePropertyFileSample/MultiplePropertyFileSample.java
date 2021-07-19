/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.KeyGenerator;
import javax.crypto.NoSuchPaddingException;

import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAESecretKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.NAESessionInterface;
import com.ingrian.security.nae.SessionLevelConfig;
/**
 *<b>Description</b> : This sample provide overview of multiple property file support on session level.In this sample 
 * there are two different session where one session pointing to different properties file and another is 
 * using global property file.
 * </br>
 * Local session is creating new key and export that key to global session using import and export apis. To validate
 * sharing between Key Manager one sample data was encrypted with local session key and decrypted by global session key.
 * 
 * @version 8.4
 */
public class MultiplePropertyFileSample {
	
	public static void main(String[] args) {
		if (args.length != 6)
	        {
	            System.err.println("Usage: java MultiplePropertyFileSample local_config_user local_config_password "
	            		+ "local_propertyfile_path global_config_user global_config_password keyname");
	            System.exit(-1);
		} 
		NAESession localsession = null;
		NAESession globalsession =null;
		NAESecretKey localsessionKey =null;
		NAEKey globalsessionKey =null;
		String data="Test Data";
		try {
			localsession = NAESession.getSession(args[0],args[1].toCharArray(), new SessionLevelConfig(args[2]));
			globalsession = NAESession.getSession(args[3],args[4].toCharArray());
			NAEParameterSpec spec = new NAEParameterSpec(args[5], true, true,false, 192, null, localsession);
			localsessionKey = generateKey(spec);
			boolean isExported = exportKeyToGlobalSession(globalsession,	localsessionKey);
			if (isExported) {
				byte[] encrytedText = encryptWithLocalConfig(data,localsessionKey);
				globalsessionKey = NAEKey.getSecretKey(localsessionKey.getName(), globalsession);
				byte[] decryptText = decryptWithGLobalConfig(encrytedText,globalsessionKey);
				if (data.equals(new String(decryptText))) {
					System.out.println("Key  is exported successfully to global Key Manager.");
				} else {
					System.out.println("Key is not exported successfully to global Key Manager.");
				}
			} else {
				System.out.println("Key is not exported successfully to global Key Manager.");
			}
			
		} catch (Exception e) {
			e.printStackTrace();
		}finally{
			if(localsessionKey!=null)
				localsessionKey.delete();
			if(globalsessionKey!=null)
				globalsessionKey.delete();
		}

	}

	static boolean exportKeyToGlobalSession(NAESessionInterface globalsessionforEn,NAEKey key) {
		if (key.isExportable()) {
			byte[] rawKey = key.export();
			NAEKey.importKey(rawKey, key.getAlgorithm(), new NAEParameterSpec(key.getName(), true, true,false, 192,null, globalsessionforEn));
			return true;
		}
		return false;
	}
	
	static NAESecretKey generateKey(NAEParameterSpec spec) throws NoSuchAlgorithmException, NoSuchProviderException, InvalidAlgorithmParameterException{
		KeyGenerator keygen = KeyGenerator.getInstance("AES", "IngrianProvider");
	    keygen.init(spec);
	   return  (NAESecretKey) keygen.generateKey();
	}
	
	static byte[] encryptWithLocalConfig(String data,NAEKey key) throws NoSuchAlgorithmException, NoSuchProviderException, 
	InvalidAlgorithmParameterException, IllegalBlockSizeException, BadPaddingException, InvalidKeyException, NoSuchPaddingException{
		Cipher cipherEncryptLocalSession = Cipher.getInstance("AES/ECB/PKCS5Padding","IngrianProvider");
		cipherEncryptLocalSession.init(Cipher.ENCRYPT_MODE, key);
		return cipherEncryptLocalSession.doFinal(data.getBytes());
	}
	
	static byte[] decryptWithGLobalConfig(byte[] encryptedText,NAEKey key) throws NoSuchAlgorithmException, 
	NoSuchProviderException, InvalidAlgorithmParameterException, IllegalBlockSizeException, BadPaddingException, InvalidKeyException, NoSuchPaddingException{
		Cipher cipherEncryptLocalSession = Cipher.getInstance("AES/ECB/PKCS5Padding","IngrianProvider");
		cipherEncryptLocalSession.init(Cipher.DECRYPT_MODE, key);
		return cipherEncryptLocalSession.doFinal(encryptedText);
	}

}
