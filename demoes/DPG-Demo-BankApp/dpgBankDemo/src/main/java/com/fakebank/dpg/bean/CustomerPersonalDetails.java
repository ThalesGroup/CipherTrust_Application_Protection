package com.fakebank.dpg.bean;

import com.fakebank.dpg.model.CustomerAccountPersonal;

public class CustomerPersonalDetails {
	private String userName;
	private CustomerAccountPersonal details;

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public CustomerAccountPersonal getDetails() {
		return details;
	}

	public void setDetails(CustomerAccountPersonal details) {
		this.details = details;
	}
}
