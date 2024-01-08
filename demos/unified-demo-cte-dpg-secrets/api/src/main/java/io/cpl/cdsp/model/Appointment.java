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
@Table(name = "appointments")
public class Appointment {	
	@Id
	@GeneratedValue(strategy = GenerationType.AUTO)
	private long id;
	
	@Column(name = "doctor_id")
    private long doctor;
	
	@Column(name = "patient_id")
    private long patient;
	
	@Column(name = "appointment_date")
	private String appointmentDate;
	
	@Column(name = "appointment_reason")
	private String appointmentReason;

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

	public String getAppointmentDate() {
		return appointmentDate;
	}

	public void setAppointmentDate(String appointmentDate) {
		this.appointmentDate = appointmentDate;
	}

	public String getAppointmentReason() {
		return appointmentReason;
	}

	public void setAppointmentReason(String appointmentReason) {
		this.appointmentReason = appointmentReason;
	}

	@Override
	public String toString() {
		return "Appointment [id=" + id + ", doctor=" + doctor + ", patient=" + patient + ", appointmentDate="
				+ appointmentDate + ", appointmentReason=" + appointmentReason + "]";
	}

	public Appointment(long id, long doctor, long patient, String appointmentDate, String appointmentReason) {
		super();
		this.id = id;
		this.doctor = doctor;
		this.patient = patient;
		this.appointmentDate = appointmentDate;
		this.appointmentReason = appointmentReason;
	}

	public Appointment() {
		super();
		// TODO Auto-generated constructor stub
	}
}
