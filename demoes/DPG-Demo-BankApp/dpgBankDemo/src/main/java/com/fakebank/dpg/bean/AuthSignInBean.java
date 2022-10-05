/**
 * 
 */
package com.fakebank.dpg.bean;

/**
 * @author CipherTrust.io
 *
 */
public class AuthSignInBean {

	private String grant_type;
	private String username;
	private String password;

	public String getGrant_type() {
		return grant_type;
	}

	public void setGrant_type(String grant_type) {
		this.grant_type = grant_type;
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

	public AuthSignInBean(String grant_type, String username, String password) {
		super();
		this.grant_type = grant_type;
		this.username = username;
		this.password = password;
	}

	@Override
	public String toString() {
		return "AuthSignInBean [grant_type=" + grant_type + ", username=" + username + ", password=" + password + "]";
	}

	public AuthSignInBean() {
		super();
		// TODO Auto-generated constructor stub
	}
}
