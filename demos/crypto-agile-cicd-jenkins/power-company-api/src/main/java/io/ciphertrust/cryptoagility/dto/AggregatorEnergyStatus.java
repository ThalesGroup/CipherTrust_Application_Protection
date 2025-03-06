package io.ciphertrust.cryptoagility.dto;

public class AggregatorEnergyStatus {

    private Long aggregatorId;
    private double totalEnergyConsumption;
    private String status;

    public AggregatorEnergyStatus() {
    }

    public AggregatorEnergyStatus(Long aggregatorId, double totalEnergyConsumption, String status) {
        this.aggregatorId = aggregatorId;
        this.totalEnergyConsumption = totalEnergyConsumption;
        this.status = status;
    }

    // Getters and Setters
    public Long getAggregatorId() {
        return aggregatorId;
    }

    public void setAggregatorId(Long aggregatorId) {
        this.aggregatorId = aggregatorId;
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
}