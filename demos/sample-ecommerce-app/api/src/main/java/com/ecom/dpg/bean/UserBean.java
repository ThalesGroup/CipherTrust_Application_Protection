package com.ecom.dpg.bean;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class UserBean {

	private String username;
	private String fullName;
	private String email;
	private String mobileNum;
	private AddressBean address;

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getMobileNum() {
		return mobileNum;
	}

	public void setMobileNum(String mobileNum) {
		this.mobileNum = mobileNum;
	}

	public AddressBean getAddress() {
		return address;
	}

	public void setAddress(AddressBean address) {
		this.address = address;
	}

	@Override
	public String toString() {
		return "UserDocument [username=" + username + ", fullName=" + fullName + ", email=" + email + ", mobileNum="
				+ mobileNum + ", address=" + address + "]";
	}

	public UserBean(String username, String fullName, String email, String mobileNum, AddressBean address) {
		super();
		this.username = username;
		this.fullName = fullName;
		this.email = email;
		this.mobileNum = mobileNum;
		this.address = address;
	}

	public UserBean() {
		super();
		// TODO Auto-generated constructor stub
	}

}
