package com.ecom.dpg.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.ecom.dpg.bean.ApiResponseBean;
import com.ecom.dpg.bean.ApiResponseWithOrdersBean;
import com.ecom.dpg.bean.SaveOrderApiRequestBean;
import com.ecom.dpg.model.OrderDocument;
import com.ecom.dpg.model.UserDocument;
import com.ecom.dpg.repository.ShopMongoRepository;
import com.ecom.dpg.repository.UserMongoRepository;
/**
 * @author Anurag Jain - Developer Advocate
 * 
 */

@RestController
public class OrderMgmtController {

	@Autowired
	private ShopMongoRepository orderRepo;
	
	@Autowired
	private UserMongoRepository userRepo;
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/order-mgmt/order/create")
	public ApiResponseBean createOrder(@RequestBody SaveOrderApiRequestBean bean) {
		ApiResponseBean response = new ApiResponseBean();
		OrderDocument newOrder;
		try {
			Optional<UserDocument> userOptional = userRepo.findById(bean.getUsername());
			if(userOptional.isPresent()) {
				UserDocument user = userOptional.get();
				OrderDocument orderDBObject = new OrderDocument();
				orderDBObject.setCard(bean.getCard());
				orderDBObject.setProducts(bean.getProducts());
				orderDBObject.setUser(user);
				try {
					newOrder = orderRepo.save(orderDBObject);
				} catch(Exception ex) {
					response.setStatus("internal server error - failed to store order information in database");
					response.setMessage(ex.getMessage());
					response.setDetails("");
					return response;
				}
			} else {
				response.setStatus("user not found");
				response.setMessage("");
				response.setDetails("");
				return response;
			}
		} catch(Exception ex) {
			response.setStatus("internal server error - failed to retrieve user from database");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		response.setStatus("success");
		response.setMessage("order created succesfully");
		response.setDetails(newOrder.getOrderId());
		return response;
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/order-mgmt/order/list")
	public ApiResponseWithOrdersBean listOrders() {
		ApiResponseWithOrdersBean response=new ApiResponseWithOrdersBean();
		List<OrderDocument> orders;
		try {
			orders = orderRepo.findAll();
			response.setStatus("success");
			response.setMessage("");
			response.setData(orders);
			return response;
		} catch(Exception ex) {
			response.setStatus("error");
			response.setMessage("Failed to retrieve data from database");
			response.setData(null);
			return response;
		}
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/order-mgmt/order/{id}")
	public ApiResponseWithOrdersBean getOrderById(@PathVariable("id") String id) {
		ApiResponseWithOrdersBean response=new ApiResponseWithOrdersBean();
		List<OrderDocument> orders = new ArrayList<OrderDocument>();
		try {
			Optional<OrderDocument> order = orderRepo.findById(id);
			if(order.isPresent()) {
				orders.add(order.get());
				response.setStatus("success");
				response.setMessage("");
				response.setData(orders);
				return response;
			} else {
				response.setStatus("error");
				response.setMessage("No order found with give ID");
				response.setData(null);
			}
		} catch(Exception ex) {
			response.setStatus("internal server error");
			response.setMessage(ex.getMessage());
			response.setData(null);
		}
		response.setStatus("error");
		response.setMessage("this is strange");
		response.setData(null);
		return response;
	}
}