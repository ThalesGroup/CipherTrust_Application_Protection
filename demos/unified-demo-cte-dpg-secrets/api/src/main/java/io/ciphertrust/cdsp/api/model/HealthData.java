package io.ciphertrust.cdsp.api.model;

import jakarta.persistence.*;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
@Entity
@Table(name = "phi")
public class HealthData {
    @Id
	private String id;
    @Column
    private String name;
    @Column
    private String dob;
    @Column
    private String healthCardNum;
    @Column
    private String zip;
    @Column
    private String fileName;
    
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

    public String getFileName() {
        return fileName;
    }
	
    public void setFileName(String filename) {
        this.fileName = filename;
    }
    
    public HealthData(String id, String name, String dob, String healthCardNum, String zip, String filename) {
		this.id = id;
		this.name = name;
		this.dob = dob;
		this.healthCardNum = healthCardNum;
		this.zip = zip;
        this.fileName = filename;
	}

	public HealthData() {
	}
    
	@Override
	public String toString() {
		return "HealthData [id=" + id + ", name=" + name + ", dob=" + dob + ", healthCardNum=" + healthCardNum
        + ", zip=" + zip + ", fileName=" + fileName + "]";
	}
}
