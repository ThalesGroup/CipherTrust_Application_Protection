/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.math.BigInteger;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.security.spec.InvalidKeySpecException;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import sun.security.x509.AlgorithmId;
import sun.security.x509.CertificateAlgorithmId;
import sun.security.x509.CertificateExtensions;
import sun.security.x509.CertificateIssuerName;
import sun.security.x509.CertificateSerialNumber;
import sun.security.x509.CertificateSubjectName;
import sun.security.x509.CertificateValidity;
import sun.security.x509.CertificateVersion;
import sun.security.x509.CertificateX509Key;
import sun.security.x509.KeyUsageExtension;
import sun.security.x509.X500Name;
import sun.security.x509.X509CertImpl;
import sun.security.x509.X509CertInfo;

import com.ecc.security.nae.NAEECIESUtils;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESession;

public class SelfSignedCertificateUtility {

	public static final Pattern JAVA_VERSION = Pattern
			.compile("([0-9]*.[0-9]*)(.*)?");

	public static void main(String[] args) {
		String userName = null;
		String password = null;
		String file = null;
		String key = null;
		String certPass = null;

		for (int i = 0; i < args.length; i++) {
			if ("-user".equals(args[i]))
				userName = args[i + 1].trim();
			else if ("-password".equals(args[i]))
				password = args[i + 1].trim();
			else if ("-key".equals(args[i]))
				key = args[i + 1].trim();
			else if ("-file".equals(args[i]))
				file = args[i + 1].trim();
			else if ("-certPass".equals(args[i]))
				certPass = args[i + 1].trim();
		}

		if (key == null || file == null)
			usage();

		try {
			Map<String, String> certificateProeprties = readPropertiesFrom(file);
			if (certPass != null)
				certificateProeprties.put("CertPassword", certPass);

			validateProperties(certificateProeprties);

			NAESession session = null;
			PrivateKey privateKey = null;
			PublicKey publicKey = null;

			try {
				if (userName != null && password != null)
					session = NAESession.getSession(userName,
							password.toCharArray());
				NAEPrivateKey private1 = NAEKey.getPrivateKey(key, session);
				NAEPublicKey public1 = NAEKey.getPublicKey(key, session);
				
				privateKey = getPrivateKey(private1, certificateProeprties.get("Algorithm"));
				publicKey = getPublicKey(public1, certificateProeprties.get("Algorithm"));
			} finally {
				if (session != null)
					session.closeSession();
			}

			X509Certificate cert = generateCertificate(publicKey, privateKey,
					certificateProeprties);
			storeCertificateInPFX(privateKey, cert, certificateProeprties);
			System.out.println("certificate is stored successfully at " + certificateProeprties.get("Destination"));
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private static PublicKey getPublicKey(NAEPublicKey key, String algo)
					throws IOException, InvalidKeySpecException {
		if (algo.endsWith("ECDSA")) {
			return NAEECIESUtils.getEcPublicKey(new String(key.export(), "UTF-8"));
		}
			
		return key.exportJCEKey();
	}

	private static PrivateKey getPrivateKey(NAEPrivateKey key, String algo) 
					throws IOException, InvalidKeySpecException {
		if (algo.endsWith("ECDSA")) {
			return NAEECIESUtils.getEcPrivateKey(
						key.export(false, "PEM-PKCS#8")[0].getKeyData());
		}
			
		return key.exportJCEKey();
	}

	private static void validateProperties(
			Map<String, String> certificateProeprties) {
		StringBuffer buffer = new StringBuffer();
		if (certificateProeprties.get("Validity") == null) {
			buffer.append("Validity");
			buffer.append(", ");
		} else {
			String days = certificateProeprties.get("Validity");
			if (Integer.valueOf(days) < 0)
				throw new NAEException("Invalid validity period: " + days);
		}

		if (certificateProeprties.get("CertPassword") == null) {
			buffer.append("CertPassword");
			buffer.append(", ");
		}

		if (certificateProeprties.get("Algorithm") == null) {
			buffer.append("Algorithm");
			buffer.append(", ");
		}
		if (certificateProeprties.get("CommonName") == null) {
			buffer.append("CommonName");
			buffer.append(", ");
		}
		if (certificateProeprties.get("CountryName") == null) {
			buffer.append("CountryName");
			buffer.append(", ");
		}
		if (buffer.length() != 0)
			throw new NAEException(buffer.toString() + " missing");
	}

	/**
	 * Store the certificate in pkcs12 format using provided certificate
	 * password and destination. Default alias is 'selfsigned'. In case no
	 * destination provided then current execution directory will be used to
	 * store file.
	 */
	private static void storeCertificateInPFX(PrivateKey privateKey,
			X509Certificate cert, Map<String, String> certificateProeprties)
			throws Exception {
		X509Certificate[] chain = { cert };

		// if destination is not provided than we use current execution
		// directory
		String destination = certificateProeprties.get("Destination");
		if (destination == null) {
			destination = System.getProperty("user.dir")
					+ System.getProperty("file.separator")
					+ "SignedCertificate.pfx";
			certificateProeprties.put("Destination", destination);
		}
		// load the certificate and password in pkcs12 format
		KeyStore store = KeyStore.getInstance("PKCS12");
		store.load(null);
		store.setKeyEntry("selfsigned", privateKey,
				certificateProeprties.get("CertPassword").toCharArray(), chain);

		// store the certificate at given path
		FileOutputStream fOut = new FileOutputStream(destination);
		store.store(fOut, certificateProeprties.get("CertPassword")
				.toCharArray());
		fOut.close();
	}

	private static X509Certificate generateCertificate(PublicKey publicKey,
			PrivateKey privateKey, Map<String, String> certificateProeprties)
			throws Exception {

		String dn = makeDN(certificateProeprties);
		X509CertInfo info = new X509CertInfo();

		Date from = new Date();
		Date to = new Date(from.getTime()
				+ Integer.valueOf(certificateProeprties.get("Validity"))
				* 86400000l);
		CertificateValidity interval = new CertificateValidity(from, to);
		X500Name owner = new X500Name(dn);

		boolean[] kueOk = getKeyUsgaeExtension(certificateProeprties
				.get("KeyUsage"));
		KeyUsageExtension kue = new KeyUsageExtension(kueOk);
		CertificateExtensions ext = new CertificateExtensions();
		ext.set(KeyUsageExtension.NAME, kue);

		info.set(X509CertInfo.VALIDITY, interval);
		BigInteger sn = new BigInteger(64, new SecureRandom());
		info.set(X509CertInfo.SERIAL_NUMBER, new CertificateSerialNumber(sn));

		boolean justName = isJavaAtLeast(1.8);
		if (justName) {
			info.set(X509CertInfo.SUBJECT, owner);
			info.set(X509CertInfo.ISSUER, owner);
		} else {
			info.set(X509CertInfo.SUBJECT, new CertificateSubjectName(owner));
			info.set(X509CertInfo.ISSUER, new CertificateIssuerName(owner));
		}

		info.set(X509CertInfo.KEY, new CertificateX509Key(publicKey));
		info.set(X509CertInfo.VERSION, new CertificateVersion(
				CertificateVersion.V3));

		AlgorithmId algo = null;
		String provider = null;
		
		switch(certificateProeprties.get("Algorithm")) {
			case "SHA1WithRSA":
								break;
			case "SHA256WithRSA": 
								break;
			case "SHA384WithRSA": 
								break;
			case "SHA512WithRSA": 
								provider = "BC";
								break;
			case "SHA1WithECDSA":
								provider = "BC";
								break;
			case "SHA224WithECDSA":
								provider = "BC";
								break;
			case "SHA256WithECDSA": 
								provider = "BC";
								break;
			case "SHA384WithECDSA": 
								provider = "BC";
								break;
			case "SHA512WithECDSA":
								provider = "BC";
								break;
			default:
				throw new NAEException(certificateProeprties.get("Algorithm")
						+ " not supported.");
		}
		 algo = AlgorithmId.get(certificateProeprties.get("Algorithm"));
		info.set(X509CertInfo.ALGORITHM_ID, new CertificateAlgorithmId(algo));
		info.set(X509CertInfo.EXTENSIONS, ext);

		// Sign the cert to identify the algorithm that's used.
		X509CertImpl cert = new X509CertImpl(info);
		if (provider != null)
			cert.sign(privateKey, certificateProeprties.get("Algorithm"), provider);
		else
			cert.sign(privateKey, certificateProeprties.get("Algorithm"));
		return cert;
	}

	public static boolean isJavaAtLeast(double version) {
		String javaVersion = System.getProperty("java.version");
		if (javaVersion == null) {
			return false;
		}

		// if the retrieved version is one three digits, remove the last one.
		Matcher matcher = JAVA_VERSION.matcher(javaVersion);
		if (matcher.matches()) {
			javaVersion = matcher.group(1);
		}

		try {
			double v = Double.parseDouble(javaVersion);
			return v >= version;
		} catch (NumberFormatException e) { // NOSONAR
			return false;
		}
	}

	private static String makeDN(Map<String, String> certificateProeprties) {
		StringBuilder builder = new StringBuilder();

		if (certificateProeprties.get("CommonName") != null)
			builder.append("CN=" + certificateProeprties.get("CommonName")
					+ ", ");
		if (certificateProeprties.get("OrganizationName") != null)
			builder.append("O=" + certificateProeprties.get("OrganizationName")
					+ ", ");
		if (certificateProeprties.get("OrganizationUnitName") != null)
			builder.append("OU="
					+ certificateProeprties.get("OrganizationUnitName") + ", ");
		if (certificateProeprties.get("Location") != null)
			builder.append("L=" + certificateProeprties.get("Location") + ", ");
		if (certificateProeprties.get("StateName") != null)
			builder.append("ST=" + certificateProeprties.get("StateName")
					+ ", ");
		if (certificateProeprties.get("CountryName") != null)
			builder.append("C=" + certificateProeprties.get("CountryName")
					+ ", ");
		if (certificateProeprties.get("Email") != null)
			builder.append("emailAddress=" + certificateProeprties.get("Email")
					+ ", ");

		builder.delete(builder.length() - 2, builder.length());
		return builder.toString();
	}

	private static boolean[] getKeyUsgaeExtension(String keyusages) {
		boolean[] kueOk = new boolean[9];
		boolean isProvided = false;
		if (keyusages == null || keyusages.trim().length() == 0) {
			kueOk[0] = true;
			kueOk[2] = true;
			return kueOk;
		}

		for (String keyusage : keyusages.split(",")) {
			keyusage = keyusage.trim();
			if ("digitalSignature".equalsIgnoreCase(keyusage)) {
				kueOk[0] = true;
				isProvided = true;
			} else if ("nonRepudiation".equalsIgnoreCase(keyusage)) {
				kueOk[1] = true;
				isProvided = true;
			} else if ("keyEncipherment".equalsIgnoreCase(keyusage)) {
				kueOk[2] = true;
				isProvided = true;
			} else if ("dataEncipherment".equalsIgnoreCase(keyusage)) {
				kueOk[3] = true;
				isProvided = true;
			} else if ("keyAgreement".equalsIgnoreCase(keyusage)) {
				kueOk[4] = true;
				isProvided = true;
			} else if ("keyCertSign".equalsIgnoreCase(keyusage)) {
				kueOk[5] = true;
				isProvided = true;
			} else if ("cRLSign".equalsIgnoreCase(keyusage)) {
				kueOk[6] = true;
				isProvided = true;
			} else if ("encipherOnly".equalsIgnoreCase(keyusage)) {
				kueOk[7] = true;
				isProvided = true;
			} else if ("decipherOnly".equalsIgnoreCase(keyusage)) {
				kueOk[8] = true;
				isProvided = true;
			} else {
				throw new NAEException("invalid keyusage value: " + keyusage);
			}
		}

		if (!isProvided) {
			kueOk[0] = true;
			kueOk[2] = true;
		}
		return kueOk;
	}

	/**
	 * Read property file and store them in a map. It will not read a line start
	 * with and space.
	 **/
	private static Map<String, String> readPropertiesFrom(String fileName)
			throws IOException {
		Map<String, String> certificateProeprties = new HashMap<String, String>();
		BufferedReader buffReader = new BufferedReader(new FileReader(fileName));
		String buffer = null;
		while ((buffer = buffReader.readLine()) != null) {
			if (buffer.startsWith("#") || buffer.trim().length() == 0)
				continue;
			String[] temp = buffer.split("=");
			if (temp.length == 1)
				continue;
			certificateProeprties.put(temp[0], temp[1]);
		}
		buffReader.close();
		return certificateProeprties;
	}

	public static void usage() {
		System.err
				.println("java SelfSignedCertificateUtility [-user KeyManagerUserName] [-password KeyManagerPassword] -key rsaOrECCKeyName -file details.properties [-certPass certPassword]");
		System.exit(-1);
	}
}
//
