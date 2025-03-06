package com.thalesgroup.crdp_demo.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * @author CipherTrust.io
 *
 */
public class CRDPProtectResponse {
    @JsonProperty("protected_data")
	private String cipherText;

	public String getCipherText() {
		return cipherText;
	}

	public void setCipherText(String cipherText) {
		this.cipherText = cipherText;
	}
}
