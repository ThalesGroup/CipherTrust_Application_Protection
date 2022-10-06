package com.fakebank.proxy.bean;

public class CustomerAccountPersonal {

	private String name;
	private String dob;
	private String mobile;
	private String ssn;
	private String thalesId;

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDob() {
		return dob;
	}

	public void setDob(String dob) {
		this.dob = dob;
	}

	public String getMobile() {
		return mobile;
	}

	public void setMobile(String mobile) {
		this.mobile = mobile;
	}

	public String getSsn() {
		return ssn;
	}

	public void setSsn(String ssn) {
		this.ssn = ssn;
	}

	public String getThalesId() {
		return thalesId;
	}

	public void setThalesId(String thalesId) {
		this.thalesId = thalesId;
	}

	@Override
	public String toString() {
		return "CustomerAccountPersonal [name=" + name + ", dob=" + dob + ", mobile=" + mobile + ", ssn=" + ssn
				+ ", thalesId=" + thalesId + "]";
	}

	public CustomerAccountPersonal(String name, String dob, String mobile, String ssn, String thalesId) {
		super();
		this.name = name;
		this.dob = dob;
		this.mobile = mobile;
		this.ssn = ssn;
		this.thalesId = thalesId;
	}

	public CustomerAccountPersonal() {
		super();
		// TODO Auto-generated constructor stub
	}

}