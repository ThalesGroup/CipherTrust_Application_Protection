/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.Key;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

import javax.crypto.Cipher;
import javax.crypto.CipherInputStream;
import javax.crypto.KeyGenerator;
import javax.crypto.Mac;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.security.nae.GCMParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.MACValue;
import com.ingrian.security.nae.NAEAESGCMCipher;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEIvAndTweakDataParameter;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAESession;


public final class CryptoTool {

	// hashmap to keep track of operations
    private final static Map<String,Integer> knownOperations = new HashMap<String,Integer>();
    
    // operation names
    private final static String ENCRYPT = "ENCRYPT";
    private final static String DECRYPT = "DECRYPT";
    private final static String MAC = "MAC";
    private final static String MACV = "MACV";
    private final static String SIGN = "SIGN";
    private final static String SIGNV = "SIGNV";
    private final static String GENERATE = "GENERATE";
    private final static String DELETE = "DELETE";
    private final static String IMPORT = "IMPORT";
    private final static String EXPORT = "EXPORT";
    private final static String LIST = "LIST";
   

    // operation codes
    private final static int ENCRYPTINT = 0;
    private final static int DECRYPTINT = 1;
    private final static int MACINT = 2;
    private final static int MACVINT = 3;
    private final static int SIGNINT = 4;
    private final static int SIGNVINT = 5;
    private final static int GENERATEINT = 6;
    private final static int DELETEINT = 7;
    private final static int IMPORTINT = 8;
    private final static int EXPORTINT = 9;
    private final static int LISTINT = 10;
    

    // parameter names
    private final static String KEY = "-key";
    private final static String ALGORITHM = "-alg";
    private final static String AUTH = "-auth";
    private final static String IV = "-iv";
    private final static String MACVALUE = "-mac";
    private final static String MACFILE = "-macfile";
    private final static String SIGNATURE = "-sig";
    private final static String SIGFILE = "-sigfile";
    private final static String INFILE = "-in";
    private final static String OUTFILE = "-out";
    private final static String EXPORTABLE = "-exportable";
    private final static String DELETABLE = "-deletable";
    private final static String KEYSIZE = "-keysize";
    private final static String IP = "-ip";
    private final static String PORT = "-port";
    private final static String PROTOCOL =  "-protocol";
    private final static String HELP = "-help";
    private final static String TWEAKDATA = "-tweakdata";
    private final static String TWEAKALGO = "-tweakalgo";
    private final static String AAD = "-aad";
    private final static String AUTHTAGLENGTH = "-authtaglength";
   
    
    // buffer length
    private final static int BUFFER_LEN = 8192;
    private static final String EMPTYSTRING = "";

    static {
        // build operation tables that maps operation name
        // with operation code
        knownOperations.put(ENCRYPT, new Integer(ENCRYPTINT));
        knownOperations.put(DECRYPT, new Integer(DECRYPTINT));
        knownOperations.put(MAC, new Integer(MACINT));
        knownOperations.put(MACV, new Integer(MACVINT));
        knownOperations.put(SIGN, new Integer(SIGNINT));
        knownOperations.put(SIGNV, new Integer(SIGNVINT));
        knownOperations.put(GENERATE, new Integer(GENERATEINT));
        knownOperations.put(DELETE, new Integer(DELETEINT));
        knownOperations.put(IMPORT, new Integer(IMPORTINT));
        knownOperations.put(EXPORT, new Integer(EXPORTINT));
        knownOperations.put(LIST, new Integer(LISTINT));
        
    }

    /** prints the usage */    
    private static void printUsage() {
        System.err.println("\nUSAGE:");
        System.err.println(
            "\tjava CryptoTool OPERATION options\n ");
        System.err.println("SUPPORTED CRYPTO OPERATIONS:");
        System.err.println("\n\tENCRYPT, DECRYPT, MAC, MACV, SIGN, SIGNV\n");
        System.err.println("SUPPORTED KEY MANAGEMENT OPERATIONS:");
        System.err.println("\n\tGENERATE, DELETE, EXPORT, IMPORT, LIST\n");
               
        System.err.print("SUPPORTED OPTIONS:\n\n");
        System.err.println(AUTH + " username:passwd \n\t username and password for authentication");
        System.err.println(INFILE + " filename \n\t specify a file instead of stdin");
        System.err.println(OUTFILE + " filename \n\t specify a file instead of stdout");
        System.err.println(KEY + " keyname \n\t key name");
        System.err.println(ALGORITHM + " algname \n\t algorithm");
        System.err.println(IV + " value \n\t initialization vector when required (must be hex ASCII encoded)");
        System.err.println(SIGNATURE +
            " value  \n\t provide signature value as an argument to use for verification (must be hex ASCII encoded)");
        System.err.println(SIGFILE +
            " filename  \n\t alternative to -sig; provide signature value in a file");
        System.err.println(MACVALUE +
            " value \n\t provide mac value as an argument to use for verification (must be hex ASCII encoded)");
        System.err.println(MACFILE +
            " filename  \n\t alternative to -mac; provide mac value in a file");
        System.err.println(KEYSIZE + " size \n\t key size to use for key generation");
        System.err.println(EXPORTABLE + " \n\t create exportable key");
        System.err.println(DELETABLE + " \n\t create deletable key");
        System.err.println(IP + " ip \n\t NAE server IP to use  (can be a colon separated list of IP addresses)");
        System.err.println(PORT + " port \n\t NAE server port to use");
        System.err.println(PROTOCOL + " prot \n\t protocol to use (ssl or tcp)");
    	System.err.println(TWEAKALGO + " TweakAlgo \n\t to specify Tweak Algorithm name for FPE encryption");
    	System.err.println(TWEAKDATA + " TweakData \n\t to specify Tweak Data for FPE encryption");
    	System.err.println(AAD + " AAD \n\t to specify AAD for GCM encryption");
    	System.err.println(AUTHTAGLENGTH + " authtaglength \n\t to specify authtaglength for GCM Encryption");
    	
    }
    
    /** A utility function that creates a hashmap from the parameters */    
    private static Map<String,String> buildArguments(String[] args) {
        int i = 1;
        if (args.length == 0) {
            System.err.println("Empty arguments");
            return null;
        }
        Map<String,String> map = new HashMap<String,String>();
        String key = null;
        while (i < args.length) {
            if (key != null) {
                if (args[i].startsWith("-")) {
                    map.put(key, null);
                    key = args[i];
                    i++;
                } else {
                    map.put(key, args[i]);
                    key = null;
                    i++;
                }

            } else {
                if (args[i].startsWith("-")) {
                    key = args[i];
                    i++;
                } else {
                    System.err.println("Invalid argument " + args[i]);
                    return null;
                }
            }
        }
        if (key != null) {
            map.put(key, null);
        }
        return map;
    }
    
    /**
	 * This method is used to get the input stream from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return InputStream
	 */
    private static InputStream getInputStream(Map<String,String> arguments) throws IOException {
        String fileName = (String) arguments.get(INFILE);
        if (fileName != null) {
            return new FileInputStream(fileName);
        } else {
            return System.in;
        }
    }
    
    /**
	 * This method is used to get the output stream from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return OutputStream
	 */   
    private static DataOutputStream getOutputStream(Map<String,String> arguments) throws IOException {
        String fileName = (String) arguments.get(OUTFILE);
        if (fileName != null) {
            return new DataOutputStream(new FileOutputStream(fileName));
        } else {
            return new DataOutputStream(System.out);
        }
    }

    /**
	 * This method is used to get the operation from the map and validate it.
	 * @param arguments map having program options as keys and its values 
	 * @return operation integer
	 */    
    private static int getOperation(String op) {
        Integer operationInt = (Integer) knownOperations.get(op);
       
		if (operationInt == null ) {
            System.err.println("Unknown Operation");
            return -1;
        }
		return operationInt.intValue();
    }
    
    /**
	 * This method is used to get the key name from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return key name
	 */   
    private static String getKeyName(Map<String,String> arguments) {
        String keyName = (String) arguments.get(KEY);
        return keyName;
    }

    /**
	 * This method is used to get the algorithm name from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return algorithm name
	 */    
    private static String getAlgorithmName(Map<String,String> arguments) {
        String algName = (String) arguments.get(ALGORITHM);
        return algName;
    }

    /**
	 * This method is used to get the auth from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return auth
	 */    
    private static String getAuth(Map<String,String> arguments) {
    	String auth = arguments.get(AUTH);
    	return auth;
    }

    /**
	 * This method is used to get the IV from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return IV
	 */   
    private static byte[] getIV(Map<String,String> arguments) {
        String ivString = (String) arguments.get(IV);
        if (ivString == null) {
            return null;
        }
        return hex2ByteArray(ivString);
    }

    /**
	 * This method is used to get the MAC from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return MAC byte array
	 */    
    private static byte[] getMAC(Map<String,String> arguments) throws IOException {
        String macString;
        if (arguments.containsKey(MACFILE)) {
            String macFileName = (String) arguments.get(MACFILE);
            if (macFileName == null) {
                return null;
            } else {
                BufferedReader br = new BufferedReader(new FileReader(
                    macFileName));
                macString = br.readLine();
                br.close();
            }
        } else {
            macString = (String) arguments.get(MACVALUE);
            if (macString == null) {
                return null;
            }
        }
        return hex2ByteArray(macString);
    }

    /**
	 * This method is used to get the Signature from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return Signature byte array
	 */     
    private static byte[] getSignature(Map<String,String> arguments) throws IOException {
        String sigString;
        if (arguments.containsKey(SIGFILE)) {
            String sigFileName = (String) arguments.get(SIGFILE);
            if (sigFileName == null) {
                return null;
            } else {
                BufferedReader br = new BufferedReader(new FileReader(
                    sigFileName));
                sigString = br.readLine();
                br.close();
            }
        } else {
            sigString = (String) arguments.get(SIGNATURE);
            if (sigString == null) {
                return null;
            }
        }
        return hex2ByteArray(sigString);
    }

    /**
	 * This method is used to get the exportable boolean from the map.
	 * @param arguments map having program options as keys and its values 
	 * @return exportable boolean
	 */    
    private static boolean getExportable(Map<String,String> arguments) {
        if (arguments.containsKey(EXPORTABLE))
            return true;
        return false;
    }

    /**
   	 * This method is used to get the deletable boolean from the map.
   	 * @param arguments map having program options as keys and its values 
   	 * @return deletable boolean
   	 */ 
    private static boolean getDeletable(Map<String,String> arguments) {
        if (arguments.containsKey(DELETABLE))
            return true;
        return false;
    }

    /**
   	 * This method is used to get the key size from the map.
   	 * @param arguments map having program options as keys and its values 
   	 * @return key size
   	 */ 
    private static int getKeySize(Map<String,String> arguments) {
        String keySize = (String) arguments.get(KEYSIZE);
        if (keySize == null) {
            return -1;
        }
        return Integer.parseInt(keySize);
    }

    
    /**
   	 * This method is used to get the AAD from the map.
   	 * @param arguments map having program options as keys and its values 
   	 * @return AAD
   	 */
    public static String getAad(Map<String,String> arguments) {
		String aad = (String) arguments.get(AAD);
    	return aad;
	}
    
    /**
   	 * This method is used to get the tweakalgo from the map.
   	 * @param arguments map having program options as keys and its values 
   	 * @return tweakalgo
   	 */
    public static String getTweakalgo(Map<String,String> arguments) {
    	String tweakalgo = (String) arguments.get(TWEAKALGO);
    	return tweakalgo;
	}
    
    /**
   	 * This method is used to get the tweakdata from the map.
   	 * @param arguments map having program options as keys and its values 
   	 * @return tweakdata
   	 */
    public static String getTweakdata(Map<String,String> arguments) {
    	String tweakdata = (String) arguments.get(TWEAKDATA);
		return tweakdata;
	}
    
    /**
   	 * This method is used to get the authtaglength from the map.
   	 * @param arguments map having program options as keys and its values 
   	 * @return authtaglength
   	 */
    public static String getAuthtaglength(Map<String,String> arguments) {
    	String authtaglength = (String)arguments.get(AUTHTAGLENGTH);
        return authtaglength;
	}

    /** Encrypts a string based on the input parameters. The encrypted value
     * is print to the output stream.
     * @param keyName Key name to use
     * @param algName Algorithm name to use
     * @param iv IV to use
     * @param session NAESession
     * @throws Exception
     * @return returns whether the operation was succesful
     */    
    private static boolean doEncrypt(String keyName, String algName,
    		byte[] iv, NAESession session, String outFile) throws Exception {

    	// error checking
    	if (keyName == null) {
    		System.err.println("Missing key name");
    		return false;
    	}
    	if (algName == null) {
    		System.err.println("Missing algorithm name");
    		return false;
    	}
    	if (iv != null && algName.indexOf("CBC") < 0) {
    		System.err.println("IV is not required for this algorithm.");
    		return false;
    	}

    	Key key;
    	if (algName.toUpperCase().startsWith("RSA")) // retrieve RSA public key
    		key = NAEKey.getPublicKey(keyName, session);
    	else // retrieve secret key
    		key = NAEKey.getSecretKey(keyName, session);
    	byte[] buffer = new byte [BUFFER_LEN];

    	// create cipher instance
    	Cipher cipher = Cipher.getInstance(algName, "IngrianProvider");
    	if (iv == null) {
    		cipher.init(Cipher.ENCRYPT_MODE, key);
    	}
    	else
    		cipher.init(Cipher.ENCRYPT_MODE, key, new IvParameterSpec(iv));
    	
    	// use the cipher instance to encrypt the input stream
    	String result = null;
    	
		if (is instanceof FileInputStream) {
			CipherInputStream cis = null;
			FileOutputStream fos = null;
			try{
				cis = new CipherInputStream(is, cipher);
				fos = new FileOutputStream(outFile);
				for (int inlen = 0; (inlen = cis.read(buffer)) != -1;) {
					fos.write(buffer, 0, inlen);
				}
			} finally{
				if(fos != null)
				fos.close();
				if(cis != null)
				cis.close();
			}
		} else {
			inputscanner = new Scanner(is);
			result = inputscanner.nextLine();
			while (EMPTYSTRING.equals(result))
				result = inputscanner.hasNext() ? inputscanner.nextLine() : null;
			os.writeBytes(IngrianProvider.byteArray2Hex(cipher.doFinal(result
					.getBytes())));
		}
    	return true;
    }
    

	private static boolean doEncryptGCM(String keyName, String algName,
			byte[] iv, NAESession session, String authTagLength, String aad, String inFile, String outFile)
			throws Exception {

		Key key = NAEKey.getSecretKey(keyName, session);

		boolean isAADSpecified = false;
		if ((null != aad) && !EMPTYSTRING.equals(aad)) {
			isAADSpecified = true;
		}

		Integer authtaglength = Integer.parseInt(authTagLength);
		if (authtaglength == null) {
			System.err.println("Unknown AuthTagLength");
		}

		NAECipher cipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding",
				"IngrianProvider");
		if (isAADSpecified) {
			byte[] aadBytes = IngrianProvider.hex2ByteArray(aad);

			GCMParameterSpec gcmSpec = new GCMParameterSpec(
					authtaglength.intValue(), iv, aadBytes);
			try {
				cipher.init(Cipher.ENCRYPT_MODE, key, gcmSpec);
			} catch (InvalidAlgorithmParameterException e) {
				
				throw new NAEException("Encrypt: failed - " + e.getMessage());
			} catch (InvalidKeyException e) {
				throw e;
			}
		} else {
			try {
				GCMParameterSpec gcmSpec = new GCMParameterSpec(
						authtaglength.intValue(), iv);
				cipher.init(Cipher.ENCRYPT_MODE, key, gcmSpec);
			} catch (InvalidKeyException e) {
				throw e;
			} catch (InvalidAlgorithmParameterException e) {
				throw e;
			}
		}
		String result = null;
		inputscanner = new Scanner(is);
		result = inputscanner.nextLine();

		if (inFile != null && outFile != null) {
			NAEAESGCMCipher gcm = cipher.get_spi();
			gcm.update(inFile, outFile, 1024, cipher);
		} else {
			while (EMPTYSTRING.equals(result))
				result = inputscanner.hasNext() ? inputscanner.nextLine() : null;
			os.writeBytes(IngrianProvider.byteArray2Hex(cipher.doFinal(result
					.getBytes())));
		}

		return true;

	}

	private static boolean doEncryptFPE(String keyName, String algName,
			byte[] iv, NAESession session, String tweakData, String tweakAlgo)
			throws Exception {

		Key key = NAEKey.getSecretKey(keyName, session);

		IvParameterSpec ivSpec = null;
		NAEIvAndTweakDataParameter ivtweak = null;
		if (iv == null) {
			ivtweak = new NAEIvAndTweakDataParameter(tweakData, tweakAlgo);
		} else {
			ivSpec = new IvParameterSpec(iv);
			// Initializes IV and tweak parameters

			ivtweak = new NAEIvAndTweakDataParameter(ivSpec, tweakData,
					tweakAlgo);
		}
		// get a cipher
		Cipher cipher = null;
		try {
			if(algName.toUpperCase().endsWith("CARD10"))
				cipher = NAECipher.getNAECipherInstance("FPE/AES/CARD10", "IngrianProvider");
			else if(algName.toUpperCase().endsWith("CARD26"))
				cipher = NAECipher.getNAECipherInstance("FPE/AES/CARD26", "IngrianProvider");
			else if(algName.toUpperCase().endsWith("CARD62"))
				cipher = NAECipher.getNAECipherInstance("FPE/AES/CARD62", "IngrianProvider");
		} catch (NoSuchAlgorithmException e) {
			throw e;
		}
		// initialize cipher to encrypt.
		cipher.init(Cipher.ENCRYPT_MODE, key, ivtweak);

		String result = null;

		inputscanner = new Scanner(is);
		result = inputscanner.nextLine();
		while (EMPTYSTRING.equals(result)) {
			result = inputscanner.hasNext() ? inputscanner.nextLine()
					: null;
		}
		os.write(cipher.doFinal(result.getBytes()));
		return true;

	}

        
 
    /** Decrypts a string based on the input parameters. The decrypted value
     * is print to the output stream.
     * @param keyName Key name to use
     * @param algName Algorithm name to use
     * @param iv IV to use
     * @param session NAESession
     * @throws Exception
     * @return returns whether the operation was succesful
     */    
	private static boolean doDecrypt(String keyName, String algName, byte[] iv,
			NAESession session, String outFile) throws Exception {

		// error checking
		if (keyName == null) {
			System.err.println("Missing key name");
			return false;
		}
		if (algName == null) {
			System.err.println("Missing algorithm name");
			return false;
		}
		if (iv == null && algName.indexOf("CBC") > 0) {
			iv = new byte[16];
			for (int i = 0; i < iv.length; i++)
				iv[i] = 0x00;
		}
		if (iv != null && algName.indexOf("CBC") < 0) {
			System.err.println("IV is not required for this algorithm.");
			return false;
		}
		
		Key key;
		if (algName.toUpperCase().startsWith("RSA")) // retrieve RSA private key
			key = NAEKey.getPrivateKey(keyName, session);
		else
			// retrieve secret key
			key = NAEKey.getSecretKey(keyName, session);

		// create cipher instance
		Cipher cipher = NAECipher.getInstance(algName, "IngrianProvider");
		if (iv == null)
			cipher.init(Cipher.DECRYPT_MODE, key);
		else
			cipher.init(Cipher.DECRYPT_MODE, key, new IvParameterSpec(iv));
		
		byte[] buffer = new byte[BUFFER_LEN];

		if (is instanceof FileInputStream) {
			CipherInputStream cis = null;
			FileOutputStream fos = null;
			try{
				cis = new CipherInputStream(is, cipher);
				fos = new FileOutputStream(outFile);
	
				for (int inlen = 0; (inlen = cis.read(buffer)) != -1;) {
					fos.write(buffer, 0, inlen);
				}
			} finally{
				if(cis != null)
				cis.close();
				if(fos != null)
				fos.close();
			}
		} else {
			Scanner inputscanner = new Scanner(is);
			String result = inputscanner.nextLine();
			while (EMPTYSTRING.equals(result.trim()))
				result = inputscanner.hasNext() ? inputscanner.nextLine() : null;
			os.writeBytes(IngrianProvider.toString(cipher
					.doFinal(IngrianProvider.hex2ByteArray(result))));
			inputscanner.close();
		}

		return true;

	}
    
	private static boolean doDecryptGCM(String keyName, String algName,
			byte[] iv, NAESession session, String authTagLength, String aad, String inFile, String outFile)
			throws Exception {

		Key key = NAEKey.getSecretKey(keyName, session);

		boolean isAADSpecified = false;
		if ((null != aad) && !EMPTYSTRING.equals(aad)) {
			isAADSpecified = true;
		}

		Integer authtaglength = Integer.parseInt(authTagLength);
		if (authtaglength == null) {
			System.err.println("Unknown AuthTagLength");
		}

		NAECipher cipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding",
				"IngrianProvider");
		if (isAADSpecified) {
			byte[] aadBytes = IngrianProvider.hex2ByteArray(aad);

			GCMParameterSpec gcmSpec = new GCMParameterSpec(
					authtaglength.intValue(), iv, aadBytes);
			try {
				cipher.init(Cipher.DECRYPT_MODE, key, gcmSpec);
			} catch (InvalidAlgorithmParameterException e) {
				
				throw new NAEException("Decrypt: failed - " + e.getMessage());
				// e.printStackTrace();
			} catch (InvalidKeyException e) {
				throw e;
			}
		} else {
			try {
				GCMParameterSpec gcmSpec = new GCMParameterSpec(
						authtaglength.intValue(), iv);
				cipher.init(Cipher.DECRYPT_MODE, key, gcmSpec);
			} catch (InvalidKeyException e) {
				throw e;
			} catch (InvalidAlgorithmParameterException e) {
				throw e;
			}
		}
		inputscanner = new Scanner(is);
		String result = inputscanner.nextLine();
		if (inFile != null && outFile != null) {
			NAEAESGCMCipher gcm = cipher.get_spi();
			gcm.update(inFile, outFile, 1024, cipher);
		} else {
			while (EMPTYSTRING.equals(result.trim()))
				result = inputscanner.hasNext() ? inputscanner.nextLine() : null;
			os.write(cipher.doFinal(IngrianProvider.hex2ByteArray(result)));
		}

		return true;

	}

	private static boolean doDecryptFPE(String keyName, String algName,
			byte[] iv, NAESession session, String tweakData, String tweakAlgo)
			throws Exception {

		Key key = NAEKey.getSecretKey(keyName, session);

		IvParameterSpec ivSpec = null;
		NAEIvAndTweakDataParameter ivtweak = null;
		if (iv == null) {
			ivtweak = new NAEIvAndTweakDataParameter(tweakData, tweakAlgo);
		} else {
			ivSpec = new IvParameterSpec(iv);
			// Initializes IV and tweak parameters

			ivtweak = new NAEIvAndTweakDataParameter(ivSpec, tweakData,
					tweakAlgo);
		}
		// get a cipher
		Cipher cipher = null;
		try {
			if(algName.toUpperCase().endsWith("CARD10"))
				cipher = NAECipher.getNAECipherInstance("FPE/AES/CARD10", "IngrianProvider");
			else if(algName.toUpperCase().endsWith("CARD26"))
				cipher = NAECipher.getNAECipherInstance("FPE/AES/CARD26", "IngrianProvider");
			else if(algName.toUpperCase().endsWith("CARD62"))
				cipher = NAECipher.getNAECipherInstance("FPE/AES/CARD62", "IngrianProvider");
		} catch (NoSuchAlgorithmException e) {
			throw e;
		}
		// initialize cipher to encrypt.
		cipher.init(Cipher.DECRYPT_MODE, key, ivtweak);

		inputscanner = new Scanner(is);
		String result = inputscanner.nextLine();
		while (EMPTYSTRING.equals(result)) {
			result = inputscanner.hasNext() ? inputscanner.nextLine()
					: null;
		}
		os.write(cipher.doFinal(result.getBytes()));
		return true;

	}

    /** Creates a MAC value for the input string. The value is written to
     * the output stream.
     * @param keyName Key name to use
     * @param algName Algorithm name to use
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doMAC(String keyName, String algName,
        NAESession session) throws Exception {
            
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        if (algName == null) {
            System.err.println("Missing algorithm name");
            return false;
        }

        // retrieve secret key
        SecretKey key = NAEKey.getSecretKey(keyName, session);
        byte[] buffer = new byte [BUFFER_LEN];
        int readBytes;
        
        // create MAC instance
        Mac mac = Mac.getInstance(algName, "IngrianProvider");
        mac.init(key);
        
        // use the MAC instance to operaton on the input stream
        while ((readBytes = is.read(buffer)) >= 0) {
            mac.update(buffer, 0, readBytes);
        }
        byte[] result = mac.doFinal();
        
        // writes the output to the output stream
        os.write(byteArray2Hex(result).getBytes());
        return true;
    }

    /** Verifies a MAC value based on the input parameters. If verified,
     * it prints "MAC Verified OK" to the output stream.
     * @param keyName Key name to use
     * @param algName Algorithm name to use
     * @param macValue MAC value to use
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doMACV(String keyName, String algName,
        byte[] macValue, NAESession session) throws Exception {
            
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        if (algName == null) {
            System.err.println("Missing algorithm name");
            return false;
        }
        if (macValue == null && !algName.equals("IngrianHMac")) {
            System.err.println("Missing mac value to verify");
            return false;
        }

        // retrieve secret key
        SecretKey key = NAEKey.getSecretKey(keyName, session);
        byte[] buffer = new byte [BUFFER_LEN];
        int readBytes;
        
        // create MAC instance
        Mac mac = Mac.getInstance(algName + "Verify", "IngrianProvider");
        mac.init(key, new MACValue(macValue));
        
        // use the MAC instance to verify the input stream
        while ((readBytes = is.read(buffer)) >= 0) {
            mac.update(buffer, 0, readBytes);
        }
        byte[] result = mac.doFinal();
        
        // check verification result and print message 
        // to output stream
        if (result.length != 1 || result[0] != 1) {
            os.write("Invalid MAC\n".getBytes());
        } else {
            os.write("MAC Verified OK\n".getBytes());
        }
        return true;
    }

    /** Signs the input value based on the parameter given. The
     * signed value is written to the output stream.
     * @param keyName Key name to use
     * @param algName Algorithm name to use
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operatino was successful
     */    
    private static boolean doSign(String keyName, String algName,
        NAESession session) throws Exception {
            
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        if (algName == null) {
            System.err.println("Missing algorithm name");
            return false;
        }

        // retrieve private key
        PrivateKey key = NAEKey.getPrivateKey(keyName, session);
        byte[] buffer = new byte [BUFFER_LEN];
        int readBytes;
        
        // create signature instance
        Signature signature = Signature.getInstance(algName, "IngrianProvider");
        signature.initSign(key);
        
        // sign the input stream
        while ((readBytes = is.read(buffer)) >= 0) {
            signature.update(buffer, 0, readBytes);
        }
        byte[] result = signature.sign();
        
        // writes the signed value to the output stream
        os.write(byteArray2Hex(result).getBytes());
        return true;
    }

    /** Verifies a signature based on the input parameters. If
     * verified, it prints "Signature verified OK" to the output
     * stream.
     * @param keyName Key name to use
     * @param algName Algorith name to use
     * @param sig Signed value
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doSignV(String keyName, String algName,
        byte[] sig, NAESession session) throws Exception {
            
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        if (algName == null) {
            System.err.println("Missing algorithm name");
            return false;
        }
        if (sig == null) {
            System.err.println("Missing signature value to verify");
            return false;
        }
        
        // retrieve public key
        PublicKey key = NAEKey.getPublicKey(keyName, session);
        byte[] buffer = new byte [BUFFER_LEN];
        int readBytes;
        
        // create signature instance
        Signature signature = Signature.getInstance(algName, "IngrianProvider");
        signature.initVerify(key);
        
        // verify the input stream and print message to the
        // output stream
        while ((readBytes = is.read(buffer)) >= 0) {
            signature.update(buffer, 0, readBytes);
        }
        if (signature.verify(sig)) {
            os.write("Signature verified OK\n".getBytes());
        } else {
            os.write("Invalid signature\n".getBytes());
        }
        return true;
    }

    /** Generates a key based on the input parameters.
     * @param keyName Key name to use
     * @param algName Algorith name to use
     * @param session NAESession
     * @param exportable Signifies whether the generated key is exportable
     * @param deletable Signifies whether the generate key is deletable
     * @param size Key size
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doGenerate(String keyName, String algName,
        NAESession session, boolean exportable, boolean deletable, int size) throws Exception {
            
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        if (algName == null) {
            System.err.println("Missing algorithm name");
            return false;
        }

        // Create key generator and use it to create the key
        if (!"RSA".equalsIgnoreCase(algName)) {
            KeyGenerator kg = KeyGenerator.getInstance(algName,
                "IngrianProvider");
            kg.init(new NAEParameterSpec(keyName, exportable, deletable, size, session));
            kg.generateKey();
        } else {
            KeyPairGenerator kpg = KeyPairGenerator.getInstance(algName,
                "IngrianProvider");
            kpg.initialize(new NAEParameterSpec(keyName,
                exportable, deletable, size, session));
            kpg.genKeyPair();
        }
        os.write("Key generated OK\n".getBytes());
        return true;
    }

    /** Deletes a key.
     * @param keyName Key name to be deleted
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doDelete(String keyName, NAESession session)
        throws Exception {
        
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        
        // retrieve NAE key based on key name
        NAEKey key = NAEKey.getSecretKey(keyName, session);
        
        // delete the key
        key.delete();
        
        // print message to output stream
        os.write("Key deleted OK\n".getBytes());
        return true;
    }

    /** Exports a key to the output stream.
     * @param keyName Key name to export
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doExport(String keyName, NAESession session) 
        throws Exception {
        
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        
        // retrieve NAE key
        NAEKey key = NAEKey.getSecretKey(keyName, session);
        
        if ("RSA".equalsIgnoreCase(key.getAlgorithm())) {
            // if key is RSA key, write the private key to
            // the output stream
            try
            {
                key = NAEKey.getPrivateKey(keyName, session);
                os.write(key.export());
            }
            catch (Exception e)
            {
                key = NAEKey.getPublicKey(keyName, session);
                os.write(key.export());
            }
        } else {
            // if key is non-RSA key, export the key to
            // the output stream

	    os.write(key.export());
        }
        return true;
    }

    /** Imports a key to the NAE server based on the
     * input parameters and the input stream.
     * @param keyName Key name to use
     * @param algName Algorithm name to use
     * @param session NAESession
     * @param exportable Signifies whether the key is exportable
     * @param deletable Signifies whether the key is deletable
     * @param size Key size
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doImport(String keyName, String algName,
        NAESession session, boolean exportable, boolean deletable, 
        int size) throws Exception {
            
        // error checking
        if (keyName == null) {
            System.err.println("Missing key name");
            return false;
        }
        if (algName == null) {
            System.err.println("Missing algorithm name");
            return false;
        }
        
        // create byte array based on input stream
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buffer = new byte [BUFFER_LEN];
        int readBytes;
        while ((readBytes = is.read(buffer)) >= 0) {
            bos.write(buffer, 0, readBytes);
        }

        // import the key based on the parameters given
        if (!"RSA".equalsIgnoreCase(algName)) {
            NAEKey.importKey (bos.toByteArray(), algName,
			      new NAEParameterSpec(keyName, exportable, deletable, size, session));
        } else {
            NAEKey.importKey (bos.toByteArray(), algName,
            new NAEParameterSpec(keyName, exportable, deletable, size, session));
        }
        os.write("Key imported OK\n".getBytes());
        return true;
    }

    /** List all the keys found in the NAE server
     * @param session NAESession
     * @throws Exception
     * @return Returns whether the operation was successful
     */    
    private static boolean doList( NAESession session) throws Exception {
        // retrieve all keys from the NAE server
        NAEKey[] keys = NAEKey.getKeys(session);
        
        // write all the key names and algorithms to
        // the string buffer
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i< keys.length; i++) {
            if (!(keys[i] instanceof PublicKey)) {
                sb.append(keys[i].getName());
                sb.append(" : ");
                sb.append(keys[i].getAlgorithm());
                sb.append('\n');
            }
        }
        
        // write the string buffer to output stream
        os.write(sb.toString().getBytes());
        return true;
    }

    private static final char[] enc =
         { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};

    /** Utility function that translates a byte array to a HEX string. */         
    private static String byteArray2Hex(byte[] bytes) {
        StringBuffer sb = new StringBuffer();
        for (int i= 0; i< bytes.length; i++) {
            sb.append(enc[(bytes[i] >> 4) & 0xF]);
            sb.append(enc[bytes[i] & 0xF]);
        }
        return sb.toString();
    }

    /** Utility function that translates a HEX string to a byte array. */    
    private static byte[] hex2ByteArray(String str) {
        if (str.length() % 2 != 0)
            return null;
        for (int i = 0; i < str.length(); i++) {
            char tmp = str.charAt(i);
            if ( (tmp >= '0' && tmp <= '9') ||
                (tmp >= 'A' && tmp <= 'F') ||
                (tmp >= 'a' && tmp <= 'f'))
                ;
            else
                return null;
        }

        int len = str.length() / 2;
        byte[] retVal = new byte[len];
        for (int i = 0; i < len; i++) {
            retVal[i] = (byte) ((byteHexValue(str.charAt(2 * i)) << 4) +
                                byteHexValue(str.charAt(2 * i + 1)));
        }
        return retVal;
    }

    /** Utility function that returns an integer based on the HEX character */    
    private static int byteHexValue(char c) {
        int val = 0;
        if (c >= '0' && c <= '9')
            val = (c - '0');
        if (c >= 'A' && c <= 'Z')
            val = (c - 'A') + 10;
        if (c >= 'a' && c <= 'z')
            val = (c - 'a') + 10;
        return val;
    }

    private static InputStream is;
    private static DataOutputStream os;
    private static Scanner inputscanner;
    /** Main routine. First it builds a hash table of parameter values.
     * Then from this hash table, it retrieves all the necessary
     * parameters. Based on the operation specified by the user, the
     * appropriate functions are called.
     */    
    public static void main(String[] args) throws Exception {
    	Map<String,String> arguments;

    	// check parameter lengths, etc.
    	if (args.length > 0 && args[0].equals(HELP)) {
    		printUsage();
    		System.exit(0);
    	}
    	if ((arguments = buildArguments(args)) == null) {
    		printErrorAndExit();
    	}

    	// retrieve IP, port number and protocol
    	String ip = (String) arguments.get(IP);
    	if (ip != null) {
    		System.setProperty("com.ingrian.security.nae.NAE_IP.1", ip);
    	}

    	String port = (String) arguments.get(PORT);
    	if (port != null) {
    		System.setProperty("com.ingrian.security.nae.NAE_Port", port);
    	}

    	String protocol = (String) arguments.get(PROTOCOL);
    	if (protocol != null) {
    		System.setProperty("com.ingrian.security.nae.Protocol", protocol);
    	}

    	java.security.Security.addProvider(new IngrianProvider());
    	// get input stream
    	is = getInputStream(arguments);
    	if (is == null) {
    		printErrorAndExit();
    	}

    	// get output stream
    	os = getOutputStream(arguments);
    	if (os == null) {
    		printErrorAndExit();
    	}

    	// get operation
    	int operation = getOperation(args[0]);
    	if (operation < 0) {
    		printErrorAndExit();
    	}

    	// get the rest of the parameters..
    	String keyName = getKeyName(arguments);
    	String algName = getAlgorithmName(arguments);
    	String auth = getAuth(arguments);
    	//String dbauth = getDBAuth(arguments);
    	int keySize = getKeySize(arguments);
    	boolean exportable = getExportable(arguments);
    	boolean deletable = getDeletable(arguments);
    	String inFile = (String)arguments.get(INFILE);
    	String outFile = (String)arguments.get(OUTFILE);
    	    	
    	// create NAE session using the user name and
    	// password passed in as parameters.
    	NAESession session = null;
    	String user = null;
		String passwd = null;
		
		
    	if (auth != null) {
    		int colon = auth.indexOf(':');
    		if (colon < 1 || colon == (auth.length() - 1)) {
    			System.err.println("Invalid -auth argument");
    			printErrorAndExit();
    		}
    		user = auth.substring(0, colon);
    		passwd = auth.substring(colon + 1, auth.length());
    		if(knownOperations.get(args[0])!=null)
    		session = NAESession.getSession(user, passwd.toCharArray());
    		
		}
    	
    	// get IV, signature and MAC if available
    	byte[] iv = getIV(arguments);
    	byte[] signature = getSignature(arguments);
    	byte[] mac = getMAC(arguments);
    	boolean result = false;

    	// parameters for GCM
    	String authTagLength = getAuthtaglength(arguments);
    	String aad = getAad(arguments);
    	String tweakData = getTweakdata(arguments);
    	String tweakAlgo = getTweakalgo(arguments);

    	// call the appropriate operation based on
    	// the operation specified by the user.
    	try{
    		switch (operation) {
	    	case ENCRYPTINT:
	    		if (algName.toUpperCase().startsWith("FPE"))
	    			result = doEncryptFPE(keyName, algName, iv, session, tweakData,
	    					tweakAlgo);
	    		else if (algName.toUpperCase().contains("GCM"))
	    			result = doEncryptGCM(keyName, algName, iv, session, authTagLength, aad, inFile, outFile);
	    		else
	    			result = doEncrypt(keyName, algName, iv, session, outFile);
	    		break;
	    	case DECRYPTINT:
	    		if (algName.toUpperCase().startsWith("FPE"))
	    			result = doDecryptFPE(keyName, algName, iv, session, tweakData,
	    					tweakAlgo);
	    		else if (algName.toUpperCase().contains("GCM"))
	    			result = doDecryptGCM(keyName, algName, iv, session, authTagLength, aad, inFile, outFile);
	    		else
	    			result = doDecrypt(keyName, algName, iv, session, outFile);
	    		break;
	    	case MACINT:
	    		result = doMAC(keyName, algName, session);
	    		break;
	    	case MACVINT:
	    		result = doMACV(keyName, algName, mac, session);
	    		break;
	    	case SIGNINT:
	    		result = doSign(keyName, algName, session);
	    		break;
	    	case SIGNVINT:
	    		result = doSignV(keyName, algName, signature, session);
	    		break;
	    	case GENERATEINT:
	    		result = doGenerate(keyName, algName, session, exportable,
	    				deletable, keySize);
	    		break;
	    	case DELETEINT:
	    		result = doDelete(keyName, session);
	    		break;
	    	case IMPORTINT:
	    		result = doImport(keyName, algName, session, exportable, deletable,
	    				keySize);
	    		break;
	    	case EXPORTINT:
	    		result = doExport(keyName, session);
	    		break;
	    	case LISTINT:
	    		result = doList(session);
	    		break;
	    	default:
	    		System.err.println("Invalid operation");
	    	}
	
	    	// if operation failed, print error message.
	    	if (!result) {
	    		printErrorAndExit();
	    	}
	    	
    	}catch(Exception e)
    	{
    		System.out.println("Exception occurred : " + e.getMessage());
    	}
    	finally
    	{
    		if(os != null)
    			{
    				os.flush();
    				os.close();
    			}
    		if(inputscanner != null)
    			inputscanner.close();
    		if(is != null)
    			is.close();
    		if (session!=null && !session.isClosed())
    			session.closeSession();
    	}
    }

		
	/**
	 * This method prints usage and exit.
	 */
	private static void printErrorAndExit() {
		System.err.println("Use -help to print usage");
		System.exit(-1);
	}

}
