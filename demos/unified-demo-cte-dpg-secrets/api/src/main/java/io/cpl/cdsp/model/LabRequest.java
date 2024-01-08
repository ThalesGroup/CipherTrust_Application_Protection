/**
 * 
 */
package io.cpl.cdsp.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */

@Entity
@Table(name = "lab_requests")
public class LabRequest {
	
	@Id
	@GeneratedValue(strategy = GenerationType.AUTO)
	private long id;
	
	@Column(name = "doctor_id")
    private long doctor;
	
	@Column(name = "patient_id")
    private long patient;
	
	@Column(name = "prescription_date")
	private String prescriptionDate;
	
	@Column(name = "prescription_pdf")
	private String prescriptionPDF;
	
	@Column
	private String symptoms;

	public long getId() {
		return id;
	}

	public void setId(long id) {
		this.id = id;
	}

	public long getDoctor() {
		return doctor;
	}

	public void setDoctor(long doctor) {
		this.doctor = doctor;
	}

	public long getPatient() {
		return patient;
	}

	public void setPatient(long patient) {
		this.patient = patient;
	}

	public String getPrescriptionDate() {
		return prescriptionDate;
	}

	public void setPrescriptionDate(String prescriptionDate) {
		this.prescriptionDate = prescriptionDate;
	}

	public String getPrescriptionPDF() {
		return prescriptionPDF;
	}

	public void setPrescriptionPDF(String prescriptionPDF) {
		this.prescriptionPDF = prescriptionPDF;
	}

	public String getSymptoms() {
		return symptoms;
	}

	public void setSymptoms(String symptoms) {
		this.symptoms = symptoms;
	}

	public LabRequest(long id, long doctor, long patient, String prescriptionDate, String prescriptionPDF,
			String symptoms) {
		super();
		this.id = id;
		this.doctor = doctor;
		this.patient = patient;
		this.prescriptionDate = prescriptionDate;
		this.prescriptionPDF = prescriptionPDF;
		this.symptoms = symptoms;
	}

	public LabRequest() {
		super();
		// TODO Auto-generated constructor stub
	}

	@Override
	public String toString() {
		return "LabRequest [id=" + id + ", doctor=" + doctor + ", patient=" + patient + ", prescriptionDate="
				+ prescriptionDate + ", prescriptionPDF=" + prescriptionPDF + ", symptoms=" + symptoms + "]";
	}
}
