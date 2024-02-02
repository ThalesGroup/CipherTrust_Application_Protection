package com.ecom.dpg.bean;


/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class OrderProductBean {
	private ProductBean product;
	private int qty;

	public ProductBean getProduct() {
		return product;
	}

	public void setProduct(ProductBean product) {
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
		return "OrderProductBean [product=" + product + ", qty=" + qty + "]";
	}

	public OrderProductBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public OrderProductBean(ProductBean product, int qty) {
		super();
		this.product = product;
		this.qty = qty;
	}

}
