
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.security.KeyStore;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;
/*
 * This app provides a number of different helper methods dealing with CM Application Data Protection UserSets.  There is a method to find 
 * a user in a userset and another method to populate the userset from a flat file.  Usersets are typically used within
 * an access policy but they are not restricted to that usage. 
 * Was tested with CM 2.14
 * Note: This source code is only to be used for testing and proof of concepts.
 * @author mwarner
 * 
 */

public class CMUserSetHelper {

	static String hostnamevalidate = "yourhostname";

	String usersetid = "716f01a6-5cab-4799-925a-6dc2d8712fc1";
	String cmIP = "yourip";
	String apiUrlGetUsers = "https://" + cmIP + "/api/v1/data-protection/user-sets/" + usersetid + "/users?name=";
	// + username_in_userset;
	String addusertouserset = "https://" + cmIP + "/api/v1/data-protection/user-sets/" + usersetid + "/users";

	int totalrecords = 0;
	String authUrl = "https://" + cmIP + "/api/v1/auth/tokens";

	static boolean debug = true;
	int chunksize = 5;
	static int CHUNKSIZEMAX = 100;

	public CMUserSetHelper(String usersetid, String cmIP) {

		this.usersetid = usersetid;
		this.cmIP = cmIP;
		this.apiUrlGetUsers = "https://" + cmIP + "/api/v1/data-protection/user-sets/" + usersetid + "/users?name=";
		// this.apiUrlGetUsers = "https://" + cmIP +
		// "/api/v1/data-protection/user-sets/" + usersetid + "/users?limit=" +
		// this.usersetlimit + "&name=";
		this.addusertouserset = "https://" + cmIP + "/api/v1/data-protection/user-sets/" + usersetid + "/users";
		this.authUrl = "https://" + cmIP + "/api/v1/auth/tokens";
	}

	public static void main(String[] args) throws Exception {

		String username = args[0];
		String password = args[1];
		String cmip = args[2];
		String usersetid = args[3];
		String filePath = args[4];
		// CMUserSetHelper("716f01a6-5cab-4799-925a-6dc2d8712fc1","20.241.70.238");
		// CMUserSetHelper("32d89a8d-efac-4c50-9b53-f51d0c03413e",
		CMUserSetHelper cmusersetHelper = new CMUserSetHelper(usersetid, cmip);
		int totalrecords = 0;

		// String apiUrl = apiUrlGetUsers;
		String jwthtoken = geAuthToken(cmusersetHelper.authUrl, username, password);

		String newtoken = "Bearer " + removeQuotes(jwthtoken);

		// String filePath =
		// "C:\\Users\\t0185905\\workspace\\CT-VL-GCP\\src\\main\\java\\com\\example\\emailAddresses.txt";
		RandomAccessFile file = new RandomAccessFile(filePath, "r");
		if (cmusersetHelper.chunksize > CHUNKSIZEMAX)
			cmusersetHelper.chunksize = CHUNKSIZEMAX;
		int totoalnbrofrecords = numberOfLines(file);
		if (cmusersetHelper.chunksize > totoalnbrofrecords) {
			cmusersetHelper.chunksize = totoalnbrofrecords / 2;
		}
		totalrecords = cmusersetHelper.addAUserToUserSetFromFile(cmusersetHelper.addusertouserset, newtoken, filePath);
		System.out.println("Totalrecords inserted into Userset  " + cmusersetHelper.usersetid + " = " + totalrecords);

	}

	/**
	 * Returns an boolean if user found
	 * <p>
	 * 
	 * @param user     user to find
	 * @param newtoken jwt token to use
	 * @return boolean true if found in userset
	 * @throws CustomException
	 */
	public boolean findUserInUserSet(String user, String newtoken) throws CustomException {
		boolean found = false;

		String apiUrl = this.apiUrlGetUsers + user;

		apiUrl = removeQuotes(apiUrl);

		try {
			URL url = new URL(apiUrl);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			connection.setRequestMethod("GET");
			connection.setRequestProperty("Authorization", newtoken);
			connection.setRequestProperty("accept", "application/json");

			connection.setDoInput(true);
			BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));

			StringBuilder response = new StringBuilder();
			String line;
			while ((line = reader.readLine()) != null) {
				response.append(line);
			}
			reader.close();

			Gson gson = new Gson();
			if (debug)
				System.out.println("response " + response);
			JsonObject input = null;
			JsonElement total = null;
			JsonElement rootNode = JsonParser.parseString(response.toString()).getAsJsonObject();
			if (rootNode.isJsonObject()) {
				input = rootNode.getAsJsonObject();
				if (input.isJsonObject()) {
					total = input.get("total");
				}
			}
			JsonPrimitive column = total.getAsJsonPrimitive();
			String totalstr = column.getAsJsonPrimitive().toString();

			Integer i = Integer.valueOf(totalstr);

			if (i > 0) {
				found = true;

			}
			connection.disconnect();
		} catch (Exception e) {
			if (e.getMessage().contains("403")) {
				throw new CustomException("1002, User Not in Application Data Protection Clients ", 1002);
			} else
				e.printStackTrace();
		}

		return found;

	}

	/**
	 * Loads users from a file to the userset. Returns an int of number of users
	 * added.
	 * <p>
	 * 
	 * @param url      url to userset api
	 * @param newtoken jwt token to use
	 * @param filePath file to load
	 * @return int totalnumberofrecords added to userset
	 */

	public int addAUserToUserSetFromFile(String url, String newtoken, String filePath) throws IOException {

		int totalnbrofrecords = 0;
		try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
			String line;
			int count = 0;
			StringBuilder payloadBuilder = new StringBuilder();

			payloadBuilder.append("{\"users\": [");

			while ((line = br.readLine()) != null) {
				totalnbrofrecords++;
				// Append the email address to the payload
				payloadBuilder.append("\"").append(line).append("\",");
				count++;

				// If 'n' records have been read, print the payload
				if (count == chunksize) {
					makeCMCall(payloadBuilder, newtoken, url);
					// Reset payload builder and count for the next batch of records
					payloadBuilder = new StringBuilder("{\"users\": [");
					count = 0;
				}
			}

			// If there are remaining records, print the payload
			if (count > 0) {
				payloadBuilder.deleteCharAt(payloadBuilder.length() - 1); // Remove the trailing comma
				payloadBuilder.append("}");
				makeCMCall(payloadBuilder, newtoken, url);
				if (debug)
					System.out.println(payloadBuilder.toString());
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		return totalnbrofrecords;

	}

	/**
	 * Loads users from a file to the userset. Returns an int of number of users
	 * added.
	 * <p>
	 * 
	 * @param payloadBuilder payload for CM call that contains users to add
	 * @param newtoken       jwt token to use
	 * @param url            url to peform inserts
	 * @return int response code
	 */

	public static int makeCMCall(StringBuilder payloadBuilder, String newtoken, String url) throws IOException {

		payloadBuilder.deleteCharAt(payloadBuilder.length() - 1); // Remove the trailing comma
		payloadBuilder.append("]}");
		if (debug)
			System.out.println(payloadBuilder.toString());
		String payload = payloadBuilder.toString();

		// Create URL object
		URL apiUrl = new URL(url);
		// Create connection object
		HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
		connection.setRequestMethod("POST");
		connection.setRequestProperty("Content-Type", "application/json");
		connection.setDoOutput(true);
		connection.setRequestProperty("Authorization", newtoken);
		// Send request
		OutputStream outputStream = connection.getOutputStream();
		outputStream.write(payload.getBytes());
		outputStream.flush();
		outputStream.close();

		// Get response
		int responseCode = connection.getResponseCode();
		BufferedReader reader;
		if (responseCode >= 200 && responseCode < 300) {
			reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
		} else {
			reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
		}

		// Read response
		String lineresponse;
		StringBuilder response = new StringBuilder();
		while ((lineresponse = reader.readLine()) != null) {
			response.append(lineresponse);
		}
		reader.close();

		// Print response
		if (debug) {
			System.out.println("Response Code: " + responseCode);
			System.out.println("Response Body: " + response.toString());
		}
		// Disconnect connection
		connection.disconnect();
		// Reset payload builder and count for the next batch of records
		payloadBuilder = new StringBuilder("{\"users\": [");

		return responseCode;

	}

	/**
	 * Simple sample of showing how to load a couple of users to the userset.
	 * Returns an int of number of users added.
	 * <p>
	 * 
	 * @param url      url to userset api
	 * @param newtoken jwt token to use
	 *
	 * @return int response code
	 */
	public static int addAUserToUserSet(String url, String newtoken) throws IOException {
		boolean found = false;

		String payload = "{\"users\": [\"akhip@company.com\",\"user2@company.com\"]}";

		// Create URL object
		URL apiUrl = new URL(url);
		// Create connection object
		HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
		connection.setRequestMethod("POST");
		connection.setRequestProperty("Content-Type", "application/json");
		connection.setDoOutput(true);
		connection.setRequestProperty("Authorization", newtoken);
		// Send request
		OutputStream outputStream = connection.getOutputStream();
		outputStream.write(payload.getBytes());
		outputStream.flush();
		outputStream.close();

		// Get response
		int responseCode = connection.getResponseCode();
		BufferedReader reader;
		if (responseCode >= 200 && responseCode < 300) {
			reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
		} else {
			reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
		}

		// Read response
		String line;
		StringBuilder response = new StringBuilder();
		while ((line = reader.readLine()) != null) {
			response.append(line);
		}
		reader.close();

		// Print response
		if (debug) {
			System.out.println("Response Code: " + responseCode);
			System.out.println("Response Body: " + response.toString());
		}
		// Disconnect connection
		connection.disconnect();

		return responseCode;

	}

	public static String removeQuotes(String input) {

		// Remove double quotes from the input string
		input = input.replace("\"", "");

		return input;
	}

	private static int numberOfLines(RandomAccessFile file) throws IOException {
		int numberOfLines = 0;
		while (file.readLine() != null) {
			numberOfLines++;
		}
		file.seek(0);
		return numberOfLines;
	}

	/**
	 * Get JWT from CM
	 * <p>
	 * 
	 * @param apiUrl   url to CM auth
	 * @param username username on CM
	 * @param pwd      password on CM
	 * @return String jwt
	 */

	public static String geAuthToken(String apiUrl, String usernb, String pwd) throws Exception

	{

		String jStr = "{\"username\":\"" + usernb + "\",\"password\":\"" + pwd + "\"}";
		disableCertValidation();

		String totalstr = null;
		try {
			URL url = new URL(apiUrl);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			connection.setRequestProperty("Content-length", String.valueOf(jStr.length()));
			connection.setRequestProperty("Content-Type", "application/json");
			connection.setRequestMethod("GET");
			connection.setDoOutput(true);
			connection.setDoInput(true);
			DataOutputStream output = new DataOutputStream(connection.getOutputStream());
			output.writeBytes(jStr);
			output.close();
			BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			StringBuilder response = new StringBuilder();
			String line;
			while ((line = reader.readLine()) != null) {
				response.append(line);
			}
			reader.close();

			JsonObject input = null;
			JsonElement total = null;
			JsonElement rootNode = JsonParser.parseString(response.toString()).getAsJsonObject();
			if (rootNode.isJsonObject()) {
				input = rootNode.getAsJsonObject();
				if (input.isJsonObject()) {
					total = input.get("jwt");
				}
			}
			JsonPrimitive column = total.getAsJsonPrimitive();
			totalstr = column.getAsJsonPrimitive().toString();
			connection.disconnect();
		} catch (Exception e) {
			e.printStackTrace();
		}

		return totalstr;

	}

	/**
	 * Get JWT from CM
	 * <p>
	 * 
	 * @param apiUrl   url to CM auth
	 * @param username username on CM
	 * @param pwd      password on CM
	 * @return String jwt
	 */

	public static String geAuthToken(String apiUrl) throws Exception

	{

		String userName = System.getenv("CMUSER");
		String password = System.getenv("CMPWD");
		String jStr = "{\"username\":\"" + userName + "\",\"password\":\"" + password + "\"}";

		disableCertValidation();

		String totalstr = null;
		try {
			URL url = new URL(apiUrl);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			connection.setRequestProperty("Content-length", String.valueOf(jStr.length()));
			connection.setRequestProperty("Content-Type", "application/json");
			connection.setRequestMethod("GET");
			connection.setDoOutput(true);
			connection.setDoInput(true);
			DataOutputStream output = new DataOutputStream(connection.getOutputStream());
			output.writeBytes(jStr);
			output.close();
			BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			StringBuilder response = new StringBuilder();
			String line;
			while ((line = reader.readLine()) != null) {
				response.append(line);
			}
			reader.close();
			if (debug)
				System.out.println("response " + response);
			JsonObject input = null;
			JsonElement total = null;
			JsonElement rootNode = JsonParser.parseString(response.toString()).getAsJsonObject();
			if (rootNode.isJsonObject()) {
				input = rootNode.getAsJsonObject();
				if (input.isJsonObject()) {
					total = input.get("jwt");
				}
			}
			JsonPrimitive column = total.getAsJsonPrimitive();
			totalstr = column.getAsJsonPrimitive().toString();
			connection.disconnect();
		} catch (Exception e) {
			e.printStackTrace();
		}

		return totalstr;

	}

	public static void disableCertValidation() throws Exception {
		TrustManager[] trustAllCerts = new TrustManager[] { new X509TrustManager() {
			public java.security.cert.X509Certificate[] getAcceptedIssuers() {
				return null;
			}

			public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) {
			}

			public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) {
			}
		} };

		// Install the all-trusting trust manager
		try {
			SSLContext sc = SSLContext.getInstance("SSL");
			sc.init(null, trustAllCerts, new java.security.SecureRandom());
			HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
		} catch (Exception e) {
			e.printStackTrace();
		}

		// Create all-trusting host name verifier
		HostnameVerifier allHostsValid = new HostnameVerifier() {
			public boolean verify(String hostname, SSLSession session) {
				return true;
			}
		};

		// Install the all-trusting host verifier
		HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);
	}

}