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

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

/**
 * @author CipherTrust.io
 * This is the main controller file that UI interacts with
 */
@RestController
public class CCAccountController {

	@Autowired
	private RestTemplate restTemplate;

	@Operation(summary = "Create a new credit card account")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account Created Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = NewAccountBean.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping(value = "/api/proxy/account/create", produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ApiResponseBean createAccount(@RequestBody NewAccountBean bean) {
		// This API controller is invoked by the signup page on the Banking Application Frontend
		// Internally invokes the dpgBankDemo app's api/user-mgmt/user/create endpoint for user creation
		// Internal endpoint is protected by the DPG container from Thales CipherTrust Application Protection suite
		String dockerUri = "http://ciphertrust:9005/api/user/create";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, bean, ApiResponseBean.class);

		return createResponse;
	}

	@Operation(summary = "Update account details of the account holder")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account Updated Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = AccountDetailsUpdateRequestBean.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping(value = "/api/proxy/account/details", produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ApiResponseBean saveAccountDetails(@RequestBody AccountDetailsUpdateRequestBean bean) {
		// Implements the API controller action for the update account details action on the frontend
		CustomerPersonalDetails acc = new CustomerPersonalDetails();
		CustomerAccountPersonal personalDetails = new CustomerAccountPersonal();

		personalDetails.setDob(bean.getDob());
		personalDetails.setMobile(bean.getMobileNumber());
		personalDetails.setName(bean.getFullName());
		personalDetails.setSsn(bean.getSsn());
		personalDetails.setThalesId(bean.getCmID());

		acc.setUserName(bean.getUserName());
		acc.setDetails(personalDetails);

		String dockerUri = "http://ciphertrust:9005/api/account/details/save";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, acc, ApiResponseBean.class);

		return createResponse;
	}

	@Operation(summary = "Add another credit card to existing user account")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Card Added Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = NewCardRequestBean.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping(value = "/api/proxy/account/card", produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ApiResponseBean saveNewCard(@RequestBody NewCardRequestBean bean) {
		//Need This
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

		String dockerUri = "http://ciphertrust:9005/api/account/card/save";
		ApiResponseBean createResponse = restTemplate.postForObject(dockerUri, newCard, ApiResponseBean.class);

		return createResponse;
	}

	@Operation(summary = "Fetch account details by user ID")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account details retrieved succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerPersonalDetails.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@GetMapping(value = "/api/proxy/account/details/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public CustomerPersonalDetails getAccountDetails(@PathVariable("id") String id,
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		String dockerUri = "http://ciphertrust:9005/api/account/details/" + id;
		HttpHeaders headers = new HttpHeaders();
		headers.add("Authorization", header);
		HttpEntity<String> request = new HttpEntity<String>(headers);
		ResponseEntity<CustomerPersonalDetails> response = restTemplate.exchange(dockerUri, HttpMethod.GET, request,
				CustomerPersonalDetails.class);

		return response.getBody();
	}

	@Operation(summary = "Fetch cards associated with the account by user ID")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account details retrieved succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerCreditAccounts.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	//@GetMapping("/api/proxy/accounts/{account}")
	@GetMapping("/api/proxy/account/cards/{id}")
	public CustomerCreditAccounts getAccountsById(@PathVariable("id") String id, 
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		String dockerUri = "http://ciphertrust:9005/api/account/cards/" + id;
		HttpHeaders headers = new HttpHeaders();
		headers.add("Authorization", header);
		HttpEntity<String> request = new HttpEntity<String>(headers);

		ResponseEntity<CustomerCreditAccounts> fetchResponse = restTemplate.exchange(dockerUri, HttpMethod.GET, request,
				CustomerCreditAccounts.class);
		return fetchResponse.getBody();
	}

	@Operation(summary = "Fetch all accounts for the admin view")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Accounts retrieved succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerPersonalAccounts.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@GetMapping("/api/proxy/accounts/all")
	public CustomerPersonalAccounts getAllAccountHolders(@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		String dockerUri = "http://ciphertrust:9005/api/account/all";
		HttpHeaders headers = new HttpHeaders();

		headers.add("Authorization", header);
		HttpEntity<String> request = new HttpEntity<String>(headers);

		ResponseEntity<CustomerPersonalAccounts> fetchResponse = restTemplate.exchange(dockerUri, HttpMethod.GET,
				request, CustomerPersonalAccounts.class);
		return fetchResponse.getBody();
	}
}
