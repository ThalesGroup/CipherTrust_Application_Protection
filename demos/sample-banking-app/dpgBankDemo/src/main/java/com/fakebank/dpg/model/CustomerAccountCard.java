/**
 * 
 */
package com.fakebank.dpg.model;

/**
 * @author CipherTrust.io
 *
 */
public class CustomerAccountCard {
	private String expDate;
	private String ccNumber;
	private String cvv;
	private String friendlyName;
	private String balance;

	public String getExpDate() {
		return expDate;
	}

	public void setExpDate(String expDate) {
		this.expDate = expDate;
	}

	public String getCcNumber() {
		return ccNumber;
	}

	public void setCcNumber(String ccNumber) {
		this.ccNumber = ccNumber;
	}

	public String getCvv() {
		return cvv;
	}

	public void setCvv(String cvv) {
		this.cvv = cvv;
	}

	public String getFriendlyName() {
		return friendlyName;
	}

	public void setFriendlyName(String friendlyName) {
		this.friendlyName = friendlyName;
	}

	public String getBalance() {
		return balance;
	}

	public void setBalance(String balance) {
		this.balance = balance;
	}

	@Override
	public String toString() {
		return "CustomerAccountCard [expDate=" + expDate + ", ccNumber=" + ccNumber + ", cvv=" + cvv + ", friendlyName="
				+ friendlyName + ", balance=" + balance + "]";
	}

	public CustomerAccountCard(String expDate, String ccNumber, String cvv, String friendlyName, String balance) {
		super();
		this.expDate = expDate;
		this.ccNumber = ccNumber;
		this.cvv = cvv;
		this.friendlyName = friendlyName;
		this.balance = balance;
	}

	public CustomerAccountCard() {
		super();
		// TODO Auto-generated constructor stub
	}

}
