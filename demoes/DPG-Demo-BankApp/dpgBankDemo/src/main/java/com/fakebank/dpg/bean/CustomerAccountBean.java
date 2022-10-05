/**
 * 
 */
package com.fakebank.dpg.bean;

/**
 * @author CipherTrust.io
 *
 */

public class CustomerAccountBean {
	private String ssn;
	private String dob;
	private String fullName;
	private String userName;
	private String mobileNumber;
	private String ccNumber;
	private String ccCvv;
	private String ccExpiry;
	private long accountBalance;
	private String createDt;
	private String intCmId;
	private String accFriendlyName;

	public String getSsn() {
		return ssn;
	}

	public void setSsn(String ssn) {
		this.ssn = ssn;
	}

	public String getDob() {
		return dob;
	}

	public void setDob(String dob) {
		this.dob = dob;
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

	public String getCcNumber() {
		return ccNumber;
	}

	public void setCcNumber(String ccNumber) {
		this.ccNumber = ccNumber;
	}

	public String getCcCvv() {
		return ccCvv;
	}

	public void setCcCvv(String ccCvv) {
		this.ccCvv = ccCvv;
	}

	public String getCcExpiry() {
		return ccExpiry;
	}

	public void setCcExpiry(String ccExpiry) {
		this.ccExpiry = ccExpiry;
	}

	public long getAccountBalance() {
		return accountBalance;
	}

	public void setAccountBalance(long accountBalance) {
		this.accountBalance = accountBalance;
	}

	public String getCreateDt() {
		return createDt;
	}

	public void setCreateDt(String createDt) {
		this.createDt = createDt;
	}

	public String getIntCmId() {
		return intCmId;
	}

	public void setIntCmId(String intCmId) {
		this.intCmId = intCmId;
	}

	public String getAccFriendlyName() {
		return accFriendlyName;
	}

	public void setAccFriendlyName(String accFriendlyName) {
		this.accFriendlyName = accFriendlyName;
	}

	public CustomerAccountBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public CustomerAccountBean(String ssn, String dob, String fullName, String userName, String mobileNumber,
			String ccNumber, String ccCvv, String ccExpiry, long accountBalance, String createDt, String intCmId,
			String accFriendlyName) {
		super();
		this.ssn = ssn;
		this.dob = dob;
		this.fullName = fullName;
		this.userName = userName;
		this.mobileNumber = mobileNumber;
		this.ccNumber = ccNumber;
		this.ccCvv = ccCvv;
		this.ccExpiry = ccExpiry;
		this.accountBalance = accountBalance;
		this.createDt = createDt;
		this.intCmId = intCmId;
		this.accFriendlyName = accFriendlyName;
	}

	@Override
	public String toString() {
		return "CustomerAccountBean [ssn=" + ssn + ", dob=" + dob + ", fullName=" + fullName + ", userName=" + userName
				+ ", mobileNumber=" + mobileNumber + ", ccNumber=" + ccNumber + ", ccCvv=" + ccCvv + ", ccExpiry="
				+ ccExpiry + ", accountBalance=" + accountBalance + ", createDt=" + createDt + ", intCmId=" + intCmId
				+ ", accFriendlyName=" + accFriendlyName + "]";
	}

}
