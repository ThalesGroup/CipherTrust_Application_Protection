package com.fakebank.dpg.bean;

public class CreateCustomerResponseBean {

	private String customerId;
	private String fullName;

	public String getCustomerId() {
		return customerId;
	}

	public void setCustomerId(String customerId) {
		this.customerId = customerId;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	@Override
	public String toString() {
		return "CreateCustomerResponseBean [customerId=" + customerId + ", fullName=" + fullName + "]";
	}

	public CreateCustomerResponseBean(String customerId, String fullName) {
		super();
		this.customerId = customerId;
		this.fullName = fullName;
	}

	public CreateCustomerResponseBean() {
		super();
		// TODO Auto-generated constructor stub
	}

}
