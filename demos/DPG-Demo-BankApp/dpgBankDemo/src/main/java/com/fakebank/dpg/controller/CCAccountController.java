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

import com.fakebank.dpg.bean.CustomerAccountBean;
import com.fakebank.dpg.bean.CustomerCreditAccounts;
import com.fakebank.dpg.bean.CustomerPersonalDetails;
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
	@PostMapping("/api/fakebank/account")
	public String saveAccount(@RequestBody CustomerAccountBean bean) {
		//MongoDb: Add the customer details to the DB
		Optional<CustomerAccountMongoDocumentBean> existingUser = mongoCustomerAccountRepo.findById(bean.getUserName());
		if(existingUser.isPresent()) {
			CustomerAccountMongoDocumentBean user = existingUser.get();
			CustomerAccountPersonal userPersonalDetails = new CustomerAccountPersonal();
			userPersonalDetails.setDob(bean.getDob());
			userPersonalDetails.setMobile(bean.getMobileNumber());
			userPersonalDetails.setName(bean.getFullName());
			userPersonalDetails.setSsn(bean.getSsn());
			userPersonalDetails.setThalesId(bean.getIntCmId());
			user.setDetails(userPersonalDetails);
			
			CustomerAccountCard newCardDetails = new CustomerAccountCard();
			newCardDetails.setCcNumber(bean.getCcNumber());
			newCardDetails.setCvv(bean.getCcCvv());
			newCardDetails.setFriendlyName(bean.getAccFriendlyName());
			newCardDetails.setExpDate(bean.getCcExpiry());
			newCardDetails.setBalance("0");
			List<CustomerAccountCard> cards = user.getCards();
			cards.add(newCardDetails);
			user.setCards(cards);
			
			mongoCustomerAccountRepo.save(user);
		}
		else {
			CustomerAccountMongoDocumentBean accountBody = new CustomerAccountMongoDocumentBean();
			accountBody.setUserName(bean.getUserName());
			CustomerAccountPersonal userPersonalDetails = new CustomerAccountPersonal();
			userPersonalDetails.setDob(bean.getDob());
			userPersonalDetails.setMobile(bean.getMobileNumber());
			userPersonalDetails.setName(bean.getFullName());
			userPersonalDetails.setSsn(bean.getSsn());
			userPersonalDetails.setThalesId(bean.getIntCmId());
			accountBody.setDetails(userPersonalDetails);
			
			CustomerAccountCard newCardDetails = new CustomerAccountCard();
			newCardDetails.setCcNumber(bean.getCcNumber());
			newCardDetails.setCvv(bean.getCcCvv());
			newCardDetails.setFriendlyName(bean.getAccFriendlyName());
			newCardDetails.setExpDate(bean.getCcExpiry());
			newCardDetails.setBalance("0");
			List<CustomerAccountCard> cards = new ArrayList<CustomerAccountCard>();
			cards.add(newCardDetails);
			accountBody.setCards(cards);
			
			accountBody.setCreationDate(bean.getCreateDt());
			
			mongoCustomerAccountRepo.save(accountBody);
		}
		
		
		/*CustomerAccount newAccount = new CustomerAccount();
		
		newAccount.setAccountBalance(0);
		newAccount.setCcCvv(bean.getCcCvv());
		newAccount.setCcNumber(bean.getCcNumber());
		newAccount.setCcExpiry(bean.getCcExpiry());
		newAccount.setFullName(bean.getFullName());
		newAccount.setDob(bean.getDob());
		newAccount.setSsn(bean.getSsn());
		newAccount.setMobileNumber(bean.getMobileNumber());
		newAccount.setUserName(bean.getUserName());
		newAccount.setCustomerCmId(bean.getIntCmId());
		
		CustomerAccount createdAccount = accountRepository.createAccount(newAccount);*/
		return "new credit account added succesfully";
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/accounts/{id}")
	public CustomerCreditAccounts getAccountsById(@PathVariable("id") String id) {
		Optional<CustomerAccountMongoDocumentBean> acc = mongoCustomerAccountRepo.findById(id);
		CustomerCreditAccounts res = new CustomerCreditAccounts();
		res.setUserName(acc.get().getUserName());
		res.setAccounts(acc.get().getCards());
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
