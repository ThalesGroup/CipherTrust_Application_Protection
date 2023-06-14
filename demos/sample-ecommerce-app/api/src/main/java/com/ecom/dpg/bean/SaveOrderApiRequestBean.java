package com.ecom.dpg.bean;

import java.util.List;

import com.ecom.dpg.model.CardDocument;
import com.ecom.dpg.model.OrderProductDocument;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class SaveOrderApiRequestBean {
	private List<OrderProductDocument> products;
	private String username;
	private CardDocument card;

	public List<OrderProductDocument> getProducts() {
		return products;
	}

	public void setProducts(List<OrderProductDocument> products) {
		this.products = products;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public CardDocument getCard() {
		return card;
	}

	public void setCard(CardDocument card) {
		this.card = card;
	}

	@Override
	public String toString() {
		return "SaveOrderApiRequestBean [products=" + products + ", username=" + username + ", card=" + card + "]";
	}

	public SaveOrderApiRequestBean(List<OrderProductDocument> products, String username, CardDocument card) {
		super();
		this.products = products;
		this.username = username;
		this.card = card;
	}

	public SaveOrderApiRequestBean() {
		super();
		// TODO Auto-generated constructor stub
	}
}
