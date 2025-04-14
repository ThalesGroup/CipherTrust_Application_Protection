package io.ciphertrust.smartmeter.dto;

import lombok.Data;

@Data
public class SmartMeterDataDto {
    private double totalEnergyConsumption;
    private double instantaneousPowerUsage;
    private double voltage;
    private double current;
    private double powerFactor;
    private double frequency;
    private String timestamp;
    private double temperature;
    private double humidity;
    private String detailedConsumptionIntervals;
    private SmartMeterDto smartMeter;
    
    @Data
    public static class SmartMeterDto {
        private Long id;
    }
}