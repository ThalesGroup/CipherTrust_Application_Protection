package com.thales.bigid.transformation;

public interface ProtectionService {

	String protect(String plainText, String piiCategory);

	String reveal(String protectedText, String piiCategory);

	String revealTaggedText(String textWithTags);
}
