package com.thales.bigid.transformation;

import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.CipherTextData;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;

public class ThalesCADPProtectRevealHelper extends ThalesProtectRevealHelper {

	public ThalesCADPProtectRevealHelper(String keyManagerHost, String registrationToken, String metadata,
			String policyType, boolean showmetadata) {
		try {
			RegisterClientParameters registerClientParams = new RegisterClientParameters.Builder(keyManagerHost,
					registrationToken.toCharArray()).build();
			CentralManagementProvider clientManagementProvider = new CentralManagementProvider(registerClientParams);
			clientManagementProvider.addProvider();
			this.metadata = metadata;
			this.policyType = policyType;
			this.showmetadata = showmetadata;
		} catch (Exception ex) {
			throw new IllegalStateException("Unable to initialize Thales CADP helper.", ex);
		}
	}

	@Override
	public String revealData(String encryptedData, String protectionPolicyName, String policyType) {
		CipherTextData encryptedDataObject = new CipherTextData();
		if ("external".equalsIgnoreCase(policyType) && metadata != null) {
			encryptedDataObject.setVersion(metadata.getBytes());
		}
		encryptedDataObject.setCipherText(encryptedData.getBytes());
		byte[] decryptedData = CryptoManager.reveal(encryptedDataObject, protectionPolicyName, this.revealUser);
		return new String(decryptedData);
	}

	@Override
	public String protectData(String plainText, String protectionPolicyName, String policyType) {
		if (!isValid(plainText)) {
			return plainText;
		}

		CipherTextData encryptedDataObject = CryptoManager.protect(plainText.getBytes(), protectionPolicyName);
		String protectedValue = new String(encryptedDataObject.getCipherText());
		this.policyType = policyType;

		if ("internal".equalsIgnoreCase(policyType)) {
			if (!showmetadata) {
				protectedValue = parseString(protectedValue);
			}
			this.metadata = protectedValue.substring(0, 7);
		} else {
			this.metadata = encryptedDataObject.getVersion() == null ? null : new String(encryptedDataObject.getVersion());
		}

		return protectedValue;
	}
}
