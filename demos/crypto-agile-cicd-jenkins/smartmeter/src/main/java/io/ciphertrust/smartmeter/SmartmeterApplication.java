package io.ciphertrust.smartmeter;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class SmartmeterApplication {

	public static void main(String[] args) {
		SpringApplication.run(SmartmeterApplication.class, args);
	}

}
