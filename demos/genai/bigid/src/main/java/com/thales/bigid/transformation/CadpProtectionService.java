package com.thales.bigid.transformation;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;

public class CadpProtectionService implements ProtectionService {

	private final ThalesCADPProtectRevealHelper helper;
	private final RuntimeConfig config;
	private final boolean prefixOutput;

	public CadpProtectionService(ThalesCADPProtectRevealHelper helper, RuntimeConfig config, boolean prefixOutput) {
		this.helper = helper;
		this.config = config;
		this.prefixOutput = prefixOutput;
	}

	@Override
	public String protect(String plainText, String piiCategory) {
		String policy = resolvePolicy(piiCategory);
		String protectedValue = helper.protectData(plainText, policy, helper.policyType);
		if (!prefixOutput) {
			return protectedValue;
		}
		String prefix = resolveTagCode(policy);
		return prefix + protectedValue.length() + ":" + protectedValue;
	}

	@Override
	public String reveal(String protectedText, String piiCategory) {
		String policy = resolvePolicy(piiCategory);
		String policyType = policy.toLowerCase().contains("internal") ? "internal" : "external";
		return helper.revealData(protectedText, policy, policyType);
	}

	@Override
	public String revealTaggedText(String textWithTags) {
		Map<String, String> replacements = new LinkedHashMap<>();
		for (Map.Entry<String, String> tagEntry : config.tagPolicyMap.entrySet()) {
			String tagName = tagEntry.getKey();
			String policy = tagEntry.getValue();
			String prefix = config.resolveTagCode(tagName);
			int index = 0;
			while ((index = textWithTags.indexOf(prefix, index)) != -1) {
				int lengthStart = index + prefix.length();
				int colonIndex = textWithTags.indexOf(':', lengthStart);
				if (colonIndex < 0) {
					break;
				}
				try {
					int protectedLength = Integer.parseInt(textWithTags.substring(lengthStart, colonIndex));
					int valueStart = colonIndex + 1;
					int valueEnd = valueStart + protectedLength;
					if (valueEnd > textWithTags.length()) {
						break;
					}
					String taggedValue = textWithTags.substring(index, valueEnd);
					String protectedValue = textWithTags.substring(valueStart, valueEnd);
					String policyType = policy.toLowerCase().contains("internal") ? "internal" : "external";
					String revealedValue = helper.revealData(protectedValue, policy, policyType);
					replacements.put(taggedValue, revealedValue);
					index = valueEnd;
				} catch (NumberFormatException ex) {
					index = colonIndex + 1;
				}
			}
		}
		String revealedText = textWithTags;
		for (Map.Entry<String, String> entry : replacements.entrySet()) {
			revealedText = revealedText.replace(entry.getKey(), entry.getValue());
		}
		return revealedText;
	}

	private String resolvePolicy(String piiCategory) {
		if (piiCategory != null) {
			for (Map.Entry<String, String> entry : config.piiPolicyMap.entrySet()) {
				if (entry.getKey().equalsIgnoreCase(piiCategory)) {
					return entry.getValue();
				}
			}
		}
		return helper.defaultPolicy != null ? helper.defaultPolicy : helper.policyName;
	}

	private String resolveTagCode(String policy) {
		String tagName = findTagNameForPolicy(policy);
		if (tagName != null) {
			return config.resolveTagCode(tagName);
		}
		String computedPrefix = Base64.getEncoder()
				.encodeToString((config.tagPrefix + "char").getBytes(StandardCharsets.UTF_8));
		return computedPrefix + "-";
	}

	private String findTagNameForPolicy(String policy) {
		for (Map.Entry<String, String> entry : config.tagPolicyMap.entrySet()) {
			if (entry.getValue().equalsIgnoreCase(policy)) {
				return entry.getKey();
			}
		}
		return null;
	}
}
