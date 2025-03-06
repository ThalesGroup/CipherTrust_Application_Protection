package io.ciphertrust.cryptoagility;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.YearMonth;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import io.ciphertrust.cryptoagility.entity.*;
import io.ciphertrust.cryptoagility.service.*;

@SpringBootApplication
public class CryptoagilityApplication {

	@Autowired
    private AggregatorService aggregatorService;

    @Autowired
    private SmartMeterService smartMeterService;

    @Autowired
    private SmartMeterDataService smartMeterDataService;

    @Autowired
    private UserService userService;

	public static void main(String[] args) {
		SpringApplication.run(CryptoagilityApplication.class, args);
	}

	@Bean
    public CommandLineRunner initDatabase() {
        return args -> {
            // Create Aggregators
            Aggregator aggregator1 = new Aggregator();
            aggregator1.setName("Crestline-Ottawa");
            aggregator1.setLocation("Ottawa");
            aggregator1.setCurrentStatus("Active");
            aggregator1.setStatusUpdateTime(LocalDateTime.now());
            aggregator1 = aggregatorService.createAggregator(aggregator1);

            Aggregator aggregator2 = new Aggregator();
            aggregator2.setName("Crestline-Toronto");
            aggregator2.setLocation("Toronto");
            aggregator2.setCurrentStatus("Active");
            aggregator2.setStatusUpdateTime(LocalDateTime.now());
            aggregator2 = aggregatorService.createAggregator(aggregator2);

            // Create Smart Meters
            SmartMeter smartMeter1 = new SmartMeter();
            smartMeter1.setMeterId("SM-OTT-12345");
            smartMeter1.setLocation("Stittsville");
            smartMeter1.setManufacturer("Crestline");
            smartMeter1.setInstallationDate(LocalDate.now());
            smartMeter1.setAggregator(aggregator1);
            smartMeter1 = smartMeterService.saveSmartMeter(smartMeter1);

            SmartMeter smartMeter2 = new SmartMeter();
            smartMeter2.setMeterId("SM-TORONTO-67890");
            smartMeter2.setLocation("Don Valley Parkway");
            smartMeter2.setManufacturer("Crestline");
            smartMeter2.setInstallationDate(LocalDate.now());
            smartMeter2.setAggregator(aggregator1);
            smartMeter2 = smartMeterService.saveSmartMeter(smartMeter2);

			aggregatorService.addSmartMeterToAggregator(aggregator1.getId(), smartMeter1.getId());
			aggregatorService.addSmartMeterToAggregator(aggregator2.getId(), smartMeter2.getId());

            // Create Smart Meter Data
            SmartMeterData smartMeterData1 = new SmartMeterData();
            smartMeterData1.setTotalEnergyConsumption(50.5);
            smartMeterData1.setInstantaneousPowerUsage(2.5);
            smartMeterData1.setVoltage(220.0);
            smartMeterData1.setCurrent(10.0);
            smartMeterData1.setPowerFactor(0.9);
            smartMeterData1.setFrequency(60.0);
            smartMeterData1.setTimestamp(LocalDateTime.now());
            smartMeterData1.setTemperature(25.0);
            smartMeterData1.setHumidity(50.0);
            smartMeterData1.setDetailedConsumptionIntervals("{\"intervals\": [{\"start\": \"12:00\", \"end\": \"12:30\", \"usage\": 1.5}]}");
            smartMeterData1.setSmartMeter(smartMeter1);
            smartMeterData1 = smartMeterDataService.saveSmartMeterData(smartMeterData1);

            // Create User Payment Info
            UserPayment userPaymentInfo1 = new UserPayment();
            userPaymentInfo1.setCardNumber("9876543210987654");
            userPaymentInfo1.setCardType("Visa");
            userPaymentInfo1.setCvv("123");
            userPaymentInfo1.setExpirationDate(LocalDate.of(2025, 12, 31));

			UserPayment userPaymentInfo2 = new UserPayment();
            userPaymentInfo2.setCardNumber("1234567890123456");
            userPaymentInfo2.setCardType("MasterCard");
            userPaymentInfo2.setCvv("456");
            userPaymentInfo2.setExpirationDate(LocalDate.of(2025, 12, 31));

            // Create Users
            User user1 = new User();
            user1.setName("John Doe");
            user1.setUsername("johndoe");
            user1.setPassword("password123");
            user1.setEmail("john.doe@example.com");
            user1.setContactNum("1234567890");
            user1.setAddressLineOne("123 Main St");
            user1.setAddressLineTwo("Apt 4B");
            user1.setCity("Stittsville");
            user1.setState("ON");
            user1.setCountry("CAN");
            user1.setZip("A1B 2C3");
            user1.setPaymentInfo(userPaymentInfo1);
            //user1.setSmartMeter(smartMeter1);
            user1 = userService.createUser(user1);

			User user2 = new User();
            user2.setName("Jane Doe");
            user2.setUsername("janedoe");
            user2.setPassword("password123");
            user2.setEmail("jane.doe@example.com");
            user2.setContactNum("1234567890");
            user2.setAddressLineOne("123 Upper St");
            user2.setAddressLineTwo("Apt 101");
            user2.setCity("Toronto");
            user2.setState("ON");
            user2.setCountry("CAN");
            user2.setZip("X1Y 2Z3");
            user2.setPaymentInfo(userPaymentInfo2);
            //user2.setSmartMeter(smartMeter2);
            user2 = userService.createUser(user2);

			userService.addSmartMeter(user1.getId(), smartMeter1);
			userService.addSmartMeter(user2.getId(), smartMeter2);
			userService.addPaymentInfo(user1.getId(), userPaymentInfo1);
			userService.addPaymentInfo(user2.getId(), userPaymentInfo2);

            // Create User Bills
            UserBill userBills1 = new UserBill();
            userBills1.setAmountPaid(100.0);
            userBills1.setStatus("paid");
            userBills1.setMonthYear(YearMonth.of(2025, 01));

			UserBill userBills2 = new UserBill();
            userBills2.setAmountPaid(110.0);
            userBills2.setStatus("paid");
            userBills2.setMonthYear(YearMonth.of(2025, 02));

			UserBill userBills3 = new UserBill();
            userBills3.setAmountPaid(90.0);
            userBills3.setStatus("due");
            userBills3.setMonthYear(YearMonth.of(2025, 03));

			userService.addBillToUser(user1.getId(), userBills1);
			userService.addBillToUser(user1.getId(), userBills2);
			userService.addBillToUser(user1.getId(), userBills3);

            System.out.println("Database initialized with sample data.");
        };
    }
}
