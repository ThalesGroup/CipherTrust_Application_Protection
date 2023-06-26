package com.ecom.dpg.bean;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class CreateUserApiRequestBean {
	private String username;
	private String password;
	private String mobileNum;
	private String email;
	private String fullName;
	private AddressBean address;

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public String getMobileNum() {
		return mobileNum;
	}

	public void setMobileNum(String mobileNum) {
		this.mobileNum = mobileNum;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	public AddressBean getAddress() {
		return address;
	}

	public void setAddress(AddressBean address) {
		this.address = address;
	}

	@Override
	public String toString() {
		return "CreateUserApiRequestBean [username=" + username + ", password=" + password + ", mobileNum=" + mobileNum
				+ ", email=" + email + ", fullName=" + fullName + ", address=" + address + "]";
	}

	public CreateUserApiRequestBean(String username, String password, String mobileNum, String email, String fullName,
			AddressBean address) {
		super();
		this.username = username;
		this.password = password;
		this.mobileNum = mobileNum;
		this.email = email;
		this.fullName = fullName;
		this.address = address;
	}

	public CreateUserApiRequestBean() {
		super();
		// TODO Auto-generated constructor stub
	}

}
