package com.ecom.proxy.model;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class ProductDocument {

	private String productId;
	private String productName;
	private Double price;

	public String getProductId() {
		return productId;
	}

	public void setProductId(String productId) {
		this.productId = productId;
	}

	public String getProductName() {
		return productName;
	}

	public void setProductName(String productName) {
		this.productName = productName;
	}

	public Double getPrice() {
		return price;
	}

	public void setPrice(Double price) {
		this.price = price;
	}

	public ProductDocument(String productId, String productName, Double price) {
		super();
		this.productId = productId;
		this.productName = productName;
		this.price = price;
	}

	public ProductDocument() {
		super();
		// TODO Auto-generated constructor stub
	}

	@Override
	public String toString() {
		return "ProductDocument [productId=" + productId + ", productName=" + productName + ", price=" + price + "]";
	}

}
