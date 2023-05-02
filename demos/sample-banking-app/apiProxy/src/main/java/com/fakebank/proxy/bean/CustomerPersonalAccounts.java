/**
 * 
 */
package com.fakebank.proxy.bean;

import java.util.List;

/**
 * @author CipherTrust.io
 *
 */
public class CustomerPersonalAccounts {
	private List<CustomerPersonalDetails> accounts;

	public List<CustomerPersonalDetails> getAccounts() {
		return accounts;
	}

	public void setAccounts(List<CustomerPersonalDetails> accounts) {
		this.accounts = accounts;
	}
}
