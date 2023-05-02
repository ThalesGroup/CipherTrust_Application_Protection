package com.fakebank.dpg.bean;

import java.util.List;

public class CMAddUsersToUserSetBean {
	private List<String> users;

	public List<String> getUsers() {
		return users;
	}

	public void setUsers(List<String> users) {
		this.users = users;
	}

	public CMAddUsersToUserSetBean(List<String> users) {
		super();
		this.users = users;
	}

	@Override
	public String toString() {
		return "CMAddUsersToUserSetBean [users=" + users + "]";
	}

	public CMAddUsersToUserSetBean() {
		super();
		// TODO Auto-generated constructor stub
	}
}
