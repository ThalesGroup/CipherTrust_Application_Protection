/**
 * 
 */
package io.cpl.cdsp.model;

import org.hibernate.annotations.GenericGenerator;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */

import jakarta.persistence.*;

@Entity
@Table(name = "patients")
public class Patient {
	@Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;
	
	@Column(name = "first_name")
	private String firstName;
	
	@Column(name = "last_name")
	private String lastName;

	@Column(name = "contact_num")
	private String contactNumber;
	
	@Column(name = "dob")
	private String dateOfBirth;
	
	@Column(name = "email")
	private String email;
	
	@Column(name = "health_card_number")
	private String healthCardNumber;
	
	@Column(name = "health_card_expiryr")
	private String healthCardExpiry;
	
	@Column
	private String gender;
	
	@Column
	private String address;
	
	@Column(name = "house_number")
	private String houseNumber;
	
	@Column
	private String city;
	
	@Column
	private String state;
	
	@Column(name = "zip_code")
	private String zipCode;
	
	@Column(name = "blood_group")
	private String bloodGroup;
	
	@Column(name = "major_ailments")
	private String ailments;
	
	@Column(name = "primary_physician")
	private String primaryPhysician;

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getFirstName() {
		return firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public String getLastName() {
		return lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

	public String getContactNumber() {
		return contactNumber;
	}

	public void setContactNumber(String contactNumber) {
		this.contactNumber = contactNumber;
	}

	public String getDateOfBirth() {
		return dateOfBirth;
	}

	public void setDateOfBirth(String dateOfBirth) {
		this.dateOfBirth = dateOfBirth;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getHealthCardNumber() {
		return healthCardNumber;
	}

	public void setHealthCardNumber(String healthCardNumber) {
		this.healthCardNumber = healthCardNumber;
	}

	public String getHealthCardExpiry() {
		return healthCardExpiry;
	}

	public void setHealthCardExpiry(String healthCardExpiry) {
		this.healthCardExpiry = healthCardExpiry;
	}

	public String getGender() {
		return gender;
	}

	public void setGender(String gender) {
		this.gender = gender;
	}

	public String getAddress() {
		return address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getHouseNumber() {
		return houseNumber;
	}

	public void setHouseNumber(String houseNumber) {
		this.houseNumber = houseNumber;
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

	public String getZipCode() {
		return zipCode;
	}

	public void setZipCode(String zipCode) {
		this.zipCode = zipCode;
	}

	public String getBloodGroup() {
		return bloodGroup;
	}

	public void setBloodGroup(String bloodGroup) {
		this.bloodGroup = bloodGroup;
	}

	public String getAilments() {
		return ailments;
	}

	public void setAilments(String ailments) {
		this.ailments = ailments;
	}

	public String getPrimaryPhysician() {
		return primaryPhysician;
	}

	public void setPrimaryPhysician(String primaryPhysician) {
		this.primaryPhysician = primaryPhysician;
	}

	@Override
	public String toString() {
		return "Patient [id=" + id + ", firstName=" + firstName + ", lastName=" + lastName + ", contactNumber="
				+ contactNumber + ", dateOfBirth=" + dateOfBirth + ", email=" + email + ", healthCardNumber="
				+ healthCardNumber + ", healthCardExpiry=" + healthCardExpiry + ", gender=" + gender + ", address="
				+ address + ", houseNumber=" + houseNumber + ", city=" + city + ", state=" + state + ", zipCode="
				+ zipCode + ", bloodGroup=" + bloodGroup + ", ailments=" + ailments + ", primaryPhysician="
				+ primaryPhysician + "]";
	}

	public Patient(String id, String firstName, String lastName, String contactNumber, String dateOfBirth, String email,
			String healthCardNumber, String healthCardExpiry, String gender, String address, String houseNumber,
			String city, String state, String zipCode, String bloodGroup, String ailments, String primaryPhysician) {
		super();
		this.id = id;
		this.firstName = firstName;
		this.lastName = lastName;
		this.contactNumber = contactNumber;
		this.dateOfBirth = dateOfBirth;
		this.email = email;
		this.healthCardNumber = healthCardNumber;
		this.healthCardExpiry = healthCardExpiry;
		this.gender = gender;
		this.address = address;
		this.houseNumber = houseNumber;
		this.city = city;
		this.state = state;
		this.zipCode = zipCode;
		this.bloodGroup = bloodGroup;
		this.ailments = ailments;
		this.primaryPhysician = primaryPhysician;
	}

	public Patient() {
		super();
		// TODO Auto-generated constructor stub
	}
}
