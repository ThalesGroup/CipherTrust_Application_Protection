package com.ecom.dpg.model;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class OrderProductDocument {
	private ProductDocument product;
	private int qty;

	public ProductDocument getProduct() {
		return product;
	}

	public void setProduct(ProductDocument product) {
		this.product = product;
	}

	public int getQty() {
		return qty;
	}

	public void setQty(int qty) {
		this.qty = qty;
	}

	@Override
	public String toString() {
		return "OrderProductDocument [product=" + product + ", qty=" + qty + "]";
	}

	public OrderProductDocument() {
		super();
		// TODO Auto-generated constructor stub
	}

	public OrderProductDocument(ProductDocument product, int qty) {
		super();
		this.product = product;
		this.qty = qty;
	}

}
