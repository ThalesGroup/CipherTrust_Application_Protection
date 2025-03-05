package io.ciphertrust.cryptoagility.dto;

import io.ciphertrust.cryptoagility.entity.Aggregator;

public class SmartMeterResponse {

    private Long id;
    private String meterId;
    private String location;
    private Aggregator aggregator;

    // Constructors, Getters, and Setters

    public SmartMeterResponse() {
    }

    public SmartMeterResponse(Long id, String meterId, String location, Aggregator aggregator) {
        this.id = id;
        this.meterId = meterId;
        this.location = location;
        this.aggregator = aggregator;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getMeterId() {
        return meterId;
    }

    public void setMeterId(String meterId) {
        this.meterId = meterId;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public Aggregator getAggregator() {
        return aggregator;
    }

    public void setAggregator(Aggregator aggregator) {
        this.aggregator = aggregator;
    }
}