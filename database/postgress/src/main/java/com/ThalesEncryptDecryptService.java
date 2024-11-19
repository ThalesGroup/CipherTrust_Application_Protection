import java.io.InputStream;
import java.security.Provider;
import java.security.Security;
import java.util.Properties;

import javax.crypto.Cipher;

import com.ingrian.security.nae.FPECharset;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;


public class ThalesEncryptDecryptService {

	private static final IngrianProvider provider;
	private static Properties properties;

	static {
		try (InputStream input = ThalesEncryptDecryptService.class.getClassLoader()
				.getResourceAsStream("application.properties")) {
			properties = new Properties();
			if (input == null) {
				throw new RuntimeException("Unable to find application.properties");
			}
			properties.load(input);
		} catch (Exception ex) {
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	static {
		try {
			// Load the properties file as an InputStream
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			// InputStream inputStream =
			// ThalesDataBricksCADPFPE.class.getClassLoader().getResourceAsStream("CADP_for_JAVA.properties");
			InputStream inputStream = ThalesEncryptDecryptService.class.getClassLoader()
					.getResourceAsStream("CADP_for_JAVA.properties");
			if (inputStream == null) {
				throw new RuntimeException("Failed to find CADP_for_JAVA.properties file.");
			}

			// Initialize the IngrianProvider using the static context
			provider = new IngrianProvider.Builder().addConfigFileInputStream(inputStream).build();
		} catch (Exception e) {
			e.printStackTrace();
			throw new RuntimeException("Failed to initialize IngrianProvider.", e);
		}
	}
	
	
	
	public static String callDecryptApi(String encryptedData) throws Exception {

		//System.out.println("Data to decrypt \"" + encryptedData + "\"");
		NAESession session = null;
		String username = properties.getProperty("app.cmuser");
		String password =  properties.getProperty("app.cmpwd");
		String keyName = properties.getProperty("app.keyname");

		String tweakAlgo = null;
		String tweakData = null;
		String encdata = encryptedData;

		try {
			// create NAE Session: pass in NAE user name and password
			session = NAESession.getSession(username, password.toCharArray());

			// Get SecretKey (just a handle to it, key data does not leave the server
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			String algorithm = "FPE/FF1/CARD62";
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			// get a cipher
			Cipher thalesCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// initialize cipher to decrypt.
			thalesCipher.init(Cipher.DECRYPT_MODE, key, param);

			// decrypt data
			byte[] outbuf = thalesCipher.doFinal(encryptedData.getBytes());

			encdata = new String(outbuf);

			// close the session
			session.closeSession();
		} catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			if (!e.getMessage().startsWith("User is not authorized to perform this operation at this time for") && !e.getMessage().contains("1401"))
				throw e;

			
		} finally {
			if (session != null) {
				session.closeSession();
			}
		}
		return new StringBuilder(encdata).toString(); // Mock decryption (reversing string)
		// return new StringBuilder(encdata).reverse().toString(); // Mock decryption (reversing string)
	}
	
    public static String callEncrypptApi(String sensitive) throws Exception
    {
    	

		//System.out.println("Data to encrypt \"" + sensitive + "\"");
		NAESession session = null;
		String username = properties.getProperty("app.cmuser");
		String password =  properties.getProperty("app.cmpwd");
		String keyName = properties.getProperty("app.keyname");

		String tweakAlgo = null;
		String tweakData = null;
		String encdata = null;

		try {
			// create NAE Session: pass in NAE user name and password
			session = NAESession.getSession(username, password.toCharArray());

			// Get SecretKey (just a handle to it, key data does not leave the server
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			String algorithm = "FPE/FF1/CARD62";
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			// get a cipher
			Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			// initialize cipher to encrypt.
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);

			// encrypt data
			byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());

			encdata = new String(outbuf);

			// close the session
			session.closeSession();
		} catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			if (!e.getMessage().startsWith("User is not authorized to perform this operation at this time for") && !e.getMessage().contains("1401"))
				throw e;

		} finally {
			if (session != null) {
				session.closeSession();
			}
		}
    	
		return encdata;
    	
    }
    
}
