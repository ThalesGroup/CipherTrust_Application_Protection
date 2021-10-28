package com.thales.cm.rest.cmhelper;

import java.io.IOException;
import java.security.KeyManagementException;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

import com.jayway.jsonpath.JsonPath;

import okhttp3.CipherSuite;
import okhttp3.ConnectionSpec;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import okhttp3.TlsVersion;

/* This example helper class simplifies the usage of REST calls to the Thales CipherTrust Manager by 
 * exposing a few API's that shield some of the complexities of the json formating.    
 * This examples also shows how to work with refresh token and use retry logic when jwt expires. 
 * JWT duration = 300 seconds
*  Handles 
*  1.) encrypt/decrypt for gcm,rsa,fpe.  (Note: RSA Decrypt returns values in base64 format)
*  2.) mac/macv
*  3.) sign/signv
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.1 & 2.2 
* Uses the okhttp3 4.7.2 library.
*     
 */
public class CipherTrustManagerHelper {
	String cmdebug = "0";

	public String token = null;
	public String key = null;
	public String cmipaddress;
	public String refreshtoken;
	public String keystorepwd;
	public String username;
	public String password;
	public String dataformat;

	public static final String endbracket = "}";
	public static final int digitblocklen = 56;
	public static final int alphablocklen = 32;
	public static final StringBuffer numberPattern = new StringBuffer(
			"01234567890123456789012345678901024567896743678905435678");
	public static final StringBuffer stringPattern = new StringBuffer("asdfghjklzxcvbnmqwertyuioplkjhgf");
	public static final StringBuffer combinedPattern = new StringBuffer("abcdefghijklmnopqrstuvwxyz012345");
	public static final String quote = "\"";
	public static final String comma = ",";
	public static final int wait = 60000;
	public static final int encoding_parameters_length = 11;
	public static final int version = 0;
	public static final String versiontag = "\"version\":";
	public static final String plaintexttag = "{\"plaintext\":";
	public static final String tag = "kBr5A0fbPjPg7lS1bB6wfw==";
	public static final String iv = "VCC3VwxWu6Z6jfQw";
	public static final String aadtag = "\"aad\":";
	public static final String padtag = "\"pad\":";
	public static final String rsapad = "\"oaep\"";
	public static final String idtag = "\"id\":";
	public static final String typetag = "\"type\":";
	public static final String name = "\"name\"";
	public static final String aad = "YXV0aGVudGljYXRl";
	public static final String ciphertexttag = "{\"ciphertext\":";
	public static final String tagtag = "\"tag\":";
	public static final String ivtag = "\"iv\":";
	public static final String modetag = "\"mode\":";
	public static final String filetagname = "etag:";
	public static final String filetagsep = "!";
	private static final String[] VALID_HOSTS = { "192.168.159.160", "192.168.1.25", "mwarner-win10" };
	public static final MediaType JSONOCTET = MediaType.get("application/octet-stream");
	public static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
	public static final MediaType JSONTXT = MediaType.get("text/plain");

	OkHttpClient client = getUnsafeOkHttpClient();

	public CipherTrustManagerHelper() {
		super();
		Map<String, String> env = System.getenv();
		// System.out.println("name of logger" + log.getName());
		// log.debug("this is a test");
		// log.info("this is a test");
		for (String envName : env.keySet()) {
			if (envName.equalsIgnoreCase("cmuserid")) {
				username = env.get(envName);
				if (cmdebug.equalsIgnoreCase("1"))
					System.out.println("cmuserid=" + username);
			} else if (envName.equalsIgnoreCase("cmpassword")) {
				password = env.get(envName);
				if (cmdebug.equalsIgnoreCase("1"))
					System.out.println("cmpassword=" + password);
			} else if (envName.equalsIgnoreCase("cmserver")) {
				cmipaddress = env.get(envName);
				if (cmdebug.equalsIgnoreCase("1"))
					System.out.println("cmserver=" + cmipaddress);
			} else if (envName.equalsIgnoreCase("cmkey")) {
				key = env.get(envName);
				if (cmdebug.equalsIgnoreCase("1"))
					System.out.println("cmkey=" + key);
			} else if (envName.equalsIgnoreCase("cmdataformat")) {
				dataformat = env.get(envName);
				if (cmdebug.equalsIgnoreCase("1"))
					System.out.println("cmdataformat=" + dataformat);
			} else if (envName.equalsIgnoreCase("cmdebug")) {
				cmdebug = env.get(envName);
				if (cmdebug.equalsIgnoreCase("1"))
					System.out.println("cmdebug=" + cmdebug);
			}
			if (cmdebug.equalsIgnoreCase("1"))
				System.out.format("%s=%s%n", envName, env.get(envName));
		}


	}

	private String posttext(String url, String text) throws IOException {
		RequestBody body = RequestBody.create(text, JSONTXT);
		Request request = new Request.Builder().url(url).post(body).addHeader("Authorization", "Bearer " + this.token)
				.addHeader("Accept", "text/plain").addHeader("Content-Type", "text/plain").build();
		try (Response response = client.newCall(request).execute()) {
			return response.body().string();
		}
	}

	private String poststream(String url, String json) throws IOException {
		RequestBody body = RequestBody.create(json, JSONOCTET);
		Request request = new Request.Builder().url(url).post(body).addHeader("Authorization", "Bearer " + this.token)
				.addHeader("Accept", "application/json").addHeader("Content-Type", "application/octet-stream").build();
		try (Response response = client.newCall(request).execute()) {
			return response.body().string();
		}
	}

	private String getjson(String url) throws IOException {
		Request request = new Request.Builder().url(url).method("GET", null)
				.addHeader("Authorization", "Bearer " + this.token).addHeader("Accept", "application/json")
				.addHeader("Content-Type", "application/json").build();
		try (Response response = client.newCall(request).execute()) {
			return response.body().string();
		}
	}

	private String postjson(String url, String json) throws IOException {
		RequestBody body = RequestBody.create(json, JSON);
		Request request = new Request.Builder().url(url).post(body).addHeader("Authorization", "Bearer " + this.token)
				.addHeader("Accept", "application/json").addHeader("Content-Type", "application/json").build();
		try (Response response = client.newCall(request).execute()) {
			return response.body().string();
		}
	}

	/**
	 * Returns an String that will be a JWT token to be used for REST calls
	 * based on the refresh token.
	 * <p>
	 * Note: This is using a Java KeyStore for authentication.
	 * 
	 * @param keystorepwd
	 *            password to the java keystore
	 * @param keystorelocation
	 *            location of javakeystore that contains certificates
	 * @return string JWT token
	 */

	public String getTokenFromRefresh(String keystorepwd, String keystorelocation) throws IOException {

		OkHttpClient client = getOkHttpClient(keystorepwd, this.cmipaddress, keystorelocation);
		MediaType mediaType = MediaType.parse("application/json");
		String grant_typetag = "{\"grant_type\":";
		String grant_type = "refresh_token";
		String refreshtokentag = "\"refresh_token\":";

		String authcall = grant_typetag + quote + grant_type + quote + comma + refreshtokentag + quote
				+ this.refreshtoken + quote + " }";

		RequestBody body = RequestBody.create(authcall, mediaType);
		Request request = new Request.Builder().url("https://" + this.cmipaddress + "/api/v1/auth/tokens")
				.method("POST", body).addHeader("Content-Type", "application/json").build();

		Response response = client.newCall(request).execute();
		String returnvalue = response.body().string();

		String jwt = JsonPath.read(returnvalue.toString(), "$.jwt").toString();

		return jwt;

	}

	/**
	 * Returns an String that will be a JWT token to be used for REST calls
	 * based on the refresh token.
	 * <p>
	 * Note: This is not using a Java KeyStore for authentication.
	 * 
	 * @return string JWT token
	 */

	public String getTokenFromRefresh() throws IOException {

		OkHttpClient client = getUnsafeOkHttpClient();
		MediaType mediaType = MediaType.parse("application/json");

		String grant_typetag = "{\"grant_type\":";
		String grant_type = "refresh_token";
		String refreshtokentag = "\"refresh_token\":";

		String authcall = grant_typetag + quote + grant_type + quote + comma + refreshtokentag + quote
				+ this.refreshtoken + quote + " }";

		RequestBody body = RequestBody.create(authcall, mediaType);
		Request request = new Request.Builder().url("https://" + this.cmipaddress + "/api/v1/auth/tokens")
				.method("POST", body).addHeader("Content-Type", "application/json").build();

		Response response = client.newCall(request).execute();
		String returnvalue = response.body().string();

		String jwt = JsonPath.read(returnvalue.toString(), "$.jwt").toString();

		return jwt;

	}

	/**
	 * Returns an String that will be a JWT token to be used for REST calls.
	 * <p>
	 * Note: This is using a Java KeyStore for authentication.
	 * 
	 * @param keystorepwd
	 *            password to the java keystore
	 * @param keystorelocation
	 *            location of javakeystore that contains certificates
	 * @return string JWT token
	 */
	public String getToken(String keystorepwd, String keystorelocation) throws IOException {

		this.keystorepwd = keystorepwd;
		OkHttpClient client = getOkHttpClient(keystorepwd, this.cmipaddress, keystorelocation);
		MediaType mediaType = MediaType.parse("application/json");

		String grant_typetag = "{\"grant_type\":";
		String grant_type = "password";
		String passwordtag = "\"password\":";
		String usernametag = "\"username\":";
		String labels = "\"labels\": [\"myapp\",\"cli\"]}";

		String authcall = grant_typetag + quote + grant_type + quote + comma + usernametag + quote + this.username
				+ quote + comma + passwordtag + quote + this.password + quote + comma + labels;

		RequestBody body = RequestBody.create(authcall, mediaType);
		Request request = new Request.Builder().url("https://" + this.cmipaddress + "/api/v1/auth/tokens")
				.method("POST", body).addHeader("Content-Type", "application/json").build();

		Response response = client.newCall(request).execute();
		String returnvalue = response.body().string();

		String jwt = JsonPath.read(returnvalue.toString(), "$.jwt").toString();
		this.refreshtoken = JsonPath.read(returnvalue.toString(), "$.refresh_token").toString();

		this.token = jwt;
		return jwt;

	}

	/**
	 * Returns an String that will be a JWT token to be used for REST calls.
	 * <p>
	 * Note: This is not using a Java KeyStore for authentication.
	 * 
	 * @return string JWT token
	 */
	public String getToken() throws IOException {

		OkHttpClient client = getUnsafeOkHttpClient();

		MediaType mediaType = MediaType.parse("application/json");

		String grant_typetag = "{\"grant_type\":";
		String grant_type = "password";
		String passwordtag = "\"password\":";
		String usernametag = "\"username\":";
		String labels = "\"labels\": [\"myapp\",\"cli\"]}";

		String authcall = grant_typetag + quote + grant_type + quote + comma + usernametag + quote + this.username
				+ quote + comma + passwordtag + quote + this.password + quote + comma + labels;
		//System.out.println("auth call " + authcall);
		RequestBody body = RequestBody.create(authcall, mediaType);
		
		Request request = new Request.Builder().url("https://" + this.cmipaddress + "/api/v1/auth/tokens")
				.method("POST", body).addHeader("Content-Type", "application/json").build();

		Response response = client.newCall(request).execute();
		String returnvalue = response.body().string();

		String jwt = JsonPath.read(returnvalue.toString(), "$.jwt").toString();
		this.refreshtoken = JsonPath.read(returnvalue.toString(), "$.refresh_token").toString();

		this.token = jwt;
		return jwt;

	}

	private static KeyStore readKeyStore(String keystorepwd, String keystorelocation)
			throws KeyStoreException, NoSuchAlgorithmException, CertificateException, IOException {
		KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());

		char[] password = keystorepwd.toCharArray();
		java.io.FileInputStream fis = null;
		try {

			fis = new java.io.FileInputStream(keystorelocation);
			ks.load(fis, password);
		} finally {
			if (fis != null) {
				fis.close();
			}
		}
		return ks;
	}

	private static OkHttpClient getOkHttpClient(String pwd, String keymgrhostname, String keystorelocation) {

		try {
			TrustManagerFactory trustManagerFactory = TrustManagerFactory
					.getInstance(TrustManagerFactory.getDefaultAlgorithm());

			trustManagerFactory.init(readKeyStore(pwd, keystorelocation));

			X509TrustManager trustManager = (X509TrustManager) trustManagerFactory.getTrustManagers()[0];
			SSLContext sslContext = SSLContext.getInstance("TLS");
			sslContext.init(null, new TrustManager[] { trustManager }, null);
			java.security.cert.X509Certificate[] xcerts = trustManager.getAcceptedIssuers();

			for (int i = 0; i < xcerts.length; i++) {
				System.out.println(xcerts[i].getSigAlgName());
				System.out.println(xcerts[i].getType());
				// System.out.println(xcerts[i].getIssuerAlternativeNames().toString());
				System.out.println(xcerts[i].getIssuerDN().getName());
				System.out.println(xcerts[i].getSubjectDN().getName());
				System.out.println(xcerts[i].getPublicKey().getFormat().getBytes().toString());
				System.out.println(xcerts[i].getSerialNumber());
			}
			return new OkHttpClient.Builder().hostnameVerifier((hostname, session) -> {
				HostnameVerifier hv = HttpsURLConnection.getDefaultHostnameVerifier();
				/*
				 * Never return true without verifying the hostname, otherwise
				 * you will be vulnerable to man in the middle attacks.
				 */
				boolean okhost = false;

				for (int i = 0; i < VALID_HOSTS.length; i++) {
					if (VALID_HOSTS[i].equalsIgnoreCase(keymgrhostname)) {
						okhost = true;
						break;
					}
				}
				return okhost;
			}).sslSocketFactory(sslContext.getSocketFactory(), trustManager).build();

		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		} catch (KeyStoreException e) {
			e.printStackTrace();
		} catch (KeyManagementException e) {
			e.printStackTrace();
		} catch (Exception e) {
			e.printStackTrace();
		}

		return null;
	}

	 public static OkHttpClient.Builder enableTls12OVersion(OkHttpClient okHttpClient) {
		  OkHttpClient.Builder client = okHttpClient.newBuilder();
		  try {
		   SSLContext sc = SSLContext.getInstance("TLSv1.2");
		   sc.init(null, null, null);
		   //sslSocketFactory = sc.getSocketFactory();
		   // client.sslSocketFactory(new Tls12SocketFactory(sc.getSocketFactory()));
		   client.sslSocketFactory(sc.getSocketFactory());
		   ConnectionSpec connectionSpec = new ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
		     .tlsVersions(TlsVersion.TLS_1_2, TlsVersion.TLS_1_1, TlsVersion.TLS_1_0).cipherSuites(
	                    CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
	                    CipherSuite.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
	                    CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,
	                    CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA).build();
		   List<ConnectionSpec> specs = new ArrayList<>();
		   specs.add(connectionSpec);
		   specs.add(ConnectionSpec.COMPATIBLE_TLS);
		   specs.add(ConnectionSpec.CLEARTEXT);
		   client.connectionSpecs(specs);
		  } catch (Exception exc) {
		   exc.printStackTrace();
		  }
		  return client;
		 }


	private static OkHttpClient getUnsafeOkHttpClient() {
		try {
			// Create a trust manager that does not validate certificate chains
			final TrustManager[] trustAllCerts = new TrustManager[] { new X509TrustManager() {
				@Override
				public void checkClientTrusted(java.security.cert.X509Certificate[] chain, String authType)
						throws CertificateException {
				}

				@Override
				public void checkServerTrusted(java.security.cert.X509Certificate[] chain, String authType)
						throws CertificateException {
				}

				@Override
				public java.security.cert.X509Certificate[] getAcceptedIssuers() {
					return new java.security.cert.X509Certificate[] {};
				}
			} };

			// Install the all-trusting trust manager
			final SSLContext sslContext = SSLContext.getInstance("TLSv1.2");
			//final SSLContext sslContext = SSLContext.getInstance("SSL");
			sslContext.init(null, trustAllCerts, new java.security.SecureRandom());
			// Create an ssl socket factory with our all-trusting manager
			final SSLSocketFactory sslSocketFactory = sslContext.getSocketFactory();
//https://stackoverflow.com/questions/49980508/okhttp-sslhandshakeexception-ssl-handshake-aborted-failure-in-ssl-library-a-pro
//https://square.github.io/okhttp/https/		
			OkHttpClient.Builder builder = new OkHttpClient.Builder();
			
			builder.sslSocketFactory(sslSocketFactory, (X509TrustManager) trustAllCerts[0]);
			builder.hostnameVerifier(new HostnameVerifier() {
			
				@Override
				public boolean verify(String hostname, SSLSession session) {
					return true;
				}
			});

			OkHttpClient okHttpClient = builder.build();
			return okHttpClient;
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	/**
	 * Will loop thru n number of times to test basic functionality for the
	 * various methods implemented. See parameters below and examples for more
	 * details.
	 * <p>
	 * Examples: keyholder pwd MyAESEncryptionKey26 5 fpe 192.168.159.160
	 * encrypt digit keyholder pwd myrsa-pub 5 rsa 192.168.159.160 encrypt
	 * alphabet keyholder pwd myrsa-pub 5 rsa 192.168.159.160 encrypt
	 * alphanumeric admin pwd! MyAESEncryptionKey26 10 fpe 192.168.159.160
	 * encrypt digit admin pwd! hmacsha256-1 1 na 192.168.159.160 mac alphabet
	 * admin pwd! rsa-key5 1 na 192.168.159.160 sign alphabet
	 *
	 * @param userid
	 *            the userid must be granted access to the key in CM.
	 * @param password
	 *            the password of the user.
	 * @param key
	 *            the key to be used. (Must be key name)
	 * @param iterations
	 *            number of iterations to run. (Will use 25 bytes of random
	 *            data)
	 * @param encmode
	 *            fpe,rsa,gcm,na
	 * @param ciphertrustip
	 *            ciphertrust manger ip address
	 * @param action
	 *            encrypt/decrypt/mac/macv/sign/signv
	 * @param typeofdata
	 *            digit/alphabet/alphanumeric
	 */

	public static void main(String[] args) throws Exception {

		if (args.length != 8) {
			System.err.println(
					"Usage: java CipherTrustManagerHelper2  userid pwd keyname iterations mode ciphertrustip [encrypt/decrypt/mac/macv/sign/signv] [digit/alphabet/alphanumeric] ");
			System.exit(-1);
		}

		CipherTrustManagerHelper awsresrest = new CipherTrustManagerHelper();
		awsresrest.username = args[0];
		awsresrest.password = args[1];
		awsresrest.key = args[2];
		int numberofrecords = Integer.parseInt(args[3]);
		awsresrest.cmipaddress = args[5];
		String action = args[6];
		String typeofdata = args[7];

		if (typeofdata.equalsIgnoreCase("digit"))
			awsresrest.dataformat = "digit";
		else if (typeofdata.equalsIgnoreCase("alphabet"))
			awsresrest.dataformat = "alphabet";
		else if (typeofdata.equalsIgnoreCase("alphanumeric"))
			awsresrest.dataformat = "alphanumeric";
		else
			throw new RuntimeException("valid values for data type are: digit,alphabet,alphanumeric");

		// String tkn = awsresrest.getToken("Vormetric123!",
		// "C:\\keystore\\cm_keystoreone");
		String tkn = awsresrest.getToken();
		Calendar calendar = Calendar.getInstance();

		// Get start time (this needs to be a global variable).
		Date startDate = calendar.getTime();
		System.out.println("key size is = " + awsresrest.getKeySize());
		// awsresrest.loop(args[4], numberofrecords, action);

		Calendar calendar2 = Calendar.getInstance();

		// Get start time (this needs to be a global variable).
		Date endDate = calendar2.getTime();
		long sumDate = endDate.getTime() - startDate.getTime();
		System.out.println("Total time " + sumDate);
	}

	/**
	 * Returns an String that will either be a signed value or the string true
	 * or false.
	 * <p>
	 * Examples: awsresrest.cmRESTSign( "SHA1", "na",
	 * "BGYUO07R7EBKYYMNGAIUAUPSJ","sign"); awsresrest.cmRESTSign( "SHA1",
	 * "15e7eb8f1b0278583d71789a7aea05cbe1a041b2313f54c43f14a0c62b628175ece14bcfdecd47637049",
	 * "BGYUO07R7EBKYYMNGAIUAUPSJ","signv");
	 *
	 * @param hashAlgo
	 *            the hash algorithum to be used. (SHA1, SHA-256, SHA-512,etc)
	 * @param signature
	 *            the signature or na
	 * @param data
	 *            the data to be signed
	 * @param action
	 *            sign or signv.
	 * @return either be a signed value or the string true or false
	 */

	public String cmRESTSign(String hashAlgo, String signature, String data, String action) throws Exception {

		String value = null;
		int keysize = this.getKeySize() / 8;

		if (hashAlgo.equalsIgnoreCase("none") && data.length() > (keysize - encoding_parameters_length)) {
			throw new RuntimeException(
					"When using none for hashAlgo data size must be smaller than (keysize - encoding parm length)");

		}

		value = sign(hashAlgo, signature, data, action);

		return value;

	}

	/**
	 * Returns an String that will either be a hash a value or the string true
	 * or false.
	 * <p>
	 * Examples: awsresrest.cmRESTMac( "na", "TIW58B91G25V3FN27491ACCTY","mac");
	 * awsresrest.cmRESTMac("7c8842d207c1d73d21ae47b82cc18e6b03c48ef9ff1c3d27c5ccf2aa3d79f21e",
	 * "TIW58B91G25V3FN27491ACCTY","macv");
	 *
	 * @param hash
	 *            the hash value must be either "na" or the actual hash value.
	 * @param data
	 *            the data to be hashed
	 * @param action
	 *            mac or macv.
	 * @return either be a hash a value or the string true or false
	 */

	public String cmRESTMac(String hash, String data, String action) throws Exception {

		String value = null;

		value = mac(hash, data, action);

		return value;

	}

	/**
	 * Returns an String that will either be a be encrypted data or ciphertext.
	 * Notes: 1.) when using rsa the key must be keyname of public key: example
	 * rsakey-pub 2.) RSA Decrpyt will return values in base64 format. 3.) When
	 * using gcm first part of encrypted data will include a tag and the tag
	 * value
	 * <p>
	 * Examples: awsresrest.cmRESTProtect( "gcm", text, "decrypt");
	 * awsresrest.cmRESTProtect( "gcm", text, "encrypt");
	 * awsresrest.cmRESTProtect( "rsa", text, "encrypt");
	 * awsresrest.cmRESTProtect( "fpe", text, "encrypt");
	 *
	 * @param encmode
	 *            the encryption mode to be used for encryption or decrypt.
	 * @param data
	 *            the data to be encrypted or the ciphertext in case of decrypt.
	 * @param action
	 *            encrypt or decrypt.
	 * @return either be encrypted data or ciphertext
	 */

	public String cmRESTProtect(String encmode, String data, String action) throws Exception {

		String value = null;

		if (action.equalsIgnoreCase("encrypt")) {
			value = encrypt(encmode, data, action);
		} else if (action.equalsIgnoreCase("decrypt")) {
			value = decrypt(encmode, data, action);
		} else {
			System.out.println("Invalid action...... ");

		}
		return value;

	}

	private void loop(String encmode, int nbrofrecords, String action) throws Exception {
		String sensitive = null;
		String value;

		for (int i = 1; i <= nbrofrecords; i++) {
			if (this.dataformat.equalsIgnoreCase("digit"))
				sensitive = randomNumeric(25);
			else if (this.dataformat.equalsIgnoreCase("alphabet"))
				sensitive = randomAlpha(25);
			else
				sensitive = randomAlphaNumeric(25);
			System.out.println("original value = " + sensitive);
			if (action.equalsIgnoreCase("encrypt")) {

				value = this.cmRESTProtect(encmode, sensitive, action);
				System.out.println("return value from enc " + value);

				value = this.cmRESTProtect(encmode, value, "decrypt");
				System.out.println("return value from decrypt " + value);
				System.out.println("----------------------------------- ");
				// Following code is to test the refresh token logic

				/*
				 * Thread.sleep(wait); System.out.println( "Thread '" +
				 * Thread.currentThread().getName() +
				 * "' is woken after sleeping for " + wait + " mseconds");
				 */
			} else if (action.equalsIgnoreCase("mac")) {
				// admin Vormetric123! hmacsha256-1 1
				// 2c6e43fbf1bcf89ed75ee69280e5f53e78ffe8fb5591d1660d081a8613cf1f10
				// 192.168.159.160 mac
				// admin Vormetric123! rsa-key5 1
				// 2c6e43fbf1bcf89ed75ee69280e5f53e78ffe8fb5591d1660d081a8613cf1f10
				// 192.168.159.160 sign
				value = this.cmRESTMac("na", sensitive, action);
				System.out.println("mac " + value);
				value = this.cmRESTMac(value, sensitive, "macv");
				System.out.println("verify " + value);

			}
			// String hashAlgo , String signature ,String data, String action
			else if (action.equalsIgnoreCase("sign")) {
				value = this.cmRESTSign("SHA1", "na", sensitive, action);
				System.out.println("sign " + value);
				value = this.cmRESTSign("SHA1", value, sensitive, "signv");
				System.out.println("verify " + value);

			} else
				throw new RuntimeException("Invalid action code, valid values are:  encrypt,sign,mac");
		}

	}

	private String buildSignVerifyURL(String hashAlgo, String signature, String action) {
		String url = null;
		if (action.equals("sign")) {
			url = "https://" + this.cmipaddress + "/api/v1/crypto/sign?keyName=" + this.key + "&hashAlgo=" + hashAlgo;

		} else if (action.equals("signv")) {
			url = "https://" + this.cmipaddress + "/api/v1/crypto/signv?keyName=" + this.key + "&hashAlgo=" + hashAlgo
					+ "&signature=" + signature;

		} else {
			System.out.println("invalid action.... ");
		}

		return url;
	}

	private String buildURL() {
		String url = null;
		url = "https://" + this.cmipaddress + "/api/v1/vault/keys2/" + this.key;

		return url;
	}

	private String buildURL(String hash, String action) {
		String url = null;
		if (action.equals("mac")) {
			url = "https://" + this.cmipaddress + "/api/v1/crypto/mac?keyName=" + this.key;

		} else if (action.equals("macv")) {
			url = "https://" + this.cmipaddress + "/api/v1/crypto/macv?keyName=" + this.key + "&hash=" + hash;

		} else
			System.out.println("invalid action.... ");
		return url;
	}

	private String buildURL(String encmode, String sensitive, String action) {

		String hint = this.dataformat;

		String url = null;
		if (action.equalsIgnoreCase("encrypt")) {
			if (encmode.equals("fpe")) {
				if (hint.equalsIgnoreCase("digit") && sensitive.length() > digitblocklen)
					url = "https://" + this.cmipaddress + "/api/v1/crypto/hide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint + "&iv=" + numberPattern;
				else if (hint.equalsIgnoreCase("alphabet") && sensitive.length() > alphablocklen)
					url = "https://" + this.cmipaddress + "/api/v1/crypto/hide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint + "&iv=" + stringPattern;
				else if (hint.equalsIgnoreCase("alphanumeric") && sensitive.length() > alphablocklen)
					url = "https://" + this.cmipaddress + "/api/v1/crypto/hide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint + "&iv=" + combinedPattern;
				else
					url = "https://" + this.cmipaddress + "/api/v1/crypto/hide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint;
			} else {
				url = "https://" + this.cmipaddress + "/api/v1/crypto/encrypt";

			}
		} else if (action.equalsIgnoreCase("decrypt")) {
			if (encmode.equals("fpe")) {
				if (hint.equalsIgnoreCase("digit") && sensitive.length() > digitblocklen)
					url = "https://" + this.cmipaddress + "/api/v1/crypto/unhide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint + "&iv=" + numberPattern;
				else if (hint.equalsIgnoreCase("alphabet") && sensitive.length() > alphablocklen)
					url = "https://" + this.cmipaddress + "/api/v1/crypto/unhide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint + "&iv=" + stringPattern;
				else if (hint.equalsIgnoreCase("alphanumeric") && sensitive.length() > alphablocklen)
					url = "https://" + this.cmipaddress + "/api/v1/crypto/unhide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint + "&iv=" + combinedPattern;
				else
					url = "https://" + this.cmipaddress + "/api/v1/crypto/unhide2?keyName=" + this.key + "&version="
							+ version + "&hint=" + hint;
			} else {
				url = "https://" + this.cmipaddress + "/api/v1/crypto/decrypt";

			}
		} else {

			System.out.println("invalid mode action provided ");

		}
		// System.out.println("url is " + url);
		return url;
	}

	private String getBody(String encmode, String sensitive, String action, String enctag) {

		String body = null;

		body = ciphertexttag + quote + sensitive + quote + comma + tagtag + quote + enctag + quote + comma + modetag
				+ quote + encmode + quote + comma + idtag + quote + this.key + quote + comma + ivtag + quote + iv
				+ quote + comma + aadtag + quote + aad + quote + endbracket;

		return body;
	}

	private String getBody(String encmode, String sensitive, String action) {

		String body = null;
		if (action.equalsIgnoreCase("encrypt")) {
			if (encmode.equals("fpe")) {
				body = sensitive;
			} else if (encmode.equals("rsa")) {
				byte[] dataBytes = sensitive.getBytes();
				String plaintextbase64 = Base64.getEncoder().encodeToString(dataBytes);
				body = plaintexttag + quote + plaintextbase64 + quote + comma + idtag + quote + this.key + quote
						+ endbracket;

			} else {
				byte[] dataBytes = sensitive.getBytes();
				String plaintextbase64 = Base64.getEncoder().encodeToString(dataBytes);
				body = plaintexttag + quote + plaintextbase64 + quote + comma + modetag + quote + encmode + quote
						+ comma + idtag + quote + this.key + quote + comma + ivtag + quote + iv + quote + comma + aadtag
						+ quote + aad + quote + endbracket;
			}

		} else {
			if (encmode.equals("fpe")) {
				body = sensitive;
			} else if (encmode.equals("rsa")) {
				/*
				 * byte[] dataBytes = sensitive.getBytes(); String
				 * plaintextbase64 =
				 * Base64.getEncoder().encodeToString(dataBytes);
				 */
				// This example only works with passing in the public key name
				// for RSA keys.
				String keyprivate = this.key.substring(0, this.key.length() - 4);
				body = ciphertexttag + quote + sensitive + quote + comma + idtag + quote + keyprivate + quote + comma
						+ typetag + name + comma + padtag + rsapad + endbracket;

			} else {

				body = ciphertexttag + quote + sensitive + quote + comma + modetag + quote + encmode + quote + comma
						+ idtag + quote + this.key + quote + comma + ivtag + quote + iv + quote + comma + aadtag + quote
						+ aad + quote + endbracket;

			}
		}
		// System.out.println(body);
		return body;
	}

	public int getKeySize() throws IOException {
		String results = null;
		int size = 0;
		results = this.getjson(buildURL());

		// System.out.println("value " + results);
		try {
			if (results.contains("Token is expired")) {
				System.out.println("get new token");
				this.token = getTokenFromRefresh();
				// Retry logic call post again.

				results = this.getjson(buildURL());
			}
			if (results.contains("Resource not found")) {
				System.out.println("Key not found");

			} else {
				results = JsonPath.read(results.toString(), "$.size").toString();
				Integer bigIntSize = new Integer(results);
				size = bigIntSize.intValue();
			}
			// System.out.println("key size = " + size);
		} catch (Exception e) {

			System.out.println(e.getMessage());

			String code = JsonPath.read(results.toString(), "$.code").toString();
			String msg = JsonPath.read(results.toString(), "$.codeDesc").toString();
			System.out.println("code " + code);
			System.out.println("code desc  " + msg);
			StackTraceElement[] ste = e.getStackTrace();
			for (int j = 0; j < ste.length; j++) {
				System.out.println(ste[j]);

			}

			System.exit(-1);
		}

		return size;

	}

	private String sign(String hashAlgo, String signature, String sensitive, String action) throws Exception {

		String returnvalue = null;
		String ciphertext = null;
		String results = null;
		results = this.poststream(buildSignVerifyURL(hashAlgo, signature, action), sensitive);

		System.out.println("value " + results);
		try {
			if (results.contains("Token is expired")) {
				System.out.println("get new token");
				this.token = getTokenFromRefresh();
				// Retry logic call post again.

				results = this.poststream(buildSignVerifyURL(hashAlgo, signature, action), sensitive);
			}
			if (action.equals("sign")) {
				results = JsonPath.read(results.toString(), "$.data").toString();
				returnvalue = results;
			} else {
				ciphertext = JsonPath.read(results.toString(), "$.verified").toString();
				returnvalue = ciphertext;
			}
			// System.out.println("cipher text = " + ciphertext);
		} catch (Exception e) {

			System.out.println(e.getMessage());

			String code = JsonPath.read(results.toString(), "$.code").toString();
			String msg = JsonPath.read(results.toString(), "$.codeDesc").toString();
			System.out.println("code " + code);
			System.out.println("code desc  " + msg);
			StackTraceElement[] ste = e.getStackTrace();
			for (int j = 0; j < ste.length; j++) {
				System.out.println(ste[j]);

			}

			System.exit(-1);
		}

		return returnvalue;
	}

	private String mac(String hash, String sensitive, String action) throws Exception {

		String returnvalue = null;
		String ciphertext = null;
		String results = null;
		results = this.poststream(buildURL(hash, action), sensitive);

		System.out.println("value " + results);
		try {
			if (results.contains("Token is expired")) {
				System.out.println("get new token");
				this.token = getTokenFromRefresh();
				// Retry logic call post again.

				results = this.postjson(buildURL(hash, action), sensitive);
			}
			if (action.equals("mac")) {
				results = JsonPath.read(results.toString(), "$.data").toString();
				returnvalue = results;
			} else {
				ciphertext = JsonPath.read(results.toString(), "$.verified").toString();
				returnvalue = ciphertext;
			}
			// System.out.println("cipher text = " + ciphertext);
		} catch (Exception e) {

			System.out.println(e.getMessage());

			String code = JsonPath.read(results.toString(), "$.code").toString();
			String msg = JsonPath.read(results.toString(), "$.codeDesc").toString();
			System.out.println("code " + code);
			System.out.println("code desc  " + msg);
			StackTraceElement[] ste = e.getStackTrace();
			for (int j = 0; j < ste.length; j++) {
				System.out.println(ste[j]);

			}

			System.exit(-1);
		}

		return returnvalue;
	}

	private String decrypt(String encmode, String sensitive, String action) throws Exception {

		String returnvalue = null;
		String ciphertext = null;
		String enctag = null;
		String results = null;
		if (encmode.equals("fpe"))
			results = this.posttext(buildURL(encmode, sensitive, action), sensitive);
		else {
			if (sensitive.startsWith(filetagname)) {
				String str = sensitive.substring(filetagname.length() - 1);
				String parts[] = str.split(filetagsep);
				enctag = parts[0].replace(":", "");
				sensitive = parts[1];
				results = this.postjson(buildURL(encmode, sensitive, action),
						this.getBody(encmode, sensitive, action, enctag));
			} else {
				results = this.postjson(buildURL(encmode, sensitive, action), getBody(encmode, sensitive, action));
			}
		}
		// System.out.println("value " + results);
		try {
			if (results.contains("Token is expired")) {
				System.out.println("get new token");
				this.token = getTokenFromRefresh();
				// Retry logic call post again.

				if (encmode.equals("fpe"))
					results = this.posttext(buildURL(encmode, sensitive, action), sensitive);
				else {
					if (sensitive.startsWith(filetagname)) {
						String str = sensitive.substring(filetagname.length() - 1);
						String parts[] = str.split(filetagsep);
						enctag = parts[0];
						sensitive = parts[1];

						results = this.postjson(buildURL(encmode, sensitive, action),
								getBody(encmode, sensitive, action, enctag));
					} else {
						results = this.postjson(buildURL(encmode, sensitive, action),
								getBody(encmode, sensitive, action));
					}
				}
			}

			if (encmode.equals("fpe")) {
				results = JsonPath.read(results.toString(), "$.data").toString();
				returnvalue = results;
			} else if (encmode.equals("rsa")) {
				// byte[] bytes = results.getBytes("UTF-8");
				// byte[] decoded = Base64.getDecoder().decode(bytes);
				// System.out.println("orgi value new " + new String(decoded));

				// String plaintextbase64 = results.toString();
				// byte[] decryoriginaldata =
				// Base64.getDecoder().decode(plaintextbase64);
				// returnvalue = new String(new String(decoded));
				returnvalue = results;

			} else {
				String plaintextbase64 = JsonPath.read(results.toString(), "$.plaintext").toString();
				byte[] decryoriginaldata = Base64.getDecoder().decode(plaintextbase64);
				returnvalue = new String(decryoriginaldata);

			}
			// System.out.println("cipher text = " + ciphertext);
		} catch (Exception e) {
			// TODO: handle exception
			System.out.println(e.getMessage());
			if (!encmode.equals("rsa")) {
				String code = JsonPath.read(results.toString(), "$.code").toString();
				String msg = JsonPath.read(results.toString(), "$.codeDesc").toString();
				System.out.println("code " + code);
				System.out.println("code desc  " + msg);
				StackTraceElement[] ste = e.getStackTrace();
				for (int j = 0; j < ste.length; j++) {
					System.out.println(ste[j]);

				}
			}
			System.exit(-1);
		}

		return returnvalue;

	}

	private String encrypt(String encmode, String sensitive, String action) throws Exception {

		String returnvalue = null;
		String ciphertext = null;
		String results = null;
		if (encmode.equals("fpe"))
			results = this.posttext(buildURL(encmode, sensitive, action), sensitive);
		else
			results = this.postjson(buildURL(encmode, sensitive, action), getBody(encmode, sensitive, action));

		//System.out.println("value " + results);
		try {
			if (results.contains("Token is expired")) {
				System.out.println("get new token");
				this.token = getTokenFromRefresh();
				// Retry logic call post again.

				if (encmode.equals("fpe"))
					results = this.posttext(buildURL(encmode, sensitive, action), sensitive);
				else
					results = this.postjson(buildURL(encmode, sensitive, action), getBody(encmode, sensitive, action));

			}

			if (encmode.equals("fpe")) {
				ciphertext = JsonPath.read(results.toString(), "$.data").toString();
				returnvalue = ciphertext;
			} else if (encmode.equals("rsa")) {
				ciphertext = JsonPath.read(results.toString(), "$.ciphertext").toString();
				returnvalue = ciphertext;

			} else {
				ciphertext = JsonPath.read(results.toString(), "$.ciphertext").toString();
				String tagtext = JsonPath.read(results.toString(), "$.tag").toString();
				returnvalue = filetagname + tagtext + filetagsep + ciphertext;

			}
			// System.out.println("cipher text = " + ciphertext);
		} catch (Exception e) {
			// TODO: handle exception
			System.out.println(e.getMessage());

			String code = JsonPath.read(results.toString(), "$.code").toString();
			String msg = JsonPath.read(results.toString(), "$.codeDesc").toString();
			System.out.println("code " + code);
			System.out.println("code desc  " + msg);
			StackTraceElement[] ste = e.getStackTrace();
			for (int j = 0; j < ste.length; j++) {
				System.out.println(ste[j]);

			}

			System.exit(-1);
		}

		return returnvalue;

	}

	private static boolean isNumeric(String str) {
		for (char c : str.toCharArray()) {

			if (!Character.isDigit(c)) {
				return false;
			}
		}
		return true;
	}

	private static boolean isAlpha(String str) {

		for (char c : str.toCharArray()) {
			if (!Character.isAlphabetic(c)) {
				// if (!Character.isLetter(c)) {
				return false;
			}
		}
		return true;

	}

	private static String getSCUnique(String name) {
		StringBuffer returnvalue = new StringBuffer();
		HashMap hm = new HashMap();
		String specialCharacters = " !#$%&'()*+,-./:;<=>?@[]^_`{|}~";
		String str2[] = name.split("");
		int count = 0;
		for (int i = 0; i < str2.length; i++) {
			if (specialCharacters.contains(str2[i])) {
				count++;
				hm.put(str2[i], str2[i]);
			}
		}

		Set set = hm.entrySet();
		Iterator i = set.iterator();

		// Display elements
		while (i.hasNext()) {
			Map.Entry me = (Map.Entry) i.next();
			returnvalue.append(me.getKey());
		}

		return returnvalue.toString();
	}

	private static final String ALPHA_NUMERIC_STRING = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
	private static final String ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

	private static String randomAlpha(int count) {
		StringBuilder builder = new StringBuilder();
		while (count-- != 0) {
			int character = (int) (Math.random() * ALPHA.length());
			builder.append(ALPHA.charAt(character));
		}
		return builder.toString();
	}

	private static String randomAlphaNumeric(int count) {
		StringBuilder builder = new StringBuilder();
		while (count-- != 0) {
			int character = (int) (Math.random() * ALPHA_NUMERIC_STRING.length());
			builder.append(ALPHA_NUMERIC_STRING.charAt(character));
		}
		return builder.toString();
	}

	private static final String NUMERIC_STRING = "0123456789";

	private static String randomNumeric(int count) {
		StringBuilder builder = new StringBuilder();
		while (count-- != 0) {
			int character = (int) (Math.random() * NUMERIC_STRING.length());
			builder.append(NUMERIC_STRING.charAt(character));
		}
		return builder.toString();
	}

}
