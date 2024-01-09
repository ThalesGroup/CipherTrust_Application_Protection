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
@Table(name = "prescriptions")
public class Prescription {	
	@Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;

	@Column(name = "doctor_id")
	private String doctor;

	@Column(name = "patient_id")
	private String patient;
	
	@Column(name = "prescription_date")
	private String prescriptionDate;
	
	@Column(name = "prescription_pdf")
	private String prescriptionPDF;
	
	@Column(name = "prescription_length")
	private String prescriptionLength;

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getDoctor() {
		return doctor;
	}

	public void setDoctor(String doctor) {
		this.doctor = doctor;
	}

	public String getPatient() {
		return patient;
	}

	public void setPatient(String patient) {
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

	public String getPrescriptionLength() {
		return prescriptionLength;
	}

	public void setPrescriptionLength(String prescriptionLength) {
		this.prescriptionLength = prescriptionLength;
	}

	@Override
	public String toString() {
		return "Prescription [id=" + id + ", doctor=" + doctor + ", patient=" + patient + ", prescriptionDate="
				+ prescriptionDate + ", prescriptionPDF=" + prescriptionPDF + ", prescriptionLength="
				+ prescriptionLength + "]";
	}

	public Prescription(String id, String doctor, String patient, String prescriptionDate, String prescriptionPDF,
			String prescriptionLength) {
		super();
		this.id = id;
		this.doctor = doctor;
		this.patient = patient;
		this.prescriptionDate = prescriptionDate;
		this.prescriptionPDF = prescriptionPDF;
		this.prescriptionLength = prescriptionLength;
	}
	
	public Prescription() {
		super();
		// TODO Auto-generated constructor stub
	}
}
