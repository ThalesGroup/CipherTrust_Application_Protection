/**
 * 
 */
package io.cpl.cdsp.bean;

import io.cpl.cdsp.model.Doctor;
import io.cpl.cdsp.model.Patient;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public class PatientLabRequestsResponse {
	private Patient patient;
	private Doctor doctor;
	private String filename;
	private String requestDate;
	private String symptoms;

	public Patient getPatient() {
		return patient;
	}

	public void setPatient(Patient patient) {
		this.patient = patient;
	}

	public Doctor getDoctor() {
		return doctor;
	}

	public void setDoctor(Doctor doctor) {
		this.doctor = doctor;
	}

	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	public String getRequestDate() {
		return requestDate;
	}

	public void setRequestDate(String requestDate) {
		this.requestDate = requestDate;
	}

	public String getSymptoms() {
		return symptoms;
	}

	public void setSymptoms(String symptoms) {
		this.symptoms = symptoms;
	}

	public PatientLabRequestsResponse(Patient patient, Doctor doctor, String filename, String requestDate,
			String symptoms) {
		super();
		this.patient = patient;
		this.doctor = doctor;
		this.filename = filename;
		this.requestDate = requestDate;
		this.symptoms = symptoms;
	}

	@Override
	public String toString() {
		return "PatientLabRequestsResponse [patient=" + patient + ", doctor=" + doctor + ", filename=" + filename
				+ ", requestDate=" + requestDate + ", symptoms=" + symptoms + "]";
	}

	public PatientLabRequestsResponse() {
		super();
		// TODO Auto-generated constructor stub
	}

}
