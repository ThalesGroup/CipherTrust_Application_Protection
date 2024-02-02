package com.ecom.dpg.model;

import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */

@Document(collection = "orders")
public class OrderDocument {

	@Id
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
