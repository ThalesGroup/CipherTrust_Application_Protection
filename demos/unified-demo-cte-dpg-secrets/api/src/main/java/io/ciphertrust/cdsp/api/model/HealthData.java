package io.ciphertrust.cdsp.api.model;

import org.hibernate.annotations.GenericGenerator;
import jakarta.persistence.*;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
@Entity
@Table(name = "phi")
public class HealthData {
    @Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;
    @Column
    private String name;
    @Column
    private String cc;
    @Column
    private String cvv;
    @Column
    private String expiry;
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
    public String getCc() {
        return cc;
    }
    public void setCc(String cc) {
        this.cc = cc;
    }
    public String getCvv() {
        return cvv;
    }
    public void setCvv(String cvv) {
        this.cvv = cvv;
    }
    public String getExpiry() {
        return expiry;
    }
    public void setExpiry(String expiry) {
        this.expiry = expiry;
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
    
    public HealthData(String id, String name, String cc, String cvv, String expiry, String zip, String filename) {
        this.id = id;
        this.name = name;
        this.cc = cc;
        this.cvv = cvv;
        this.expiry = expiry;
        this.zip = zip;
        this.fileName = filename;
    }

	public HealthData() {
	}
    
	@Override
	public String toString() {
		return "HealthData [id=" + id + ", name=" + name + ", cc=" + cc + ", cvv=" + cvv + ", expiry=" + expiry
				+ ", zip=" + zip + ", fileName=" + fileName + "]";
	}
}
