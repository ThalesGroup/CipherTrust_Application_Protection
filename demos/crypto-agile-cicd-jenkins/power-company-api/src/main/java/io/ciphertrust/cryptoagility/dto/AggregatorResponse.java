package io.ciphertrust.cryptoagility.dto;

import io.ciphertrust.cryptoagility.entity.SmartMeter;

import java.time.LocalDateTime;
import java.util.List;

public class AggregatorResponse {

    private Long id;
    private String currentStatus;
    private LocalDateTime statusUpdateTime;
    private String location;
    private List<SmartMeter> smartMeters;
    private int smartMeterCount;

    // Constructors, Getters, and Setters

    public AggregatorResponse() {
    }

    public AggregatorResponse(Long id, String currentStatus, LocalDateTime statusUpdateTime, String location, List<SmartMeter> smartMeters) {
        this.id = id;
        this.currentStatus = currentStatus;
        this.statusUpdateTime = statusUpdateTime;
        this.location = location;
        this.smartMeters = smartMeters;
        this.smartMeterCount = smartMeters != null ? smartMeters.size() : 0;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCurrentStatus() {
        return currentStatus;
    }

    public void setCurrentStatus(String currentStatus) {
        this.currentStatus = currentStatus;
    }

    public LocalDateTime getStatusUpdateTime() {
        return statusUpdateTime;
    }

    public void setStatusUpdateTime(LocalDateTime statusUpdateTime) {
        this.statusUpdateTime = statusUpdateTime;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public List<SmartMeter> getSmartMeters() {
        return smartMeters;
    }

    public void setSmartMeters(List<SmartMeter> smartMeters) {
        this.smartMeters = smartMeters;
        this.smartMeterCount = smartMeters != null ? smartMeters.size() : 0;
    }

    public int getSmartMeterCount() {
        return smartMeterCount;
    }

    public void setSmartMeterCount(int smartMeterCount) {
        this.smartMeterCount = smartMeterCount;
    }
}