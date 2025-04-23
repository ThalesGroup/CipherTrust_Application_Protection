package io.ciphertrust.migration.entity;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonBackReference;
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

    @Column(name = "total_energy_consumption")
    private String totalEnergyConsumption; // in kWh

    @Column(name = "instantaneous_power_usage")
    private String instantaneousPowerUsage; // in kW

    @Column(name = "voltage")
    private String voltage; // in volts

    @Column(name = "current")
    private String current; // in amperes

    @Column(name = "power_factor")
    private String powerFactor; // dimensionless (0 to 1)

    @Column(name = "frequency")
    private String frequency; // in Hz

    @Column(name = "timestamp")
    private LocalDateTime timestamp; // timestamp of the reading

    @Column(name = "temperature")
    private String temperature; // in °C (optional)

    @Column(name = "humidity")
    private String humidity; // in % (optional)

    @Column(name = "detailed_consumption_intervals")
    private String detailedConsumptionIntervals; // JSON or CSV format for detailed intervals

    @ManyToOne
    @JoinColumn(name = "smart_meter_id", nullable = false)
    @JsonBackReference("smartmeter-telemetry")
    private SmartMeter smartMeter; // Associated smart meter
  
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTotalEnergyConsumption() {
        return totalEnergyConsumption;
    }

    public void setTotalEnergyConsumption(String totalEnergyConsumption) {
        this.totalEnergyConsumption = totalEnergyConsumption;
    }

    public String getInstantaneousPowerUsage() {
        return instantaneousPowerUsage;
    }

    public void setInstantaneousPowerUsage(String instantaneousPowerUsage) {
        this.instantaneousPowerUsage = instantaneousPowerUsage;
    }

    public String getVoltage() {
        return voltage;
    }

    public void setVoltage(String voltage) {
        this.voltage = voltage;
    }

    public String getCurrent() {
        return current;
    }

    public void setCurrent(String current) {
        this.current = current;
    }

    public String getPowerFactor() {
        return powerFactor;
    }

    public void setPowerFactor(String powerFactor) {
        this.powerFactor = powerFactor;
    }

    public String getFrequency() {
        return frequency;
    }

    public void setFrequency(String frequency) {
        this.frequency = frequency;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public String getTemperature() {
        return temperature;
    }

    public void setTemperature(String temperature) {
        this.temperature = temperature;
    }

    public String getHumidity() {
        return humidity;
    }

    public void setHumidity(String humidity) {
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

    public SmartMeterData() {
    }

    @Override
    public String toString() {
        return "SmartMeterData [id=" + id + ", totalEnergyConsumption=" + totalEnergyConsumption
                + ", instantaneousPowerUsage=" + instantaneousPowerUsage + ", voltage=" + voltage + ", current="
                + current + ", powerFactor=" + powerFactor + ", frequency=" + frequency + ", timestamp=" + timestamp
                + ", temperature=" + temperature + ", humidity=" + humidity + ", detailedConsumptionIntervals="
                + detailedConsumptionIntervals + ", smartMeter=" + smartMeter + "]";
    }

    
}
