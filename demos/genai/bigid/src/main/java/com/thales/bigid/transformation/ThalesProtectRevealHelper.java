package com.thales.bigid.transformation;

public abstract class ThalesProtectRevealHelper {

	String metadata = null;
	String policyType = null;
	boolean showmetadata = true;
	String policyName = null;
	String revealUser = null;
	String defaultPolicy = null;

	public abstract String protectData(String source, String policyName, String policyType);

	public abstract String revealData(String source, String policyName, String policyType);

	public boolean isValid(String input) {
		return input != null && !input.isEmpty() && input.length() >= 2;
	}

	public String parseString(String input) {
		this.metadata = input.substring(0, 7);
		return input.substring(7);
	}
}
