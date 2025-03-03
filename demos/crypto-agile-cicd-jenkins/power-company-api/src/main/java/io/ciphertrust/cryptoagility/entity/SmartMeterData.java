package io.ciphertrust.cryptoagility.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "smart_meter_data")
public class SmartMeterData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "total_energy_consumption", nullable = false)
    private Double totalEnergyConsumption; // in kWh

    @Column(name = "instantaneous_power_usage", nullable = false)
    private Double instantaneousPowerUsage; // in kW

    @Column(name = "voltage", nullable = false)
    private Double voltage; // in volts

    @Column(name = "current", nullable = false)
    private Double current; // in amperes

    @Column(name = "power_factor", nullable = false)
    private Double powerFactor; // dimensionless (0 to 1)

    @Column(name = "frequency", nullable = false)
    private Double frequency; // in Hz

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp; // timestamp of the reading

    @Column(name = "temperature")
    private Double temperature; // in °C (optional)

    @Column(name = "humidity")
    private Double humidity; // in % (optional)

    @Column(name = "detailed_consumption_intervals")
    private String detailedConsumptionIntervals; // JSON or CSV format for detailed intervals

    @ManyToOne
    @JoinColumn(name = "smart_meter_id", nullable = false)
    private SmartMeter smartMeter; // Associated smart meter

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Double getTotalEnergyConsumption() {
        return totalEnergyConsumption;
    }

    public void setTotalEnergyConsumption(Double totalEnergyConsumption) {
        this.totalEnergyConsumption = totalEnergyConsumption;
    }

    public Double getInstantaneousPowerUsage() {
        return instantaneousPowerUsage;
    }

    public void setInstantaneousPowerUsage(Double instantaneousPowerUsage) {
        this.instantaneousPowerUsage = instantaneousPowerUsage;
    }

    public Double getVoltage() {
        return voltage;
    }

    public void setVoltage(Double voltage) {
        this.voltage = voltage;
    }

    public Double getCurrent() {
        return current;
    }

    public void setCurrent(Double current) {
        this.current = current;
    }

    public Double getPowerFactor() {
        return powerFactor;
    }

    public void setPowerFactor(Double powerFactor) {
        this.powerFactor = powerFactor;
    }

    public Double getFrequency() {
        return frequency;
    }

    public void setFrequency(Double frequency) {
        this.frequency = frequency;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public Double getTemperature() {
        return temperature;
    }

    public void setTemperature(Double temperature) {
        this.temperature = temperature;
    }

    public Double getHumidity() {
        return humidity;
    }

    public void setHumidity(Double humidity) {
        this.humidity = humidity;
    }

    public String getDetailedConsumptionIntervals() {
        return detailedConsumptionIntervals;
    }

    public void setDetailedConsumptionIntervals(String detailedConsumptionIntervals) {
        this.detailedConsumptionIntervals = detailedConsumptionIntervals;
    }

    public SmartMeter getSmartMeter() {
        return smartMeter;
    }

    public void setSmartMeter(SmartMeter smartMeter) {
        this.smartMeter = smartMeter;
    }
}
