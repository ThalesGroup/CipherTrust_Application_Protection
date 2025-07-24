package com.example;


import java.io.IOException;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/*
 * This app provides a number of different helper methods dealing with CM Application Data Protection UserSets.  There is a method to find 
 * a user in a userset and another method to populate the userset from a flat file.  Usersets are typically used within
 * an access policy but they are not restricted to that usage. 
 * Was tested with CM 2.14
 * Note: This source code is only to be used for testing and proof of concepts.
 * @author mwarner
 * 
 */

public class ThalesRestProtectRevealHelper extends ThalesProtectRevealHelper {

	String crdpip = "yourip";

	static boolean debug = true;

	public ThalesRestProtectRevealHelper(String crdpip, String metadata, String policyType, boolean showmetadata) {
		this.crdpip = crdpip;
		this.metadata = metadata;
		this.policyType = policyType;
		this.showmetadata = showmetadata;
	}

	public static void main(String[] args) throws Exception {

		String crdpip = args[0];
		String metadata = args[1];
		String policyType = args[2];
		String showmetadata = args[3];
		String crdpuser = args[4];

		boolean showmetadataparm = true;
		if (!showmetadata.equalsIgnoreCase("true"))
			showmetadataparm = false;

		ThalesRestProtectRevealHelper cmresthelper = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType,
				showmetadataparm);

		String results = cmresthelper.protectData("Thisisnewdata", "plain-alpha-internal", policyType);
		cmresthelper.revealUser = crdpuser;
		if (policyType.equalsIgnoreCase("external"))
			cmresthelper.revealData(results, "alpha-external", policyType);
		else
			cmresthelper.revealData( results, "plain-alpha-internal", policyType);
		
		System.out.println("metadata " + cmresthelper.metadata);
	}

	public String revealData(String encryptedData, String protectionPolicyName, String policyType) {

		String return_value = null;
		String protectedData = null;

		OkHttpClient client = new OkHttpClient().newBuilder().build();
		MediaType mediaType = MediaType.parse("application/json");

		String crdpjsonBody = null;

		JsonObject crdp_payload = new JsonObject();

		crdp_payload.addProperty("protection_policy_name", protectionPolicyName);
		crdp_payload.addProperty("protected_data", encryptedData);
		if (policyType.equalsIgnoreCase("external"))
			crdp_payload.addProperty("external_version", this.metadata);
		
		crdp_payload.addProperty("username", this.revealUser);
		crdpjsonBody = crdp_payload.toString();
		System.out.println(crdpjsonBody);
		RequestBody body = RequestBody.create(mediaType, crdpjsonBody);


		Request request = new Request.Builder().url("http://" + this.crdpip + ":8090/v1/reveal").method("POST", body)
				.addHeader("Content-Type", "application/json").build();
		Response response;
		try {
			response = client.newCall(request).execute();
			
			if (response.isSuccessful()) {
				// Parse JSON response
				String responseBody = response.body().string();
				System.out.println(responseBody);
				Gson gson = new Gson();
				JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
				protectedData = jsonObject.get("data").getAsString();

				// Print the protected data
				System.out.println("Revealed Data: " + protectedData);
			} else {
				System.err.println("Request failed with status code: " + response.code());
			}

			response.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}



		System.out.println("username is in reveal " + this.revealUser);
		return_value = protectedData;

		return return_value;
	}

	public String protectData(String plainText, String protectionPolicyName, String policyType) {

		String return_value = plainText;
		String protectedData = return_value;
		this.policyType = policyType;

		String crdpjsonBody = null;
		if (isValid(plainText)) {
			JsonObject crdp_payload = new JsonObject();

			crdp_payload.addProperty("protection_policy_name", protectionPolicyName);
			crdp_payload.addProperty("data", plainText);

			OkHttpClient client = new OkHttpClient().newBuilder().build();
			MediaType mediaType = MediaType.parse("application/json");

			crdpjsonBody = crdp_payload.toString();

			System.out.println(crdpjsonBody);

			RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

			Request request = new Request.Builder().url("http://" + this.crdpip + ":8090/v1/protect")
					.method("POST", body).addHeader("Content-Type", "application/json").build();
			Response response;
			try {
				response = client.newCall(request).execute();
				String version = null;
				if (response.isSuccessful()) {
					// Parse JSON response
					String responseBody = response.body().string();
					Gson gson = new Gson();
					JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
					protectedData = jsonObject.get("protected_data").getAsString();
					if (policyType.equalsIgnoreCase("external")) {
						version = jsonObject.get("external_version").getAsString();
						System.out.println("external_version: " + version);
						this.metadata = version;
					} else {
						this.metadata = protectedData.substring(0, 7);
						if (!this.showmetadata) {

							protectedData = parseString(protectedData);
						}

					}
					// Print the protected data
					System.out.println("Protected Data: " + protectedData);

				} else {
					System.err.println("Request failed with status code: " + response.code());
				}

				response.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}


		}
		return_value = protectedData;
		return return_value;

	}



}