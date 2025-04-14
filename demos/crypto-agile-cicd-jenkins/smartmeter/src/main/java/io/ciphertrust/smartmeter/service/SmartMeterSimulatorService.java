package io.ciphertrust.smartmeter.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import io.ciphertrust.smartmeter.dto.SmartMeterDataDto;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Random;

@Service
public class SmartMeterSimulatorService {
    private static final Logger logger = LoggerFactory.getLogger(SmartMeterSimulatorService.class);
    private static final DateTimeFormatter TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss");
    private static final Random RANDOM = new Random();

    private final RestTemplate restTemplate;

    @Value("${app.api.url}")
    private String apiUrl;

    @Value("${app.api.user-id}")
    private Long userId;

    @Value("${app.api.smart-meter-id}")
    private Long smartMeterId;

    @Value("${app.simulation.enabled}")
    private boolean simulationEnabled;

    public SmartMeterSimulatorService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Scheduled(initialDelayString = "${app.simulation.initial-delay}", fixedRateString = "${app.simulation.fixed-rate}")
    public void sendTelemetryData() {
        if (!simulationEnabled) {
            logger.debug("Simulation is disabled - skipping execution");
            return;
        }

        try {
            SmartMeterDataDto data = generateSimulatedData();
            
            logger.debug("Sending simulated data for user {} and smart meter {}: {}", 
                userId, smartMeterId, data);

            ResponseEntity<String> response = restTemplate.postForEntity(apiUrl, data, String.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                logger.info("Data sent successfully for user {} and smart meter {}", 
                    userId, smartMeterId);
            } else {
                logger.error("Failed to send data. Response code: {}", 
                    response.getStatusCodeValue());
            }
        } catch (Exception e) {
            logger.error("Error sending telemetry data", e);
        }
    }

    private SmartMeterDataDto generateSimulatedData() {
        SmartMeterDataDto data = new SmartMeterDataDto();
        SmartMeterDataDto.SmartMeterDto smartMeter = new SmartMeterDataDto.SmartMeterDto();
        
        // Set smart meter ID
        smartMeter.setId(smartMeterId);
        
        // Generate simulated values
        data.setTotalEnergyConsumption(100 + RANDOM.nextDouble() * 50);
        data.setInstantaneousPowerUsage(2 + RANDOM.nextDouble() * 3);
        data.setVoltage(220 + RANDOM.nextDouble() * 20);
        data.setCurrent(5 + RANDOM.nextDouble() * 5);
        data.setPowerFactor(0.9 + RANDOM.nextDouble() * 0.1);
        data.setFrequency(50 + RANDOM.nextDouble() * 2);
        data.setTimestamp(LocalDateTime.now().format(TIMESTAMP_FORMAT));
        data.setTemperature(20 + RANDOM.nextDouble() * 10);
        data.setHumidity(40 + RANDOM.nextDouble() * 30);
        data.setDetailedConsumptionIntervals(
            "0-15min: " + (0.5 + RANDOM.nextDouble() * 0.5) + "kWh");
        data.setSmartMeter(smartMeter);
        
        return data;
    }
}