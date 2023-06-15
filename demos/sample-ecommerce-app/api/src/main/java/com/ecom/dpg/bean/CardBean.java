package com.ecom.dpg.bean;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class CardBean {
	private String cardNumber;
	private String cvv;
	private AddressBean billingAddress;
	private AddressBean shippingAddress;

	public String getCardNumber() {
		return cardNumber;
	}

	public void setCardNumber(String cardNumber) {
		this.cardNumber = cardNumber;
	}

	public String getCvv() {
		return cvv;
	}

	public void setCvv(String cvv) {
		this.cvv = cvv;
	}

	public AddressBean getBillingAddress() {
		return billingAddress;
	}

	public void setBillingAddress(AddressBean billingAddress) {
		this.billingAddress = billingAddress;
	}

	public AddressBean getShippingAddress() {
		return shippingAddress;
	}

	public void setShippingAddress(AddressBean shippingAddress) {
		this.shippingAddress = shippingAddress;
	}

	@Override
	public String toString() {
		return "CardDocument [cardNumber=" + cardNumber + ", cvv=" + cvv + ", billingAddress=" + billingAddress
				+ ", shippingAddress=" + shippingAddress + "]";
	}

	public CardBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public CardBean(String cardNumber, String cvv, AddressBean billingAddress,
			AddressBean shippingAddress) {
		super();
		this.cardNumber = cardNumber;
		this.cvv = cvv;
		this.billingAddress = billingAddress;
		this.shippingAddress = shippingAddress;
	}

}
