package com.ecom.dpg.bean;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
public class AddressBean {
	private String street;
	private String unit;
	private String city;
	private String state;
	private String zipCode;
	private String country;

	public String getStreet() {
		return street;
	}

	public void setStreet(String street) {
		this.street = street;
	}

	public String getUnit() {
		return unit;
	}

	public void setUnit(String unit) {
		this.unit = unit;
	}

	public String getCity() {
		return city;
	}

	public void setCity(String city) {
		this.city = city;
	}

	public String getState() {
		return state;
	}

	public void setState(String state) {
		this.state = state;
	}

	public String getZipCode() {
		return zipCode;
	}

	public void setZipCode(String zipCode) {
		this.zipCode = zipCode;
	}

	public String getCountry() {
		return country;
	}

	public void setCountry(String country) {
		this.country = country;
	}

	@Override
	public String toString() {
		return "AddressBean [street=" + street + ", unit=" + unit + ", city=" + city + ", state=" + state
				+ ", zipCode=" + zipCode + ", country=" + country + "]";
	}

	public AddressBean(String street, String unit, String city, String state, String zipCode, String country) {
		super();
		this.street = street;
		this.unit = unit;
		this.city = city;
		this.state = state;
		this.zipCode = zipCode;
		this.country = country;
	}

	public AddressBean() {
		super();
		// TODO Auto-generated constructor stub
	}

}
