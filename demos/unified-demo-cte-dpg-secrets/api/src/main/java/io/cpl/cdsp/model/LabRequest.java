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
@Table(name = "lab_requests")
public class LabRequest {
	@Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;

	@Column(name = "doctor_id")
	private String doctor;

	@Column(name = "patient_id")
	private String patient;

	@Column(name = "request_date")
	private String labRequisitionDate;

	@Column(name = "request_form")
	private String labRequisitionPDF;

	@Column
	private String symptoms;

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

	public String getLabRequisitionDate() {
		return labRequisitionDate;
	}

	public void setLabRequisitionDate(String labRequisitionDate) {
		this.labRequisitionDate = labRequisitionDate;
	}

	public String getLabRequisitionPDF() {
		return labRequisitionPDF;
	}

	public void setLabRequisitionPDF(String labRequisitionPDF) {
		this.labRequisitionPDF = labRequisitionPDF;
	}

	public String getSymptoms() {
		return symptoms;
	}

	public void setSymptoms(String symptoms) {
		this.symptoms = symptoms;
	}

	@Override
	public String toString() {
		return "LabRequest [id=" + id + ", doctor=" + doctor + ", patient=" + patient + ", labRequisitionDate="
				+ labRequisitionDate + ", labRequisitionPDF=" + labRequisitionPDF + ", symptoms=" + symptoms + "]";
	}

	public LabRequest(String id, String doctor, String patient, String labRequisitionDate, String labRequisitionPDF,
			String symptoms) {
		super();
		this.id = id;
		this.doctor = doctor;
		this.patient = patient;
		this.labRequisitionDate = labRequisitionDate;
		this.labRequisitionPDF = labRequisitionPDF;
		this.symptoms = symptoms;
	}

	public LabRequest() {
		super();
		// TODO Auto-generated constructor stub
	}

}
