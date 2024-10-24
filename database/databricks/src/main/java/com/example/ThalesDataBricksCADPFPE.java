package example;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.security.nae.FPECharset;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import java.io.InputStream;
import java.math.BigInteger;
import java.util.Properties;

public class ThalesDataBricksCADPFPE {
//  @Override
	/*
	 * This test app to test the logic for a Databricks User Defined Function(UDF). It is an example of how to use
	 * Thales Cipher Trust Application Data Protection (CADP) to protect sensitive data in a column. This example uses
	 * Format Preserve Encryption (FPE) to maintain the original format of the data so applications or business
	 * intelligence tools do not have to change in order to use these columns.
	 * 
	 * Note: This source code is only to be used for testing and proof of concepts. Not production ready code. Was not
	 * tested for all possible data sizes and combinations of encryption algorithms and IV, etc. Was tested with CM 2.14
	 * & CADP 8.16 For more information on CADP see link below.
	 * https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
	 * 
	 * @author mwarner
	 * 
	 */

	private static final IngrianProvider provider;
	private static Properties properties;

	static {
		try (InputStream input = ThalesDataBricksCADPFPE.class.getClassLoader()
				.getResourceAsStream("udfConfig.properties")) {
			properties = new Properties();
			if (input == null) {
				throw new RuntimeException("Unable to find udfConfig.properties");
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
					"CADP_for_JAVA_Public.properties");
			// InputStream inputStream =
			// ThalesDataBricksCADPFPE.class.getClassLoader().getResourceAsStream("CADP_for_JAVA.properties");
			InputStream inputStream = ThalesDataBricksCADPFPE.class.getClassLoader()
					.getResourceAsStream("CADP_for_JAVA_Public.properties");
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

	public static void main(String[] args) throws Exception

	{
		String request_decrypt_char = "thisis a test this is only a test";
		// String request_decrypt_nbr = "4356346534533";
		// 8310258662548
		String request_decrypt_nbr = "8310258662548";
		String request = "554";
		String response = null;
		System.out.println("input data = " + request);
		String mode = "encrypt";
		String datatype = "nbr";

		System.out.println("results = " + thales_cadp_udf(request, mode, datatype));
	}

	public static String thales_cadp_udf(String databricks_inputdata, String mode, String datatype) throws Exception {

		if (databricks_inputdata != null && !databricks_inputdata.isEmpty()) {
			if (databricks_inputdata.length() < 2)
				return databricks_inputdata;

			if (!datatype.equalsIgnoreCase("char")) {

				BigInteger lowerBound = BigInteger.valueOf(-9);
				BigInteger upperBound = BigInteger.valueOf(-1);

				try {
					// Convert the string to an integer
					BigInteger number = new BigInteger(databricks_inputdata);

					// Check if the number is between -1 and -9
					if (number.compareTo(lowerBound) >= 0 && number.compareTo(upperBound) <= 0) {
						System.out.println("The input is a negative number between -1 and -9.");
						return databricks_inputdata;
					}
				} catch (NumberFormatException e) {
					System.out.println("The input is not a valid number.");
					return databricks_inputdata;
				}
			}

		} else {
			System.out.println("The input is either null or empty.");
			return databricks_inputdata;
		}

		String keyName = "testfaas";
		// String userName = System.getenv("CMUSER");
		String userName = properties.getProperty("CMUSER");
		if (userName == null) {
			throw new IllegalArgumentException("No CMUSER found for UDF: ");
		}
		// String password = System.getenv("CMPWD");
		String password = properties.getProperty("CMPWD");
		String returnciphertextforuserwithnokeyaccess = properties
				.getProperty("returnciphertextforuserwithnokeyaccess");
		// yes,no
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");

		NAESession session = null;
		String formattedString = null;

		try {

			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			IvParameterSpec ivSpec = null;

			int cipherType = 0;
			String algorithm = "FPE/FF1/CARD62";

			String tweakAlgo = null;
			String tweakData = null;
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();

			if (mode.equals("encrypt"))
				cipherType = Cipher.ENCRYPT_MODE;
			else
				cipherType = Cipher.DECRYPT_MODE;

			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else {
				algorithm = "FPE/FF1/CARD10";
				// Can define own charset.
				// FPECharset charset = FPECharset.getUnicodeRangeCharset("31-39");
				// param = new
				// FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).set_charset(tweakData)
				// .build();
			}

			ivSpec = param;
			Cipher thalesCipher = Cipher.getInstance(algorithm, "IngrianProvider");
			thalesCipher.init(cipherType, key, ivSpec);

			byte[] outbuf;
			try {
				outbuf = thalesCipher.doFinal(databricks_inputdata.getBytes());
				formattedString = new String(outbuf);
			} catch (Exception e) {
				String errormsgkeyaccess = new String("User is not authorized to perform this operation");

				String errormsg = e.getMessage();
				if (errormsg.startsWith(errormsgkeyaccess)) {
					if (returnciphertextbool)
						formattedString = databricks_inputdata;
					else
						formattedString = null;
				}
			}

		} catch (Exception e) {

			System.out.println("in exception with " + e.getMessage());

			if (returnciphertextbool) {
				if (e.getMessage().contains("1401")
						|| (e.getMessage().contains("1001") || (e.getMessage().contains("1002")))) {
					if (databricks_inputdata != null) {
						formattedString = databricks_inputdata;
					}

				} else {
					e.printStackTrace(System.out);

				}
			} else {
				e.printStackTrace(System.out);

			}
		} finally

		{
			if (session != null) {
				session.closeSession();
			}
		}
		return formattedString;

	}
}