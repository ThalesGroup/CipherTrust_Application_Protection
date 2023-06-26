package com.ecom.dpg.model;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class CardDocument {
	private String cardNumber;
	private String cvv;
	private AddressDocument billingAddress;
	private AddressDocument shippingAddress;

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

	public AddressDocument getBillingAddress() {
		return billingAddress;
	}

	public void setBillingAddress(AddressDocument billingAddress) {
		this.billingAddress = billingAddress;
	}

	public AddressDocument getShippingAddress() {
		return shippingAddress;
	}

	public void setShippingAddress(AddressDocument shippingAddress) {
		this.shippingAddress = shippingAddress;
	}

	@Override
	public String toString() {
		return "CardDocument [cardNumber=" + cardNumber + ", cvv=" + cvv + ", billingAddress=" + billingAddress
				+ ", shippingAddress=" + shippingAddress + "]";
	}

	public CardDocument() {
		super();
		// TODO Auto-generated constructor stub
	}

	public CardDocument(String cardNumber, String cvv, AddressDocument billingAddress,
			AddressDocument shippingAddress) {
		super();
		this.cardNumber = cardNumber;
		this.cvv = cvv;
		this.billingAddress = billingAddress;
		this.shippingAddress = shippingAddress;
	}

}
