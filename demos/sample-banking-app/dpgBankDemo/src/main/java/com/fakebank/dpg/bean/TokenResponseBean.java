/**
 * 
 */
package com.fakebank.dpg.bean;

/**
 * @author CipherTest.io
 *
 */
public class TokenResponseBean {
	private String jwt;
	private int duration;
	private String token_type;
	private String client_id;
	private String refresh_token_id;
	private String refresh_token;

	@Override
	public String toString() {
		return "TokenResponseBean [jwt=" + jwt + ", duration=" + duration + ", token_type=" + token_type
				+ ", client_id=" + client_id + ", refresh_token_id=" + refresh_token_id + ", refresh_token="
				+ refresh_token + "]";
	}

	public TokenResponseBean(String jwt, int duration, String token_type, String client_id, String refresh_token_id,
			String refresh_token) {
		super();
		this.jwt = jwt;
		this.duration = duration;
		this.token_type = token_type;
		this.client_id = client_id;
		this.refresh_token_id = refresh_token_id;
		this.refresh_token = refresh_token;
	}

	public String getJwt() {
		return jwt;
	}

	public void setJwt(String jwt) {
		this.jwt = jwt;
	}

	public int getDuration() {
		return duration;
	}

	public void setDuration(int duration) {
		this.duration = duration;
	}

	public String getToken_type() {
		return token_type;
	}

	public void setToken_type(String token_type) {
		this.token_type = token_type;
	}

	public String getClient_id() {
		return client_id;
	}

	public void setClient_id(String client_id) {
		this.client_id = client_id;
	}

	public String getRefresh_token_id() {
		return refresh_token_id;
	}

	public void setRefresh_token_id(String refresh_token_id) {
		this.refresh_token_id = refresh_token_id;
	}

	public String getRefresh_token() {
		return refresh_token;
	}

	public void setRefresh_token(String refresh_token) {
		this.refresh_token = refresh_token;
	}

	public TokenResponseBean() {
		super();
		// TODO Auto-generated constructor stub
	}
}
