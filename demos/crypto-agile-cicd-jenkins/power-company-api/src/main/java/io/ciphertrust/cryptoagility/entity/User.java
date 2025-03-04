package io.ciphertrust.cryptoagility.entity;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.fasterxml.jackson.annotation.JsonProperty;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String username;
    private String password;
    private String email;
    @Column(name = "contact_num")
    private String contactNum;
    @Column(name = "address_line1")
    private String addressLineOne;
    @Column(name = "address_line2") 
    private String addressLineTwo;
    private String city;
    private String state;
    private String country;
    private String zip;
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "smart_meter_id", referencedColumnName = "id")
    @JsonManagedReference("user-smartmeter")
    private SmartMeter smartMeter;
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "payment_info_id", referencedColumnName = "id")
    @JsonManagedReference("user-paymentinfo")
    private UserPayment paymentInfo;

    public Long getId() {
        return id;
    }
    public void setId(Long id) {
        this.id = id;
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public String getUsername() {
        return username;
    }
    public void setUsername(String username) {
        this.username = username;
    }
    public String getPassword() {
        return password;
    }
    public void setPassword(String password) {
        this.password = password;
    }
    public String getEmail() {
        return email;
    }
    public void setEmail(String email) {
        this.email = email;
    }
    public String getContactNum() {
        return contactNum;
    }
    public void setContactNum(String contactNum) {
        this.contactNum = contactNum;
    }
    public String getAddressLineOne() {
        return addressLineOne;
    }
    public void setAddressLineOne(String addressLineOne) {
        this.addressLineOne = addressLineOne;
    }
    public String getAddressLineTwo() {
        return addressLineTwo;
    }
    public void setAddressLineTwo(String addressLineTwo) {
        this.addressLineTwo = addressLineTwo;
    }
    public String getCity() {
        return city;
    }
    public void setCity(String city) {
        this.city = city;
    }
    public String getState() {
        return state;
    }
    public void setState(String state) {
        this.state = state;
    }
    public String getCountry() {
        return country;
    }
    public void setCountry(String country) {
        this.country = country;
    }
    public String getZip() {
        return zip;
    }
    public void setZip(String zip) {
        this.zip = zip;
    }
    public SmartMeter getSmartMeter() {
        return smartMeter;
    }
    public void setSmartMeter(SmartMeter smartMeter) {
        this.smartMeter = smartMeter;
    }
    public UserPayment getPaymentInfo() {
        return paymentInfo;
    }
    public void setPaymentInfo(UserPayment paymentInfo) {
        this.paymentInfo = paymentInfo;
    }

    public User() {
    }   
}