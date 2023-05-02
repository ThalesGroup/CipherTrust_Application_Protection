/**
 * 
 */
package com.fakebank.proxy.bean;

import java.util.List;

/**
 * @author CipherTrust.io
 *
 */
public class CustomerCreditAccounts {
	private String userName;
	private List<CustomerAccountCard> accounts;

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public List<CustomerAccountCard> getAccounts() {
		return accounts;
	}

	public void setAccounts(List<CustomerAccountCard> accounts) {
		this.accounts = accounts;
	}
}
