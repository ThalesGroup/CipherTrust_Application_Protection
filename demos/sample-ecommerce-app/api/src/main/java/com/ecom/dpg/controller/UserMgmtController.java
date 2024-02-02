package com.ecom.dpg.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.ecom.dpg.bean.ApiResponseBean;
import com.ecom.dpg.bean.ApiResponseWithUserBean;
import com.ecom.dpg.bean.CMAddUsersToUserSetBean;
import com.ecom.dpg.bean.CMCreateTokenBean;
import com.ecom.dpg.bean.CMCreateUserBean;
import com.ecom.dpg.bean.CreateUserApiRequestBean;
import com.ecom.dpg.model.AddressDocument;
import com.ecom.dpg.model.UserDocument;
import com.ecom.dpg.repository.UserMongoRepository;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
@RestController
public class UserMgmtController {

	@Autowired
	private UserMongoRepository userRepo;
	
	@Autowired
	private RestTemplate restTemplate;
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/user-mgmt/user/create")
	public ApiResponseBean saveOrUpdateUser(@RequestBody CreateUserApiRequestBean bean) {
		ApiResponseBean response = new ApiResponseBean();
		
		//Add User to CM
		//Get CM IP and credentials from system environment - passed via docker invocation
		String cmUrl = System.getenv("CM_IP");
		String cmUser = System.getenv("CM_USERNAME");
		String cmUserPwd = System.getenv("CM_PASSWORD");
		String cmUserSetId = System.getenv("CM_USER_SET_ID");
		
		//Acquire JWT from CM
		CMCreateTokenBean tokenRequest = new CMCreateTokenBean("password", cmUser, cmUserPwd);
		HttpHeaders tokenRequestHeaders = new HttpHeaders();
		tokenRequestHeaders.setContentType(MediaType.APPLICATION_JSON);
	    HttpEntity<CMCreateTokenBean> tokenRequestEntity = new HttpEntity<CMCreateTokenBean>(tokenRequest,tokenRequestHeaders);
	    ResponseEntity<JsonNode> tokenResponse;
	    try {
	    	tokenResponse = 
	    			restTemplate.exchange(cmUrl + "/api/v1/auth/tokens", HttpMethod.POST, tokenRequestEntity, JsonNode.class);
		} catch (Exception ex) {
			response.setStatus("failed to acquire JWT");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		JsonNode map = tokenResponse.getBody();
		String jwt = map.get("jwt").asText();
		
		//Create User CM API endpoint
		String URI_USER_CREATE = cmUrl + "/api/v1/usermgmt/users";
		
		//Add auth header
		HttpHeaders headers = new HttpHeaders();
		headers.add("Authorization", "Bearer " + jwt);
		
		//Create Request Object
		CMCreateUserBean request = new CMCreateUserBean();
		request.setEmail(bean.getEmail());
		request.setName(bean.getFullName());
		request.setPassword(bean.getPassword());
		request.setUsername(bean.getUsername());
		
		HttpEntity<CMCreateUserBean> entity = new HttpEntity<CMCreateUserBean>(request,headers);
		try {
			restTemplate.exchange(
					URI_USER_CREATE, 
					HttpMethod.POST, 
					entity,
					JsonNode.class);
		} catch (Exception ex) {
			response.setStatus("failed to create user on Ciphertrust Manager");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		//Add User to the right user set
		String URI_ADD_USER_TO_SET = cmUrl + "/api/v1/data-protection/user-sets/" + cmUserSetId + "/users";
		//Create Request Object
		CMAddUsersToUserSetBean requestBean = new CMAddUsersToUserSetBean();
		List<String> users = new ArrayList<String>();
		users.add(bean.getUsername());
		requestBean.setUsers(users);
		HttpEntity<CMAddUsersToUserSetBean> createUserEntity = new HttpEntity<CMAddUsersToUserSetBean>(requestBean,headers);
		try {
			restTemplate.exchange(
					URI_ADD_USER_TO_SET, 
					HttpMethod.POST, 
					createUserEntity,
					JsonNode.class);
		} catch (Exception ex) {
			response.setStatus("failed to add user to the userset on Ciphertrust Manager");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		//Add User to Local DB
		UserDocument newUser = new UserDocument();
		AddressDocument newAddress = new AddressDocument(
				bean.getAddress().getStreet(), 
				bean.getAddress().getUnit(), 
				bean.getAddress().getCity(),
				bean.getAddress().getState(),
				bean.getAddress().getZipCode(),
				bean.getAddress().getCountry());
		newUser.setAddress(newAddress);
		newUser.setEmail(bean.getEmail());
		newUser.setFullName(bean.getFullName());
		newUser.setMobileNum(bean.getMobileNum());
		newUser.setUsername(bean.getUsername());
		try {
		 userRepo.save(newUser);
		} catch (Exception ex) {
			response.setStatus("internal server error - failed to save data");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		response.setStatus("success");
		response.setMessage("User addedd succesfully");
		response.setDetails("");
		
		return response;
	}
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/user-mgmt/user/login")
	public ApiResponseBean authenticate(@RequestBody CMCreateTokenBean bean) {
		ApiResponseBean response = new ApiResponseBean();
		UserDocument user; 
		//Check user in local Mongo DB
		try {
			user = userRepo.findUserByUserName(bean.getUsername());
			if(user == null) {
				response.setStatus("user not found in database");
				response.setMessage("");
				response.setDetails("");
				return response;
			}
		} catch (Exception ex) {
			response.setStatus("internal server error - failed to retrieve user data");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		//We have found the user in local DB ... now auth with CM and get JWT
		//Get CM IP and credentials from system environment - passed via docker invocation
		String cmUrl = System.getenv("CM_IP");
		String cmUser = bean.getUsername();
		String cmUserPwd = bean.getPassword();
		
		//Acquire JWT from CM
		CMCreateTokenBean tokenRequest = new CMCreateTokenBean("password", cmUser, cmUserPwd);
		HttpHeaders tokenRequestHeaders = new HttpHeaders();
		tokenRequestHeaders.setContentType(MediaType.APPLICATION_JSON);
	    HttpEntity<CMCreateTokenBean> tokenRequestEntity = new HttpEntity<CMCreateTokenBean>(tokenRequest,tokenRequestHeaders);
	    ResponseEntity<JsonNode> tokenResponse;
	    try {
	    	tokenResponse = 
	    			restTemplate.exchange(cmUrl + "/api/v1/auth/tokens", HttpMethod.POST, tokenRequestEntity, JsonNode.class);
		} catch (Exception ex) {
			response.setStatus("failed to acquire JWT");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		JsonNode map = tokenResponse.getBody();
		String jwt = map.get("jwt").asText();
		
		response.setStatus("success");
		response.setMessage(jwt);
		response.setDetails(user.getUserId());
		
		return response;
	}
	
	@CrossOrigin(origins = "*")
	@PostMapping("/api/user-mgmt/admin/login")
	public ApiResponseBean adminLogin(@RequestBody CMCreateTokenBean bean) {
		ApiResponseBean response = new ApiResponseBean();
		
		//Get CM IP and credentials from system environment - passed via docker invocation
		String cmUrl = System.getenv("CM_IP");
		String cmUser = bean.getUsername();
		String cmUserPwd = bean.getPassword();
		
		//Acquire JWT from CM
		CMCreateTokenBean tokenRequest = new CMCreateTokenBean("password", cmUser, cmUserPwd);
		HttpHeaders tokenRequestHeaders = new HttpHeaders();
		tokenRequestHeaders.setContentType(MediaType.APPLICATION_JSON);
	    HttpEntity<CMCreateTokenBean> tokenRequestEntity = new HttpEntity<CMCreateTokenBean>(tokenRequest,tokenRequestHeaders);
	    ResponseEntity<JsonNode> tokenResponse;
	    try {
	    	tokenResponse = 
	    			restTemplate.exchange(cmUrl + "/api/v1/auth/tokens", HttpMethod.POST, tokenRequestEntity, JsonNode.class);
		} catch (Exception ex) {
			response.setStatus("failed to acquire JWT");
			response.setMessage(ex.getMessage());
			response.setDetails("");
			return response;
		}
		
		JsonNode map = tokenResponse.getBody();
		String jwt = map.get("jwt").asText();
		
		response.setStatus("success");
		response.setMessage(jwt);
		response.setDetails("");
		
		return response;
	}
	
	@CrossOrigin(origins = "*")
	@GetMapping("/api/user-mgmt/user/{id}")
	public ApiResponseWithUserBean fetchUserById(@PathVariable("id") String id) {
		ApiResponseWithUserBean response = new ApiResponseWithUserBean();
		 try {
			Optional<UserDocument> userOptional = userRepo.findById(id);
			if(userOptional.isPresent()) {
				UserDocument user = userOptional.get();
				response.setStatus("success");
				response.setMessage("User retrieved sucessfully");
				response.setUser(user);
				return response;
			} else {
				response.setStatus("internal server error - failed to retrieve user data");
				response.setMessage("user not found with teh given ID");
				response.setUser(null);
				return response;
			}
		} catch (Exception ex) {
			response.setStatus("internal server error - failed to retrieve user data");
			response.setMessage(ex.getMessage());
			response.setUser(null);
			return response;
		}
	}
}
