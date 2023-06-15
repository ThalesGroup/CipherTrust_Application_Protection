package com.ecom.proxy.model;

import java.util.List;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */

public class OrderDocument {

	private String orderId;
	private UserDocument user;
	private CardDocument card;
	private List<OrderProductDocument> products;

	public String getOrderId() {
		return orderId;
	}

	public void setOrderId(String orderId) {
		this.orderId = orderId;
	}

	public UserDocument getUser() {
		return user;
	}

	public void setUser(UserDocument user) {
		this.user = user;
	}

	public CardDocument getCard() {
		return card;
	}

	public void setCard(CardDocument card) {
		this.card = card;
	}

	public List<OrderProductDocument> getProducts() {
		return products;
	}

	public void setProducts(List<OrderProductDocument> products) {
		this.products = products;
	}

	@Override
	public String toString() {
		return "OrderDocument [orderId=" + orderId + ", user=" + user + ", card=" + card + ", products=" + products
				+ "]";
	}

	public OrderDocument(String orderId, UserDocument user, CardDocument card, List<OrderProductDocument> products) {
		super();
		this.orderId = orderId;
		this.user = user;
		this.card = card;
		this.products = products;
	}

	public OrderDocument() {
		super();
		// TODO Auto-generated constructor stub
	}
}
