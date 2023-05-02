/**
 * 
 */
package com.fakebank.dpg.bean;

/**
 * @author CipherTrust.io
 *
 */
public class AccountDetailsUpdateRequestBean {
	private String ssn;
	private String fullName;
	private String userName;
	private String mobileNumber;
	private String dob;
	private String cmID;

	public String getSsn() {
		return ssn;
	}

	public void setSsn(String ssn) {
		this.ssn = ssn;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public String getMobileNumber() {
		return mobileNumber;
	}

	public void setMobileNumber(String mobileNumber) {
		this.mobileNumber = mobileNumber;
	}

	public String getDob() {
		return dob;
	}

	public void setDob(String dob) {
		this.dob = dob;
	}

	public String getCmID() {
		return cmID;
	}

	public void setCmID(String cmID) {
		this.cmID = cmID;
	}

	public AccountDetailsUpdateRequestBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public AccountDetailsUpdateRequestBean(String ssn, String fullName, String userName, String mobileNumber, String dob,
			String cmID) {
		super();
		this.ssn = ssn;
		this.fullName = fullName;
		this.userName = userName;
		this.mobileNumber = mobileNumber;
		this.dob = dob;
		this.cmID = cmID;
	}

	@Override
	public String toString() {
		return "AccountCreateRequestBean [ssn=" + ssn + ", fullName=" + fullName + ", userName=" + userName
				+ ", mobileNumber=" + mobileNumber + ", dob=" + dob + ", cmID=" + cmID + "]";
	}
}
