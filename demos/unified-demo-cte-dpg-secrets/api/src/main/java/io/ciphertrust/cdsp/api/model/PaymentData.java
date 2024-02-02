package io.ciphertrust.cdsp.api.model;

import org.hibernate.annotations.GenericGenerator;
import jakarta.persistence.*;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
@Entity
@Table(name = "pci")
public class PaymentData {
    @Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;
    @Column
    private String name;
    @Column
    private String dob;
    @Column
    private String healthCardNum;
    @Column
    private String zip;
    
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getDob() {
		return dob;
	}
	public void setDob(String dob) {
		this.dob = dob;
	}
	public String getHealthCardNum() {
		return healthCardNum;
	}
	public void setHealthCardNum(String healthCardNum) {
		this.healthCardNum = healthCardNum;
	}
	public String getZip() {
		return zip;
	}
	public void setZip(String zip) {
		this.zip = zip;
	}

	public PaymentData(String id, String name, String dob, String healthCardNum, String zip) {
		this.id = id;
		this.name = name;
		this.dob = dob;
		this.healthCardNum = healthCardNum;
		this.zip = zip;
	}
    
	public PaymentData() {
	}

	@Override
	public String toString() {
		return "PaymentData [id=" + id + ", name=" + name + ", dob=" + dob + ", healthCardNum=" + healthCardNum
				+ ", zip=" + zip + "]";
	}  
}
