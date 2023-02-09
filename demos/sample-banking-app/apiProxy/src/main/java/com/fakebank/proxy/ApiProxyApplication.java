package com.fakebank.proxy;

import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;

@SpringBootApplication
@OpenAPIDefinition
public class ApiProxyApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApiProxyApplication.class, args);
	}

	@Bean
	public RestTemplate restTemplate() throws KeyStoreException, NoSuchAlgorithmException, KeyManagementException {
		RestTemplate restTemplate = new RestTemplate();
	    return restTemplate;
	}
}
