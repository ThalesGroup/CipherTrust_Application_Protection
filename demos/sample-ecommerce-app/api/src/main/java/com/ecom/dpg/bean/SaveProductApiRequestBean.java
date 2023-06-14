/**
 * 
 */
package com.ecom.dpg.bean;

import java.util.List;

/**
 * @author Anurag Jain
 *
 */
public class SaveProductApiRequestBean {

	private String prodCategory;
	private String prodTitle;
	private String unitPrice;
	private String prodDesc;
	private List<String> availableColors;
	private List<String> availableStyles;
	private String prodCode;
	private String prodDimH;
	private String prodDimD;
	private String prodDimL;
	private String prodComposition;

	public String getProdCategory() {
		return prodCategory;
	}

	public void setProdCategory(String prodCategory) {
		this.prodCategory = prodCategory;
	}

	public String getProdTitle() {
		return prodTitle;
	}

	public void setProdTitle(String prodTitle) {
		this.prodTitle = prodTitle;
	}

	public String getUnitPrice() {
		return unitPrice;
	}

	public void setUnitPrice(String unitPrice) {
		this.unitPrice = unitPrice;
	}

	public String getProdDesc() {
		return prodDesc;
	}

	public void setProdDesc(String prodDesc) {
		this.prodDesc = prodDesc;
	}

	public List<String> getAvailableColors() {
		return availableColors;
	}

	public void setAvailableColors(List<String> availableColors) {
		this.availableColors = availableColors;
	}

	public List<String> getAvailableStyles() {
		return availableStyles;
	}

	public void setAvailableStyles(List<String> availableStyles) {
		this.availableStyles = availableStyles;
	}

	public String getProdCode() {
		return prodCode;
	}

	public void setProdCode(String prodCode) {
		this.prodCode = prodCode;
	}

	public String getProdDimH() {
		return prodDimH;
	}

	public void setProdDimH(String prodDimH) {
		this.prodDimH = prodDimH;
	}

	public String getProdDimD() {
		return prodDimD;
	}

	public void setProdDimD(String prodDimD) {
		this.prodDimD = prodDimD;
	}

	public String getProdDimL() {
		return prodDimL;
	}

	public void setProdDimL(String prodDimL) {
		this.prodDimL = prodDimL;
	}

	public String getProdComposition() {
		return prodComposition;
	}

	public void setProdComposition(String prodComposition) {
		this.prodComposition = prodComposition;
	}

	public SaveProductApiRequestBean() {

	}
}
