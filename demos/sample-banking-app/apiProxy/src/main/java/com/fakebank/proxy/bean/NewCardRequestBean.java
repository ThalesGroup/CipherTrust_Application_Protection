/**
 * 
 */
package com.fakebank.proxy.bean;

/**
 * @author CipherTrust.io
 *
 */
public class NewCardRequestBean {
	private String userName;
	private String accFriendlyName;

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public String getAccFriendlyName() {
		return accFriendlyName;
	}

	public void setAccFriendlyName(String accFriendlyName) {
		this.accFriendlyName = accFriendlyName;
	}

	public NewCardRequestBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public NewCardRequestBean(String userName, String accFriendlyName) {
		super();
		this.userName = userName;
		this.accFriendlyName = accFriendlyName;
	}

	@Override
	public String toString() {
		return "AccountCreateRequestBean [userName=" + userName + ", accFriendlyName="	+ accFriendlyName + "]";
	}
}
