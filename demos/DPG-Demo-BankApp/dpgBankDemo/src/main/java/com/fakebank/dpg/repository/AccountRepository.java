/**
 * 
 */
package com.fakebank.dpg.repository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.fakebank.dpg.model.CustomerAccount;


/**
 * @author CipherTrust.io
 *
 */
@Repository
public class AccountRepository {
	@Autowired
	private DynamoDBMapper dynamoDBMapper;

	public CustomerAccount createAccount(CustomerAccount customer) {
		dynamoDBMapper.save(customer);
		return customer;
	}

	public CustomerAccount getCustomerById(String customerId) {
		return dynamoDBMapper.load(CustomerAccount.class, customerId);
	}
}