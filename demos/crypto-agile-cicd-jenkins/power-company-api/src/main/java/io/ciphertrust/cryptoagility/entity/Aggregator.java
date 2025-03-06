package io.ciphertrust.cryptoagility.entity;

import java.time.LocalDateTime;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonBackReference;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

@Entity
@Table(name = "aggregators")
public class Aggregator {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String currentStatus;
    private LocalDateTime statusUpdateTime;
    private String location;

    @OneToMany(mappedBy = "aggregator", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonBackReference("aggregator-smartmeter")
    private List<SmartMeter> smartMeters;

    public Aggregator() {
    }

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
    }

    // Helper method to add a SmartMeter
    public void addSmartMeter(SmartMeter smartMeter) {
        smartMeters.add(smartMeter);
        smartMeter.setAggregator(this);
    }

    // Helper method to remove a SmartMeter
    public void removeSmartMeter(SmartMeter smartMeter) {
        smartMeters.remove(smartMeter);
        smartMeter.setAggregator(null);
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
