/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.IOException;
import java.io.RandomAccessFile;
import java.security.Security;
import java.security.spec.AlgorithmParameterSpec;
import java.util.HashMap;
import java.util.Map;

import javax.crypto.Cipher;

import com.ingrian.security.nae.AbstractNAECipher;
import com.ingrian.security.nae.GCMParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This samples show how to perform bulk operation using different algorithms on
 * different type of data and algorithm data.
 * 
 * Note: For AES-GCM algorithm, same combination of nonce (IV) and key must not be reused 
 * during encryption/decryption operations.	 
 */
public class BulkOperationSample {

	private static byte[][] data;
	private static AlgorithmParameterSpec[] spec;

	static {
		Security.addProvider(new IngrianProvider());
	}

	public static void main(String[] args) {

		if (args.length != 4) {
			System.out.println("Usage: java BulkOperationSample <username>"
					+ " <password>" + " <keyname> <datafile>");
			System.exit(-1);
		}

		String userName = args[0];
		String password = args[1];
		String keyName = args[2];
		String fileName = args[3];

		NAESession session = null;

		try {
			// Getting session and key
			session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			// Getting instance for the bulk operation. Should be called
			// whenever bulk operation needs to be performed.
			AbstractNAECipher encryptCipher = NAECipher.getInstanceForBulkData(
					"AES/GCM/NoPadding", "IngrianProvider");

			// read the contents from the file and write into the arrays
			readContentsFromFileAndWriteToArrays(fileName);

			// initializing the cipher for encrypt operation
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, spec[0]);

			// Map to store exceptions while encryption
			Map<Integer, String> encryptedErrorMap = new HashMap<Integer, String>();

			// performing bulk operation
			byte[][] encryptedData = encryptCipher.doFinalBulk(data, spec,
					encryptedErrorMap);

			// displaying the encrypted data
			displayData(encryptedData, "Encrypted data");
			
			//cipher instance for decryption
			AbstractNAECipher decryptCipher = NAECipher.getInstanceForBulkData(
					"AES/GCM/NoPadding", "IngrianProvider");

			// initializing the cipher for decrypt operation
			decryptCipher.init(Cipher.DECRYPT_MODE, key, spec[0]);

			// Map to store exceptions while decryption
			Map<Integer, String> decryptedErrorMap = new HashMap<Integer, String>();

			// performing bulk operation
			byte[][] decryptedData = decryptCipher.doFinalBulk(encryptedData, spec,
					decryptedErrorMap);

			// displaying the decrypted data
			displayData(decryptedData, "Decrypted Data ");
		} catch (Exception e) {
		       e.printStackTrace();
                       System.out.println("The Cause is " + e.getMessage() + ".");
	               throw e;
		} finally{
			// releasing session
			if(session!=null) {
				session.closeSession();
			}
		}

		
	}

	private static void displayData(byte[][] input, String message) {
		for (int i = 0; i < data.length; i++) {
			System.out.println(message + i + ": "
					+ (input[i] == null ? "null" : new String(input[i])));
		}
	}

	/**
	 * This will create the arrays required of size equals to the number of data
	 * into the file.
	 */
	private static void readContentsFromFileAndWriteToArrays(String fileName)
			throws IOException {
		RandomAccessFile file = new RandomAccessFile(fileName, "r");
		int numberOfLines = numberOfLines(file);

		spec = new GCMParameterSpec[numberOfLines];
		data = new byte[numberOfLines][];

		WriteFileContentIntoArrays(file, data, spec);
		file.close();
	}

	/**
	 * This will write the respective data into the array objects.
	 */
	private static void WriteFileContentIntoArrays(RandomAccessFile file,
			byte[][] data, AlgorithmParameterSpec[] spec)
					throws NumberFormatException, IOException {

		int dataIndex = 0;
		int specIndex = 0;
		String line = null;

		while ((line = file.readLine()) != null) {
			if (line.length() == 0) {
				break;
			}
			String[] words = line.split(",");

			int tagLength = Integer.parseInt(words[1].trim());
			data[dataIndex++] = words[0].trim().getBytes();

			spec[specIndex++] = new GCMParameterSpec(tagLength,
					IngrianProvider.hex2ByteArray(words[2].trim()), words[3]
							.trim().getBytes());
		}
	}

	/**
	 * This will find the number of lines in the file and set the file pointer
	 * again to first line when total number lines read.
	 * 
	 * @param file
	 *            file in which data stored
	 * @return number of lines
	 * @throws IOException
	 *             when problem with file I/O
	 */
	private static int numberOfLines(RandomAccessFile file) throws IOException {
		int numberOfLines = 0;
		while (file.readLine() != null) {
			numberOfLines++;
		}
		file.seek(0);
		return numberOfLines;
	}
}
