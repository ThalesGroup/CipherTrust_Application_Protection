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
public class PatientAppointmentsResponse {
	private Patient patient;
	private Doctor doctor;
	private String date;
	private String reason;

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

	public String getDate() {
		return date;
	}

	public void setDate(String date) {
		this.date = date;
	}

	public String getReason() {
		return reason;
	}

	public void setReason(String reason) {
		this.reason = reason;
	}

	@Override
	public String toString() {
		return "PatientAppointmentsResponse [patient=" + patient + ", doctor=" + doctor + ", date=" + date + ", reason="
				+ reason + "]";
	}

	public PatientAppointmentsResponse(Patient patient, Doctor doctor, String date, String reason) {
		super();
		this.patient = patient;
		this.doctor = doctor;
		this.date = date;
		this.reason = reason;
	}

	public PatientAppointmentsResponse() {
		super();
		// TODO Auto-generated constructor stub
	}
}
