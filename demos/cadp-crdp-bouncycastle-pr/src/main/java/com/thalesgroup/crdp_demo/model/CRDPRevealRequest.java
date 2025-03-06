package com.thalesgroup.crdp_demo.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * @author CipherTrust.io
 *
 */
public class CRDPRevealRequest {
    @JsonProperty("protection_policy_name")
	private String policyName;
    @JsonProperty("protected_data")
	private String data;
    private String username;

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
    public String getUsername() {
        return username;
    }
    public void setUsername(String username) {
        this.username = username;
    }
}
