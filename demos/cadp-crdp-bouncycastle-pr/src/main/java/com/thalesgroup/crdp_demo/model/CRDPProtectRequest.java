package com.thalesgroup.crdp_demo.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * @author CipherTrust.io
 *
 */
public class CRDPProtectRequest {
    @JsonProperty("protection_policy_name")
	private String policyName;
	private String data;

	public String getPolicyName() {
		return policyName;
	}

	public void setPolicyName(String policyName) {
		this.policyName = policyName;
	}

	public String getData() {
		return data;
	}

	public void setData(String data) {
		this.data = data;
	}
}
