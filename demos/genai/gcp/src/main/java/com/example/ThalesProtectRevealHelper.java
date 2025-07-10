/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
package com.example;



/**
 * This sample shows how to encrypt/decrypt data using protect/reveal API's in
 * CADP for JAVA.
 */
public abstract class ThalesProtectRevealHelper {

	String metadata = null;
	String policyType = null;
	boolean showmetadata = true;
	String policyName = null;
	String revealUser = null;
	String defaultPolicy = null;



	public abstract String protectData(String s, String b, String c);
	
	public abstract String revealData(String s, String b, String c);
	
	public ThalesProtectRevealHelper()
	{
	}
	private static String removeQuotes(String input) {

		// Remove double quotes from the input string
		input = input.replace("\"", "");

		return input;
	}

	public boolean isValid(String input) {

		if (input == null || input.isEmpty()) {
			System.out.println("Input string is null or empty.");
			return false;
		}

		if (input.length() < 2) {
			System.out.println("Input string is shorter than 3 bytes: " + input);
			return false;
		}

		return true;

	}

	public String parseString(String input) {

		String metadata = input.substring(0, 7);

		this.metadata = metadata;
		String protectedData = input.substring(7);

		return protectedData;
	}
}
