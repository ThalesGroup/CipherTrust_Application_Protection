/**
 * 
 */
package com.fakebank.dpg.controller;

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

import com.fakebank.dpg.bean.ApiResponseBean;
import com.fakebank.dpg.bean.CustomerCreditAccounts;
import com.fakebank.dpg.bean.CustomerPersonalAccounts;
import com.fakebank.dpg.bean.CustomerPersonalDetails;
import com.fakebank.dpg.bean.NewCreditCardBean;
import com.fakebank.dpg.model.CustomerAccountCard;
import com.fakebank.dpg.model.CustomerAccountMongoDocumentBean;
import com.fakebank.dpg.model.CustomerAccountPersonal;
import com.fakebank.dpg.repository.CustomerAccountMongoRepository;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;


/**
 * @author CipherTrust.io
 *
 */
@RestController
public class CCAccountController {

	@Autowired
	private CustomerAccountMongoRepository mongoCustomerAccountRepo;
	//private AccountRepository accountRepository;
	
	@Operation(summary = "Add new card to existing user account")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Card Added Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = NewCreditCardBean.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping("/api/account/card/save")
	public ApiResponseBean saveCreditAccount(@RequestBody NewCreditCardBean bean) {
		ApiResponseBean response = new ApiResponseBean();
		
		// Check if the user already exists in the database
		// If yes add new card entry, else fail with no user existing
		Optional<CustomerAccountMongoDocumentBean> existingUser = mongoCustomerAccountRepo.findById(bean.getUserName());
		if(existingUser.isPresent()) {
			CustomerAccountMongoDocumentBean user = existingUser.get();
			CustomerAccountCard newCardDetails = new CustomerAccountCard();
			newCardDetails.setCcNumber(bean.getCcNumber());
			newCardDetails.setCvv(bean.getCvv());
			newCardDetails.setFriendlyName(bean.getFriendlyName());
			newCardDetails.setExpDate(bean.getExpDate());
			newCardDetails.setBalance("0");
			List<CustomerAccountCard> cards = new ArrayList<CustomerAccountCard>();
			if(user.getCards() != null) {
				cards = user.getCards();
			}			
			cards.add(newCardDetails);
			user.setCards(cards);			
			mongoCustomerAccountRepo.save(user);
		}
		else {
			response.setStatus("Failed");
			response.setMessage("User does not exists");
			return response;
		}
		response.setStatus("Success");
		response.setMessage("New card added succesfully");
		return response;
	}
	
	@Operation(summary = "Create or update user account")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Details Updated Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerPersonalDetails.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping("/api/account/details/save")
	public ApiResponseBean saveAccountDetails(@RequestBody CustomerPersonalDetails bean) {
		ApiResponseBean response = new ApiResponseBean();
		Optional<CustomerAccountMongoDocumentBean> existingUser = mongoCustomerAccountRepo.findById(bean.getUserName());
		// Find if the user already exists, if yes update details
		// If not add one
		if(existingUser.isPresent()) {
			CustomerAccountMongoDocumentBean user = existingUser.get();
			CustomerAccountPersonal userPersonalDetails = bean.getDetails();
			user.setDetails(userPersonalDetails);
			
			mongoCustomerAccountRepo.save(user);
		}
		else {
			CustomerAccountMongoDocumentBean accountBody = new CustomerAccountMongoDocumentBean();
			accountBody.setUserName(bean.getUserName());
			CustomerAccountPersonal userPersonalDetails = bean.getDetails();
			accountBody.setDetails(userPersonalDetails);
			
			mongoCustomerAccountRepo.save(accountBody);
		}
		response.setStatus("Success");
		response.setMessage("user details added succesfully");
		return response;
	}
	
	@Operation(summary = "Fetch account details for userId")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account Details Retrieved Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerPersonalDetails.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@GetMapping("/api/account/details/{id}")
	public CustomerPersonalDetails getAccountDetails(@PathVariable("id") String id) {
		Optional<CustomerAccountMongoDocumentBean> acc = mongoCustomerAccountRepo.findById(id);
		CustomerPersonalDetails customer = new CustomerPersonalDetails();
		if(acc.isPresent()) {
			customer.setUserName(acc.get().getUserName());
			CustomerAccountPersonal personalDetails = acc.get().getDetails();
			customer.setDetails(personalDetails);
		} else {
			customer.setUserName(id);
			CustomerAccountPersonal personalDetails = new CustomerAccountPersonal();
			customer.setDetails(personalDetails);
		}
		return customer;
	}
	
	@Operation(summary = "Fetch all cards for userId")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account Cards Retrieved Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerCreditAccounts.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@GetMapping("/api/account/cards/{id}")
	public CustomerCreditAccounts getAccountsById(@PathVariable("id") String id) {
		Optional<CustomerAccountMongoDocumentBean> acc = mongoCustomerAccountRepo.findById(id);
		CustomerCreditAccounts res = new CustomerCreditAccounts();
		if(acc.isPresent()) {
			res.setUserName(acc.get().getUserName());
			res.setAccounts(acc.get().getCards());
		} else {
			res.setUserName(id);
			List<CustomerAccountCard> emptyCards = new ArrayList<CustomerAccountCard>();
			res.setAccounts(emptyCards);
		}
		return res;
	}
	
	@Operation(summary = "Fetch all account holders")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Accounts Retrieved Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = CustomerPersonalDetails.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@GetMapping("/api/account/all")
	public CustomerPersonalAccounts getAccountHolders() {
		// Fetch all accounts for the administrator view
		List<CustomerAccountMongoDocumentBean> accounts = mongoCustomerAccountRepo.findAll();
		ArrayList<CustomerPersonalDetails> list = new ArrayList<CustomerPersonalDetails>();
		CustomerPersonalAccounts res = new CustomerPersonalAccounts();
		for (int i = 0; i < accounts.size(); i++) {
			CustomerPersonalDetails cust = new CustomerPersonalDetails();
			cust.setUserName(accounts.get(i).getUserName());
			cust.setDetails(accounts.get(i).getDetails());
			list.add(cust);
		}
		res.setAccounts(list);
		return res;
	}
	
	// Most likely not needed
	/*
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/details/{id}")
	public CustomerPersonalDetails getAccountDetailsById(@PathVariable("id") String id) {
		Optional<CustomerAccountMongoDocumentBean> acc = mongoCustomerAccountRepo.findById(id);
		CustomerPersonalDetails res = new CustomerPersonalDetails();
		res.setUserName(acc.get().getUserName());
		res.setDetails(acc.get().getDetails());
		return res;
	}*/
	
}
