/**
 * 
 */
package com.fakebank.dpg.controller;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.fakebank.dpg.bean.ApiResponseBean;
import com.fakebank.dpg.bean.AuthSignInBean;
import com.fakebank.dpg.bean.CMAddUsersToUserSetBean;
import com.fakebank.dpg.bean.CMCreateTokenBean;
import com.fakebank.dpg.bean.CMCreateUserBean;
import com.fakebank.dpg.bean.NewAccountBean;
import com.fakebank.dpg.bean.TokenResponseBean;
import com.fakebank.dpg.model.CustomerAccountCard;
import com.fakebank.dpg.model.CustomerAccountMongoDocumentBean;
import com.fakebank.dpg.model.CustomerAccountPersonal;
import com.fakebank.dpg.repository.CustomerAccountMongoRepository;
import com.fasterxml.jackson.databind.JsonNode;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

/**
 * @author CipherTrust.io
 * This is the main controller file for user creation and login API calls
 * CM = CipherTrust Manager
 */
@RestController
public class ThalesCMAuthController {

	@Autowired
	private RestTemplate restTemplate;
	
	@Autowired
	private CustomerAccountMongoRepository mongoCustomerAccountRepo;
	
	@Operation(summary = "Create a new credit card account")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account Created Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = NewAccountBean.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping("/api/user/create")
	public ApiResponseBean saveOrUpdateUser(@RequestBody NewAccountBean bean) {
		// This API controller is invoked by the sign up page on the Banking Application front end
		
		ApiResponseBean response = new ApiResponseBean();
		
		// First step is to add User to CM - we need JWT for any further DPG policies to apply
		// Get CM IP and credentials from system environment - passed via docker invocation
		String cmUrl = System.getenv("CM_URL");
		String cmUser = System.getenv("CM_USERNAME");
		String cmUserPwd = System.getenv("CM_PASSWORD");
		String cmUserSetId = System.getenv("CM_USER_SET_ID");
		
		// Acquire JWT from CM for the newly created user
		CMCreateTokenBean tokenRequest = new CMCreateTokenBean("password", cmUser, cmUserPwd);
		HttpHeaders tokenRequestHeaders = new HttpHeaders();
		tokenRequestHeaders.setContentType(MediaType.APPLICATION_JSON);
	    HttpEntity<CMCreateTokenBean> tokenRequestEntity = new HttpEntity<CMCreateTokenBean>(tokenRequest,tokenRequestHeaders);
	    ResponseEntity<JsonNode> tokenResponse;
	    try {
	    	// API call to CM for acquiring JWT
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
		request.setEmail(bean.getUserName() + "@local");
		request.setName(bean.getPersonal().getFullName());
		request.setPassword(bean.getPassword());
		request.setUsername(bean.getUserName());
		
		HttpEntity<CMCreateUserBean> entity = new HttpEntity<CMCreateUserBean>(request,headers);
		JsonNode responseUserCreate = null;
		try {
			responseUserCreate = restTemplate.exchange(
					URI_USER_CREATE, 
					HttpMethod.POST, 
					entity,
					JsonNode.class).getBody();
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
		users.add(bean.getUserName());
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
		Calendar c = Calendar.getInstance();
		DateFormat dateFormat = new SimpleDateFormat("mm/dd/yyyy");  
        String createDate = dateFormat.format(c.getTime());
		
        CustomerAccountMongoDocumentBean userBean = new CustomerAccountMongoDocumentBean();
		userBean.setUserName(bean.getUserName());
		userBean.setCreationDate(createDate);
		
		CustomerAccountCard card = new CustomerAccountCard();
		card.setBalance("0");
		card.setCcNumber(bean.getCard().getCcNumber());
		card.setCvv(bean.getCard().getCvv());
		card.setExpDate(bean.getCard().getExpDate());
		card.setFriendlyName(bean.getCard().getFriendlyName());
		List<CustomerAccountCard> cards = new ArrayList<CustomerAccountCard>();
		cards.add(card);		
		userBean.setCards(cards);
		
		CustomerAccountPersonal acc = new CustomerAccountPersonal();
		acc.setDob(bean.getPersonal().getDob());
		acc.setMobile(bean.getPersonal().getMobileNumber());
		acc.setName(bean.getPersonal().getFullName());
		acc.setSsn(bean.getPersonal().getSsn());
		acc.setThalesId(responseUserCreate.get("user_id").asText());
		userBean.setDetails(acc);
		
		try {
			mongoCustomerAccountRepo.save(userBean);
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
	
	
	@Operation(summary = "Login user")
	@ApiResponses(value = {
		@ApiResponse(responseCode = "200", description = "Account Authenticated Succesfully", content = {
			@Content(mediaType = "application/json", schema = @Schema(implementation = AuthSignInBean.class)) }),
		@ApiResponse(responseCode = "404", description = "Resource not found", content = @Content) })
	@CrossOrigin(origins = "*")
	@PostMapping("/api/user/signin")
	public TokenResponseBean login(@RequestBody AuthSignInBean credentials) {
		String BaseUrl = System.getenv("CM_URL");
		System.out.println(BaseUrl);
		String URI_USERS = BaseUrl + "/api/v1/auth/tokens/";
		TokenResponseBean token = restTemplate.postForObject(URI_USERS, credentials, TokenResponseBean.class);
		
		return token;
	}
	
	// This might be useless...we will see
	/*
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
	}*/
}
