/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.StringWriter;
import java.security.KeyFactory;
import java.security.MessageDigest;
import java.security.PublicKey;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.util.HashMap;
import java.util.Map;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;

import org.bouncycastle.asn1.ASN1ObjectIdentifier;
import org.bouncycastle.asn1.ASN1Primitive;
import org.bouncycastle.asn1.pkcs.PKCSObjectIdentifiers;
import org.bouncycastle.asn1.x509.SubjectPublicKeyInfo;
import org.bouncycastle.asn1.x9.X9ObjectIdentifiers;
import org.bouncycastle.util.encoders.Base64;
import org.bouncycastle.util.io.pem.PemObject;
import org.bouncycastle.util.io.pem.PemWriter;

import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecretKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.WrapFormatPadding;												  

public class ByokSample {
	public static void main(String[] args) {
		
		if (args.length < 12)
			checkUsage();
		try {
			Map<String, String> inputs = fetchInputArguments(args);

			String username = inputs.get("userName");
			String password = inputs.get("password");
			String cloudName = inputs.get("cloudName").toLowerCase();
			String aesKeyName = inputs.get("aesKeyName");
			String publicKeyPath = inputs.get("publicKeyPath");
			String wrappedKeyPath = inputs.get("wrappedKeyPath");
			String wrappingKeyName = inputs.get("wrappingKeyName");
			String wrappingAlgo = inputs.get("wrappingAlgo");
			String hash256Path = inputs.get("hash256Path");
			String outputFormat = inputs.get("outputFormat") == null ? "default"
					: inputs.get("outputFormat").toLowerCase();
			//sha256 is supported by Java 8 and above
			checkIfJavaSupportedWrappingAlgo(wrappingAlgo, 1.8);
			
           byte[] wrappedKey,publicKeyBytes = null;
           //read public key from file if publicKeyPath is not null
           if(publicKeyPath != null)
			publicKeyBytes=("aws".equals(cloudName))?readAWSPublicKeyFromFile(publicKeyPath):readPublicKeyFromcloudFile(publicKeyPath);
             wrappedKey = wrapKeyFromKS(username, password, aesKeyName,
					wrappingKeyName, wrappingAlgo, publicKeyBytes,cloudName,hash256Path);
		  // write wrapped key into file in Base64 format.
			writeInFile(cloudName,wrappedKeyPath, wrappedKey, outputFormat);
            System.out.println("Key wrapped and saved in file successfully.");
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}

	private static byte[] readPublicKeyFromcloudFile(String publicKeyPath) {
		byte[] parsedByte=null;
		PublicKey publicKey;
		try {
			publicKey = readPublicKeyFromFile(publicKeyPath);
		byte[] pubBytes = publicKey.getEncoded();
		SubjectPublicKeyInfo spkInfo = SubjectPublicKeyInfo
				.getInstance(pubBytes);
		ASN1Primitive primitive = spkInfo.parsePublicKey();
		if(primitive!=null)
		return primitive.getEncoded();
		} catch (Exception e) {
			throw new NAEException("Unable to read public key from public key path"+e.getMessage());
		}
		return parsedByte;
		
	}

	private static byte[] readAWSPublicKeyFromFile(String publicKeyPath)
			throws Exception {
		File file = new File(publicKeyPath);
		FileInputStream ios = new FileInputStream(file);
		byte[] buffer = new byte[(int) file.length()];
		try{
			ios.read(buffer);
		}
		finally{
			ios.close();
		}
		// format conversion to PEM encoded PKCS#1 to allow import on to
		// keysecure
		X509EncodedKeySpec spec1 = new X509EncodedKeySpec(buffer);
		KeyFactory kf1 = KeyFactory.getInstance("RSA");
		RSAPublicKey pubKey = (RSAPublicKey) kf1.generatePublic(spec1);

		byte[] pubBytes = pubKey.getEncoded();
		SubjectPublicKeyInfo spkInfo = SubjectPublicKeyInfo
				.getInstance(pubBytes);
		ASN1Primitive primitive = spkInfo.parsePublicKey();
		if(primitive != null)
			return primitive.getEncoded();
		return null;
	}

	public static PublicKey generatePublicKey(final SubjectPublicKeyInfo pkInfo)
			throws Exception {
		X509EncodedKeySpec keyspec;
		try {
			keyspec = new X509EncodedKeySpec(pkInfo.getEncoded());
		} catch (IOException e) {
			throw new InvalidKeySpecException(e.getMessage(), e);
		}
		ASN1ObjectIdentifier aid = pkInfo.getAlgorithm().getAlgorithm();
		KeyFactory kf;
		if (PKCSObjectIdentifiers.rsaEncryption.equals(aid)) {
			kf = KeyFactory.getInstance("RSA");
		} else if (X9ObjectIdentifiers.id_dsa.equals(aid)) {
			kf = KeyFactory.getInstance("DSA");
		} else if (X9ObjectIdentifiers.id_ecPublicKey.equals(aid)) {
			kf = KeyFactory.getInstance("ECDSA");
		} else {
			throw new InvalidKeySpecException("unsupported key algorithm: "
					+ aid);
		}
		return kf.generatePublic(keyspec);
	}

	/** read public key from the file and convert it to X.509 format. 
	 * @throws IOException */
	private static PublicKey readPublicKeyFromFile(String publicKeyPath)
			throws CertificateException, IOException {
		File file = new File(publicKeyPath);
		FileInputStream ios = null;
		PublicKey key = null;
		try{
			ios = new FileInputStream(file);
			CertificateFactory fact = CertificateFactory.getInstance("X.509");
			X509Certificate cer = (X509Certificate) fact.generateCertificate(ios);
			key = cer.getPublicKey();
		}finally{
			if(ios != null)
				ios.close();
		}
		
		return key;
	}

	private static Map<String, String> fetchInputArguments(String[] args) {
		if (args == null)
			checkUsage();
		Map<String, String> inputs = new HashMap<String, String>();
		for (int i = 0; i < args.length; i++) {
			if ("-cloudName".equals(args[i]))
				inputs.put("cloudName", args[i + 1]);
			else if ("-userName".equals(args[i]))
				inputs.put("userName", args[i + 1]);
			else if ("-password".equals(args[i]))
				inputs.put("password", args[i + 1]);
			else if ("-aesKeyName".equals(args[i]))
				inputs.put("aesKeyName", args[i + 1]);
			else if ("-publicKeyPath".equals(args[i]))
				inputs.put("publicKeyPath", args[i + 1]);
			else if ("-wrappedKeyPath".equals(args[i]))
				inputs.put("wrappedKeyPath", args[i + 1]);
			else if ("-wrappingKeyName".equals(args[i]))
				inputs.put("wrappingKeyName", args[i + 1]);
			else if ("-wrappingAlgo".equals(args[i]))
				inputs.put("wrappingAlgo", args[i + 1]);
			else if ("-hash256Path".equals(args[i]))
				inputs.put("hash256Path", args[i + 1]);
			else if ("-outputFormat".equals(args[i]))
				inputs.put("outputFormat", args[i + 1]);
		}
		validateInput(inputs);
		return inputs;
	}

	private static void checkUsage() {
		System.err.println("Usage: java ByokSample"
				+ " -cloudName [AWS|Salesforce|GoogleCloud]" // cloud
																// name
				+ " -userName <userName> " // Key Manager username
				+ " -password <password>" // Key Manager password
				+ " -aesKeyName <aes-256 Key Name>" // aes key name on
													// Key Manager
				+ " [ -publicKeyPath <public key path>]" // file
														// path
														// of
														// the
														// public
														// key
				+ " -wrappedKeyPath <wrapped key path>" // destination
														// path
														// where
														// wrapped
														// key
														// will
														// be
														// stored
				+ " [ -wrappingKeyName RSA KeyName]" // RSA key name import to
													// the Key Manager
				// format of wrapped key needs to be stored in file.
				+ " [-outputFormat base64]"
				// for AWS only. Key should not exist on Key Manager.
				+ " -wrappingAlgo [SHA1|SHA256|PKCS1.5]" // Google cloud
															// supports
															// only SHA1 and
															// SHA256,
															// AWS supports
															// PKCS1.5 as
															// well
				+ " [-hash256Path filePath]"); // specific
														// to
														// salesforce
														// only
		System.exit(-1);
	}

	private static void validateInput(Map<String, String> inputs) {
		StringBuilder errorMsg = new StringBuilder();
		String cloudName = inputs.get("cloudName").toLowerCase();
		if (!cloudName.equals("aws") && !cloudName.equals("salesforce")
				&& !cloudName.equals("googlecloud"))
			errorMsg.append("cloud " + cloudName + "  not supported" + "\n");
		if (inputs.get("userName") == null)
			errorMsg.append("username not provided" + "\n");
		if (inputs.get("password") == null)
			errorMsg.append("password not provided" + "\n");
		if (inputs.get("aesKeyName") == null)
			errorMsg.append("key name not provided" + "\n");
		if (inputs.get("wrappedKeyPath") == null)
			errorMsg.append("wrapped key path not provided" + "\n");
		if (inputs.get("wrappingAlgo") == null)
			errorMsg.append("wrapping algoname not provided");
		if (inputs.get("wrappingKeyName") == null
				&& "pkcs1.5".equals(inputs.get("wrappingAlgo").toLowerCase()))
			errorMsg.append("wrapped key name not provided" + "\n");
		if (inputs.get("hash256Path") == null){
			if(cloudName.equalsIgnoreCase("salesforce"))
				errorMsg.append("hash256Path is mandatory for salesforce cloud");
		}
		if (inputs.get("outputFormat") != null) {
			String format = inputs.get("outputFormat");
			if (!"default".equals(format.toLowerCase())
					&& !"base64".equals(format.toLowerCase()))
				errorMsg.append(format + " is not supported.");
			if(!"base64".equals(format.toLowerCase()) && (cloudName.equalsIgnoreCase("salesforce")||cloudName.equalsIgnoreCase("googlecloud")))
				errorMsg.append("only base64 format is support in salesforce");
		}
		if(inputs.get("wrappingAlgo") != null){
            String wrappingAlgo=inputs.get("wrappingAlgo");
			if((cloudName.equalsIgnoreCase("salesforce") || cloudName.equalsIgnoreCase("googleCloud")) && !wrappingAlgo.equalsIgnoreCase("SHA1")) {
				errorMsg.append("only SHA1 wrapping Algorithm support for selected cloud");
			}
		}
		if (errorMsg.length() != 0)
			throw new NAEException(errorMsg.toString());
	}

	
	private static void validateKeySize(NAEKey aesKey, int allowedSize) {
		if (aesKey.getKeySize() != allowedSize)
			throw new NAEException("Only key with size " + allowedSize
					+ " allowed");
	}

	private static byte[] wrapKeyFromKS(String username, String password,
			String aesKeyName, String wrappingKeyName, String wrappingAlgo,
			byte[] publicKey, String cloudName, String hash256Path) throws Exception {
		String pemString = null;
		if(publicKey!=null){
		PemObject pemObject = new PemObject("RSA PUBLIC KEY", publicKey);
		StringWriter stringWriter = new StringWriter();
		PemWriter pemWriter = new PemWriter(stringWriter);
		pemWriter.writeObject(pemObject);
		pemWriter.close();
		pemString = stringWriter.toString();
		}
		NAESession session = null;
		try {
			// create nae session
			session = NAESession.getSession(username, password.toCharArray());
			NAESecretKey secretKey = NAEKey.getSecretKey(aesKeyName, session);
			if (isKeyNameValid(secretKey))
				validateKeySize(secretKey, 256);
			else{
				createAES256Key(aesKeyName, session);
				secretKey = NAEKey.getSecretKey(aesKeyName, session);
			}
				
			//Need not import if publicKey is null
			if(publicKey!=null){
			// key import spec 
			NAEParameterSpec rsaParamSpec = new NAEParameterSpec(
					wrappingKeyName, true, true, session, null);
   
			// import the rsa public key
			NAEPublicKey.importKey(pemString.getBytes("UTF-8"), "RSA", rsaParamSpec);
			}
			// get key handle to the imported RSA key
			NAEPublicKey pubRSAKey = NAEKey.getPublicKey(wrappingKeyName,
					session);
			// spec for key to be wrapped
			NAEParameterSpec aesSpec = new NAEParameterSpec(aesKeyName, true,
					true, 256, session);
			//setting padding format to wrap a key
			aesSpec.setWrapPaddingFormat("PKCS1.5".equals(wrappingAlgo.toUpperCase()) ? WrapFormatPadding.DEFAULT : WrapFormatPadding.valueOf(wrappingAlgo.toUpperCase()));
			// Init a JCE Cipher in WRAP_MODE to do the key wrapping.
			Cipher cipher = Cipher.getInstance("RSA", "IngrianProvider");
			cipher.init(Cipher.WRAP_MODE, pubRSAKey, aesSpec);
			byte[] wrappedByte= cipher.wrap(secretKey);
			//write hash
			if(cloudName.equalsIgnoreCase("salesforce")) {
				writeHashToTheFile(cloudName,secretKey.getKeyData(), hash256Path);}
			return wrappedByte;
		} finally {
			if (session != null)
				session.closeSession();
		}
	}
	
	private static void createAES256Key(String aesKeyName, NAESession session)
			throws Exception {
		NAEParameterSpec spec = new NAEParameterSpec(aesKeyName, true, true,
				true, 256, null, session);
		KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
		kg.init(spec);
		kg.generateKey();
	}

	private static boolean isKeyNameValid(NAESecretKey secretKey)
			throws Exception {
		try {
			return secretKey.isValid();
		} catch (Exception e) {
			System.out.println("Invalid secret key");
		}
		return false;
	}

	private static void writeInFile(String cloudName,String wrappedKeyPath, byte[] wrappedKey,
			String outputFormat) throws FileNotFoundException, IOException {
		wrappedKeyPath=validateFileFormat(cloudName, wrappedKeyPath);
		FileOutputStream out = new FileOutputStream(wrappedKeyPath);
		try{
			if ("default".equals(outputFormat))
				out.write(wrappedKey);
			else
				out.write(Base64.toBase64String(wrappedKey)
						.getBytes());
		}finally{	
			out.close();
		}
	}

	private static void checkIfJavaSupportedWrappingAlgo(String wrappingAlgo, double supportedVersion) {
		 String version = System.getProperty("java.version");
		    int pos = version.indexOf('.');
		    pos = version.indexOf('.', pos+1);
		    Double curVer = Double.parseDouble (version.substring (0, pos));
		    if (wrappingAlgo.equalsIgnoreCase("sha256") && curVer < supportedVersion)
		    	 throw new NAEException(wrappingAlgo +  " is supported by"
		    	 		+ " Java version " + supportedVersion +   " and above.");
	}
	private static void writeHashToTheFile(String cloudName,byte[] wrappedKey, String hash256Path)
			throws Exception {
		if (hash256Path != null) {
			MessageDigest digest = MessageDigest.getInstance("SHA-256");
			byte[] hash = digest.digest(wrappedKey);
			writeInFile(cloudName,hash256Path, hash, "base64");
			System.out.println("hash saved to the file");
		}
	}
	
	private static String validateFileFormat(String cloudName,String fileName){
		if(cloudName.equalsIgnoreCase("salesforce") && !fileName.contains(".b64")){
			return fileName.concat(".b64");
		}
		return fileName;
	}
}
