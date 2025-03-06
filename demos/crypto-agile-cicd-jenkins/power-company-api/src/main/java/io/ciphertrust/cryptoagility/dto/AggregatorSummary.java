package io.ciphertrust.cryptoagility.dto;

public class AggregatorSummary {

    private Long aggregatorId;
    private String name;
    private String location;
    private double totalEnergyConsumption;
    private String status;
    private int totalSmartMeters;

    // Constructors, Getters, and Setters

    public AggregatorSummary() {
    }

    public AggregatorSummary(Long aggregatorId, String name, String location, double totalEnergyConsumption, String status, int totalSmartMeters) {
        this.aggregatorId = aggregatorId;
        this.name = name;
        this.location = location;
        this.totalEnergyConsumption = totalEnergyConsumption;
        this.status = status;
        this.totalSmartMeters = totalSmartMeters;
    }

    // Getters and Setters
    public Long getAggregatorId() {
        return aggregatorId;
    }

    public void setAggregatorId(Long aggregatorId) {
        this.aggregatorId = aggregatorId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public double getTotalEnergyConsumption() {
        return totalEnergyConsumption;
    }

    public void setTotalEnergyConsumption(double totalEnergyConsumption) {
        this.totalEnergyConsumption = totalEnergyConsumption;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public int getTotalSmartMeters() {
        return totalSmartMeters;
    }

    public void setTotalSmartMeters(int totalSmartMeters) {
        this.totalSmartMeters = totalSmartMeters;
    }
}