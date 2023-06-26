/**
 * 
 */
package com.ecom.dpg.controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.ecom.dpg.bean.ApiResponseBean;
import com.ecom.dpg.bean.SaveProductApiRequestBean;

/**
 * @author Anurag Jain
 *
 */
@RestController
public class InventoryMgmtController {
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/inventory-mgmt/product/create")
	public ApiResponseBean createProduct(@RequestBody SaveProductApiRequestBean bean) {
		ApiResponseBean resp = new ApiResponseBean();
		return resp;
	}
}
