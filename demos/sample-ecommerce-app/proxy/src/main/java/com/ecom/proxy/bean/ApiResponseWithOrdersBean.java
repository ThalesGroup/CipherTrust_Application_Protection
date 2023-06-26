package com.ecom.proxy.bean;

import java.util.List;

import com.ecom.proxy.model.OrderDocument;

public class ApiResponseWithOrdersBean {
	private String status;
	private String message;
	private List<OrderDocument> data;

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

	public String getMessage() {
		return message;
	}

	public void setMessage(String message) {
		this.message = message;
	}

	public List<OrderDocument> getData() {
		return data;
	}

	public void setData(List<OrderDocument> data) {
		this.data = data;
	}

	@Override
	public String toString() {
		return "ApiResponseWithOrdersBean [status=" + status + ", message=" + message + ", data=" + data + "]";
	}

	public ApiResponseWithOrdersBean(String status, String message, List<OrderDocument> data) {
		super();
		this.status = status;
		this.message = message;
		this.data = data;
	}

	public ApiResponseWithOrdersBean() {
		super();
		// TODO Auto-generated constructor stub
	}
}
