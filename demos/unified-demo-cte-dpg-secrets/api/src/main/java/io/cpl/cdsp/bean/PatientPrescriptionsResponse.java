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
public class PatientPrescriptionsResponse {
	private Patient patient;
	private Doctor doctor;
	private String filename;
	private String durationInDays;
	private String prescriptionDate;

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

	public String getDurationInDays() {
		return durationInDays;
	}

	public void setDurationInDays(String durationInDays) {
		this.durationInDays = durationInDays;
	}

	public String getPrescriptionDate() {
		return prescriptionDate;
	}

	public void setPrescriptionDate(String prescriptionDate) {
		this.prescriptionDate = prescriptionDate;
	}

	@Override
	public String toString() {
		return "PatientPrescriptionsResponse [patient=" + patient + ", doctor=" + doctor + ", filename=" + filename
				+ ", durationInDays=" + durationInDays + ", prescriptionDate=" + prescriptionDate + "]";
	}

	public PatientPrescriptionsResponse(Patient patient, Doctor doctor, String filename, String durationInDays,
			String prescriptionDate) {
		super();
		this.patient = patient;
		this.doctor = doctor;
		this.filename = filename;
		this.durationInDays = durationInDays;
		this.prescriptionDate = prescriptionDate;
	}

	public PatientPrescriptionsResponse() {
		super();
		// TODO Auto-generated constructor stub
	}

}
