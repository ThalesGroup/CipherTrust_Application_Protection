package io.ciphertrust.smartmeter.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

@Data
@ToString
@NoArgsConstructor
@AllArgsConstructor
public class SmartMeterDataDto {
    private String totalEnergyConsumption;
    private String instantaneousPowerUsage;
    private String voltage;
    private String current;
    private String powerFactor;
    private String frequency;
    private String timestamp;
    private String temperature;
    private String humidity;
    private String detailedConsumptionIntervals;
    private SmartMeterDto smartMeter;
    
    @Data
    public static class SmartMeterDto {
        private Long id;
    }
}