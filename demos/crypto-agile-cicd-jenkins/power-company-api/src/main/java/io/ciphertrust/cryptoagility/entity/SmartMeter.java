package io.ciphertrust.cryptoagility.entity;

import java.time.LocalDate;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonBackReference;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "smart_meter")
public class SmartMeter {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String meterId;

    @Column(name = "manufacturer")
    private String manufacturer; // Manufacturer of the smart meter

    @Column(name = "installation_date")
    private LocalDate installationDate; // Date when the meter was installed

    @OneToOne(mappedBy = "smartMeter")
    @JsonBackReference("user-smartmeter")
    private User user;

    @OneToMany(mappedBy = "smartMeter", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonBackReference
    private List<SmartMeterData> telemetryData; // Telemetry data for this smart meter

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getManufacturer() {
        return manufacturer;
    }

    public void setManufacturer(String manufacturer) {
        this.manufacturer = manufacturer;
    }

    public LocalDate getInstallationDate() {
        return installationDate;
    }

    public void setInstallationDate(LocalDate installationDate) {
        this.installationDate = installationDate;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public List<SmartMeterData> getTelemetryData() {
        return telemetryData;
    }

    public void setTelemetryData(List<SmartMeterData> telemetryData) {
        this.telemetryData = telemetryData;
    }

    public String getMeterId() {
        return meterId;
    }

    public void setMeterId(String meterId) {
        this.meterId = meterId;
    }

    public SmartMeter() {
    }
}
