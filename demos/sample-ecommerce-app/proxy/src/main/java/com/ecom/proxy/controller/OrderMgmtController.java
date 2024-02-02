package com.ecom.proxy.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import com.ecom.proxy.bean.ApiResponseBean;
import com.ecom.proxy.bean.ApiResponseWithOrdersBean;
import com.ecom.proxy.bean.SaveOrderApiRequestBean;

@RestController
public class OrderMgmtController {
	
	@Autowired
	private RestTemplate restTemplate;

	@CrossOrigin(origins = "*")
	@PostMapping("/proxy/order-mgmt/order/create")
	public ApiResponseBean createOrder(@RequestBody SaveOrderApiRequestBean bean) {
		String dockerUri = "http://ciphertrust:9005/api/order-mgmt/order/create";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, bean, ApiResponseBean.class);
		return createResponse;
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/proxy/order-mgmt/order/list")
	public ApiResponseWithOrdersBean listOrders() {
		String dockerUri = "http://ciphertrust:9005/api/order-mgmt/order/list";
		ApiResponseWithOrdersBean listResponse = restTemplate.getForObject(dockerUri, ApiResponseWithOrdersBean.class);
		return listResponse;
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/proxy/order-mgmt/order/{id}")
	public ApiResponseWithOrdersBean getOrderById(@PathVariable("id") String id) {
		String dockerUri = "http://ciphertrust:9005/api/order-mgmt/order/" + id;
		ApiResponseWithOrdersBean listResponse = restTemplate.getForObject(dockerUri, ApiResponseWithOrdersBean.class);
		return listResponse;
	}
}
