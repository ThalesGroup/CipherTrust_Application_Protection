/**
 * 
 */
package io.cpl.cdsp.model;

import org.hibernate.annotations.GenericGenerator;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */

@Entity
@Table(name = "doctors")
public class Doctor {
	@Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;
	
	@Column(name = "first_name")
	private String firstName;
	
	@Column(name = "last_name")
	private String lastName;
	
	@Column(name = "practice_type")
	private String practiceType;
	
	@Column
	private String email;
	
	@Column
	private String gender;
	
	@Column(name = "doctor_reg_number")
	private String registrationNumber;

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

	public String getPracticeType() {
		return practiceType;
	}

	public void setPracticeType(String practiceType) {
		this.practiceType = practiceType;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getGender() {
		return gender;
	}

	public void setGender(String gender) {
		this.gender = gender;
	}

	public String getRegistrationNumber() {
		return registrationNumber;
	}

	public void setRegistrationNumber(String registrationNumber) {
		this.registrationNumber = registrationNumber;
	}

	@Override
	public String toString() {
		return "Doctor [id=" + id + ", firstName=" + firstName + ", lastName=" + lastName + ", practiceType="
				+ practiceType + ", email=" + email + ", gender=" + gender + ", registrationNumber="
				+ registrationNumber + "]";
	}

	public Doctor(String id, String firstName, String lastName, String practiceType, String email, String gender,
			String registrationNumber) {
		super();
		this.id = id;
		this.firstName = firstName;
		this.lastName = lastName;
		this.practiceType = practiceType;
		this.email = email;
		this.gender = gender;
		this.registrationNumber = registrationNumber;
	}

	public Doctor() {
		super();
		// TODO Auto-generated constructor stub
	}
}
