/**
 * 
 */
package com.fakebank.dpg.model;

import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

/**
 * @author CipherTrust.io
 *
 */
@Document(collection = "accounts")
public class CustomerAccountMongoDocumentBean {

	@Id
	private String userName;
	private String creationDate;
	private List<CustomerAccountCard> cards;
	private CustomerAccountPersonal details;

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public String getCreationDate() {
		return creationDate;
	}

	public void setCreationDate(String creationDate) {
		this.creationDate = creationDate;
	}

	public List<CustomerAccountCard> getCards() {
		return cards;
	}

	public void setCards(List<CustomerAccountCard> cards) {
		this.cards = cards;
	}

	public CustomerAccountPersonal getDetails() {
		return details;
	}

	public void setDetails(CustomerAccountPersonal details) {
		this.details = details;
	}

	@Override
	public String toString() {
		return "CustomerAccountMongoDocumentBean [userName=" + userName + ", creationDate=" + creationDate + ", cards="
				+ cards + ", details=" + details + "]";
	}
}
