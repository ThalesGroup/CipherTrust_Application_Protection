package com.ecom.dpg.model;

import org.springframework.data.annotation.Id;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class UserDocument {

	@Id
	private String userId;
	private String username;
	private String fullName;
	private String email;
	private String mobileNum;
	private AddressDocument address;

	public String getUserId() {
		return userId;
	}

	public void setUserId(String userId) {
		this.userId = userId;
	}

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

	public AddressDocument getAddress() {
		return address;
	}

	public void setAddress(AddressDocument address) {
		this.address = address;
	}

	@Override
	public String toString() {
		return "UserDocument [userId=" + userId + ", username=" + username + ", fullName=" + fullName + ", email="
				+ email + ", mobileNum=" + mobileNum + ", address=" + address + "]";
	}

	public UserDocument(String userId, String username, String fullName, String email, String mobileNum,
			AddressDocument address) {
		super();
		this.userId = userId;
		this.username = username;
		this.fullName = fullName;
		this.email = email;
		this.mobileNum = mobileNum;
		this.address = address;
	}

	public UserDocument() {
		super();
		// TODO Auto-generated constructor stub
	}
}
