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


/**
 * @author CipherTrust.io
 *
 */
@RestController
public class CCAccountController {

	@Autowired
	private CustomerAccountMongoRepository mongoCustomerAccountRepo;
	//private AccountRepository accountRepository;
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/fakebank/account/card")
	public ApiResponseBean saveCreditAccount(@RequestBody NewCreditCardBean bean) {
		//MongoDb: Add the customer details to the DB
		ApiResponseBean response = new ApiResponseBean();
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
			System.out.println(user.toString());
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
		response.setMessage("new credit account added succesfully");
		return response;
	}
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/fakebank/account/personal")
	public ApiResponseBean saveAccountDetails(@RequestBody CustomerPersonalDetails bean) {
		//MongoDb: Add the customer details to the DB
		ApiResponseBean response = new ApiResponseBean();
		Optional<CustomerAccountMongoDocumentBean> existingUser = mongoCustomerAccountRepo.findById(bean.getUserName());
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
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/account/personal/{id}")
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
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/accounts/{id}")
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
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/account/holders")
	public CustomerPersonalAccounts getAccountHolders() {
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
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/details/{id}")
	public CustomerPersonalDetails getAccountDetailsById(@PathVariable("id") String id) {
		Optional<CustomerAccountMongoDocumentBean> acc = mongoCustomerAccountRepo.findById(id);
		CustomerPersonalDetails res = new CustomerPersonalDetails();
		res.setUserName(acc.get().getUserName());
		res.setDetails(acc.get().getDetails());
		return res;
	}
	
}
