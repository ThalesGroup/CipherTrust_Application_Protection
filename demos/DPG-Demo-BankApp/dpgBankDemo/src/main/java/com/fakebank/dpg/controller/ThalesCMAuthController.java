/**
 * 
 */
package com.fakebank.dpg.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.fakebank.dpg.bean.AuthSignInBean;
import com.fakebank.dpg.bean.TokenResponseBean;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * @author CipherTrust.io
 *
 */
@RestController
public class ThalesCMAuthController {

	@Autowired
	private RestTemplate restTemplate;
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/fakebank/signin")
	public TokenResponseBean login(@RequestBody AuthSignInBean credentials) {
		String BaseUrl = System.getenv("CMIP");
		System.out.println(BaseUrl);
		String URI_USERS = BaseUrl + "/api/v1/auth/tokens/";
		TokenResponseBean token = restTemplate.postForObject(URI_USERS, credentials, TokenResponseBean.class);
		
		return token;
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/fakebank/getUserDetails")
	public void getUserDetails(@RequestParam(name = "t") String token) {
		String BaseUrl = System.getenv("CMIP");
		System.out.println(BaseUrl);
		String url = BaseUrl + "/api/v1/auth/self/user/";
		
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		headers.set("Authorization", "Bearer " + token);

		HttpEntity<String> entity = new HttpEntity<String>("",headers);
		
		ResponseEntity<JsonNode> response = 
		         restTemplate.exchange(url, HttpMethod.GET, entity, JsonNode.class);
		JsonNode map = response.getBody();
	    String someValue = map.get("name").asText();
	    System.out.println(someValue);
	}
}
