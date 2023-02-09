package com.fakebank.dpg.bean;

public class CMCreateUserBean {
	private String email;
	private String name;
	private String username;
	private String password;

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public CMCreateUserBean() {
		super();
		// TODO Auto-generated constructor stub
	}

	public CMCreateUserBean(String email, String name, String username, String password) {
		super();
		this.email = email;
		this.name = name;
		this.username = username;
		this.password = password;
	}

	@Override
	public String toString() {
		return "CMCreateUserBean [email=" + email + ", name=" + name + ", username=" + username + ", password="
				+ password + "]";
	}
}
