/**
 * 
 */
package com.fakebank.proxy.controller;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.concurrent.ThreadLocalRandom;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.fakebank.proxy.bean.AccountDetailsUpdateRequestBean;
import com.fakebank.proxy.bean.ApiResponseBean;
import com.fakebank.proxy.bean.CustomerAccountPersonal;
import com.fakebank.proxy.bean.CustomerCreditAccounts;
import com.fakebank.proxy.bean.CustomerPersonalAccounts;
import com.fakebank.proxy.bean.CustomerPersonalDetails;
import com.fakebank.proxy.bean.NewAccountBean;
import com.fakebank.proxy.bean.NewCardRequestBean;
import com.fakebank.proxy.bean.NewCreditCardBean;


/**
 * @author CipherTrust.io
 *
 */
@RestController
public class CCAccountController {

	@Autowired
	private RestTemplate restTemplate;
	
	@CrossOrigin(origins = "*")
	@PostMapping(
			value = "/api/proxy/account/create", 
			produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ApiResponseBean createAccount(@RequestBody NewAccountBean bean) {
		
		String dockerUri = "http://ciphertrust:9005/api/user-mgmt/user/create";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, bean, ApiResponseBean.class);
		
		return createResponse;
	}
	
	@CrossOrigin(origins = "*")
	@PostMapping(
			value = "/api/proxy/account/details", 
			produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ApiResponseBean saveAccountDetails(@RequestBody AccountDetailsUpdateRequestBean bean) {
		CustomerPersonalDetails acc = new CustomerPersonalDetails();
		CustomerAccountPersonal personalDetails = new CustomerAccountPersonal();
		
		personalDetails.setDob(bean.getDob());
		personalDetails.setMobile(bean.getMobileNumber());
		personalDetails.setName(bean.getFullName());
		personalDetails.setSsn(bean.getSsn());
		personalDetails.setThalesId(bean.getCmID());
		
		acc.setUserName(bean.getUserName());
		acc.setDetails(personalDetails);
		
		String dockerUri = "http://ciphertrust:9005/api/fakebank/account/personal";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, acc, ApiResponseBean.class);
		
		return createResponse;
	}
	
	
	@CrossOrigin(origins = "*")
	@PostMapping(
			value = "/api/proxy/account/card", 
			produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ApiResponseBean saveNewCard(@RequestBody NewCardRequestBean bean) {
		NewCreditCardBean newCard = new NewCreditCardBean();
		int cvv = ThreadLocalRandom.current().nextInt(100, 999);
		String ccNumber = String.valueOf(ThreadLocalRandom.current().nextInt(1000, 9999)) + "-"
			+ String.valueOf(ThreadLocalRandom.current().nextInt(1000, 9999)) + "-"
			+ String.valueOf(ThreadLocalRandom.current().nextInt(1000, 9999)) + "-"
			+ String.valueOf(ThreadLocalRandom.current().nextInt(1000, 9999));
		
		Calendar c = Calendar.getInstance();
		c.setTime(c.getTime());
		c.add(Calendar.YEAR, 3);
		DateFormat dateFormat = new SimpleDateFormat("mm/dd/yyyy");  
        String expDate = dateFormat.format(c.getTime());
		
        newCard.setCcNumber(ccNumber);
        newCard.setCvv(String.valueOf(cvv));
        newCard.setExpDate(expDate);
		newCard.setBalance(String.valueOf(0));
		newCard.setFriendlyName(bean.getAccFriendlyName());
		newCard.setUserName(bean.getUserName());
		
		String dockerUri = "http://ciphertrust:9005/api/fakebank/account/card";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, newCard, ApiResponseBean.class);
		
		return createResponse;
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping(
			value = "/api/proxy/account/details/{id}", 
			produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public CustomerPersonalDetails getAccountDetails(
			@PathVariable("id") String id,
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		String dockerUri = "http://ciphertrust:9005/api/fakebank/account/personal/" + id;
		HttpHeaders headers = new HttpHeaders();
		headers.add("Authorization", header);
		HttpEntity<String> request = new HttpEntity<String>(headers);
		ResponseEntity<CustomerPersonalDetails> response = restTemplate.exchange(
				dockerUri, 
				HttpMethod.GET,
				request,
				CustomerPersonalDetails.class);
		
		return response.getBody();
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/proxy/accounts/{requestor}/{account}")
	public CustomerCreditAccounts getAccountsById(
			@PathVariable("requestor") String requestor,
			@PathVariable("account") String accountId,
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		String dockerUri = "http://ciphertrust:9005/api/fakebank/accounts/"+accountId;
		HttpHeaders headers = new HttpHeaders();
		headers.add("Authorization", header);
		HttpEntity<String> request = new HttpEntity<String>(headers);
		
		ResponseEntity<CustomerCreditAccounts> fetchResponse = restTemplate.exchange(
				dockerUri, 
				HttpMethod.GET, 
				request, 
				CustomerCreditAccounts.class);
		return fetchResponse.getBody();
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/proxy/accounts/all/{requestor}")
	public CustomerPersonalAccounts getAllAccountHolders(
			@PathVariable("requestor") String requestor,
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		String dockerUri = "http://ciphertrust:9005/api/fakebank/account/holders";
		HttpHeaders headers = new HttpHeaders();
		
		headers.add("Authorization", header);
		HttpEntity<String> request = new HttpEntity<String>(headers);
		
		ResponseEntity<CustomerPersonalAccounts> fetchResponse = restTemplate.exchange(
				dockerUri, 
				HttpMethod.GET, 
				request, 
				CustomerPersonalAccounts.class);
		return fetchResponse.getBody();
	}
}
