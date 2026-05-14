package com.example;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes.
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

/**
 * This sample shows how to use the protect/reveal REST API using both the regular protect and the protectbulk.
 * 
 */
public class CRDPBulkOperation {

	private static int BATCHLIMIT = 5000;

	public static void main(String[] args) throws Exception {

		String crdp_container_IP = "192.168.159.143";
		int batchsize = 2;
		String protectURL = "http://" + crdp_container_IP + ":8090/v1/protect";
		boolean debug = false;

		String protection_profile = "plain-nbr-internal";
		String modeofoperation = "regular";

		if (!args[0].contains("null")) {
			debug = args[0].equalsIgnoreCase("true");
		}

		if (!args[1].contains("null")) {
			modeofoperation = args[1];
		}
		if (modeofoperation.equalsIgnoreCase("bulk"))
			protectURL = protectURL + "bulk";

		int index = 0;
		int totalrecords = 0;
		int recordcnter = 0;
		long startTime = System.currentTimeMillis();
		int nbrofchunks = 0;

		//emp-id1k.txt, emp-id5k.txt,emp-nbr-smallout.txt
		String filePath = "C:\\data\\emp-nbr-smallout.txt"; // Change



		if (modeofoperation.equalsIgnoreCase("regular")) {
			totalrecords = protectFromFile(protectURL, debug, filePath, protection_profile);
			nbrofchunks = 1;
		} else {
			List<String> strings = readStringsFromFile(filePath);
			int totalnumberofrecords = strings.size();
			int recordsleft = totalnumberofrecords;

			List<String> batchnnn = new ArrayList<>();
			startTime = System.currentTimeMillis();

			if (batchsize > totalnumberofrecords)
				batchsize = totalnumberofrecords;
			if (batchsize >= BATCHLIMIT)
				batchsize = BATCHLIMIT;

			while (index < totalnumberofrecords) {

				for (int i = 0; i < batchsize && index < totalnumberofrecords; i++) {
					batchnnn.add(strings.get(recordcnter));
					recordcnter++;
					index++;
					recordsleft--;

				}

				totalrecords = totalrecords + protectFromFileBulk(protectURL, debug, batchnnn, batchsize, index,
						totalnumberofrecords, recordsleft, protection_profile);
				batchnnn = new ArrayList<>();
				nbrofchunks++;

			}
		}

		long endTime = System.currentTimeMillis();
		long totalTime = endTime - startTime;
		System.out.println("Time taken CDRP test: " + totalTime + " milliseconds");
		if (modeofoperation.equalsIgnoreCase("bulk")) {
			System.out.println("BatchSize: " + batchsize);
			System.out.println("Nbrofchunks : " + nbrofchunks);
		}
		System.out.println("Total records = " + totalrecords);

	}

	public static int protectFromFileBulk(String url, boolean debug, List<String> strings, int batchsize, int index,
			int totalnumberofrecords, int recordsleft, String protection_profile) throws Exception {

		JsonObject crdp_payload = new JsonObject();
		String jsonBody = null;
		JsonArray crdp_payload_array = new JsonArray();
		String inputdataarray = null;
		StringBuffer protection_policy_buff = new StringBuffer();

		int totalnbrofrecords = 0;

		String line = "";
		int count = 0;
		int stopper = batchsize;
		if (index == totalnumberofrecords)
			stopper = recordsleft + 1;

		String formattedElement = String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
		protection_policy_buff.append(formattedElement);
		protection_policy_buff.append(",");

		// Loop is only needed if you have different policies for each data value in the array.
		// Example:
		/*
		 * {"protection_policy_name": "plain-nbr-internal","protection_policy_name": "plain-alpha-internal",
		 * "data_array": [ "1234567812345678", "abcdef" ]}
		 * 
		 * for (int i = 0; i < stopper; i++) {
		 * 
		 * String formattedElement = String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
		 * protection_policy_buff.append(formattedElement); protection_policy_buff.append(",");
		 * 
		 * }
		 */

		for (String str : strings) {
			totalnbrofrecords++;

			crdp_payload_array.add(str);
			count++;

			if (count == batchsize) {

				crdp_payload.add("data_array", crdp_payload_array);
				inputdataarray = crdp_payload.toString();
				protection_policy_buff.append(inputdataarray);
				inputdataarray = protection_policy_buff.toString();
				jsonBody = inputdataarray.replace("{", " ");

				jsonBody = "{" + jsonBody;

				if (debug)
					System.out.println("json body ---------------" + jsonBody);

				makeCMCall(jsonBody, url, debug);

				formattedElement = String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
				protection_policy_buff.append(formattedElement);
				protection_policy_buff.append(",");
				// Loop is only needed if you have different policies for each data value in the array.
				/*
				 * for (int i = 0; i < stopper; i++) { String formattedElement =
				 * String.format("\"protection_policy_name\" : \"%s\"", protection_profile);
				 * protection_policy_buff.append(formattedElement); protection_policy_buff.append(",");
				 * 
				 * }
				 */
				count = 0;
			}
			line = str;
		}

		if (count > 0) {
			crdp_payload.add("data_array", crdp_payload_array);
			inputdataarray = crdp_payload.toString();
			protection_policy_buff.append(inputdataarray);
			inputdataarray = protection_policy_buff.toString();
			jsonBody = inputdataarray.replace("{", " ");

			jsonBody = "{" + jsonBody;

			if (debug) {
				System.out.println(jsonBody.toString());
				System.out.println("count =" + count);
			}
			makeCMCall(jsonBody, url, debug);

		}

		return totalnbrofrecords;

	}

	public static int protectFromFile(String url, boolean debug, String filePath, String protection_profile)
			throws Exception {

		JsonObject crdp_payload = new JsonObject();
		String jsonBody = null;
		String inputdataarray = null;

		int totalnbrofrecords = 0;
		try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
			String line;

			crdp_payload.addProperty("protection_policy_name", protection_profile);

			while ((line = br.readLine()) != null) {
				totalnbrofrecords++;
				crdp_payload.addProperty("data", line);
				inputdataarray = crdp_payload.toString();
				jsonBody = inputdataarray.replace("{", " ");
				jsonBody = "{" + jsonBody;
				if (debug)
					System.out.println("jsonBody        " + jsonBody);
				makeCMCall(jsonBody, url, debug);
				crdp_payload = new JsonObject();
				crdp_payload.addProperty("protection_policy_name", protection_profile);
			}

		} catch (IOException e) {
			e.printStackTrace();
		}

		return totalnbrofrecords;

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

	public static int makeCMCall(String payload, String url, boolean debug) throws Exception {

		disableCertValidation();

		// Create URL object
		URL apiUrl = new URL(url);
		// Create connection object
		HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
		connection.setRequestMethod("POST");
		connection.setRequestProperty("Content-Type", "application/json");
		connection.setDoOutput(true);
		// connection.setRequestProperty("Authorization", newtoken);
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

		return responseCode;

	}

	public static List<String> readStringsFromFile(String filePath) {
		List<String> strings = new ArrayList<>();

		try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
			String line;
			while ((line = reader.readLine()) != null) {
				strings.add(line);
			}
		} catch (IOException e) {
			System.err.println("Error reading file: " + e.getMessage());
		}

		return strings;
	}

}
