/**
 * 
 */
package com.fakebank.dpg.bean;

import java.util.List;

import com.fakebank.dpg.model.CustomerAccountCard;

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
