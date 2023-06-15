package com.ecom.dpg.bean;

import com.ecom.dpg.model.UserDocument;

public class ApiResponseWithUserBean {
	private String status;
	private String message;
	private UserDocument user;

	public ApiResponseWithUserBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public ApiResponseWithUserBean(String status, String message, UserDocument user) {
		super();
		this.status = status;
		this.message = message;
		this.user = user;
	}

	@Override
	public String toString() {
		return "ApiResponseWithUserBean [status=" + status + ", message=" + message + ", user=" + user + "]";
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

	public String getMessage() {
		return message;
	}

	public void setMessage(String message) {
		this.message = message;
	}

	public UserDocument getUser() {
		return user;
	}

	public void setUser(UserDocument user) {
		this.user = user;
	}
}
