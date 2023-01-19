package com.fakebank.dpg.bean;

public class NewAccountBean {
	private String userName;
	private String password;
	private AccountDetailsUpdateRequestBean personal;
	private ExistingCardBean card;

	public String getUserName() {
		return userName;
	}

	public void setUsername(String userName) {
		this.userName = userName;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public AccountDetailsUpdateRequestBean getPersonal() {
		return personal;
	}

	public void setPersonal(AccountDetailsUpdateRequestBean personal) {
		this.personal = personal;
	}

	public ExistingCardBean getCard() {
		return card;
	}

	public void setCard(ExistingCardBean card) {
		this.card = card;
	}

	public NewAccountBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public NewAccountBean(String userName, String password, AccountDetailsUpdateRequestBean personal,
			ExistingCardBean card) {
		super();
		this.userName = userName;
		this.password = password;
		this.personal = personal;
		this.card = card;
	}

	@Override
	public String toString() {
		return "NewAccountBean [userName=" + userName + ", password=" + password + ", personal=" + personal + ", card="
				+ card + "]";
	}
}
