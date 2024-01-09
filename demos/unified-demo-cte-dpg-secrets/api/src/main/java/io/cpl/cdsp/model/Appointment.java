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
@Table(name = "appointments")
public class Appointment {
	@Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	private String id;

	@Column(name = "doctor_id")
	private String doctor;

	@Column(name = "patient_id")
	private String patient;

	@Column(name = "appointment_date")
	private String appointmentDate;

	@Column(name = "appointment_reason")
	private String appointmentReason;

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

	public Appointment(String id, String doctor, String patient, String appointmentDate, String appointmentReason) {
		super();
		this.id = id;
		this.doctor = doctor;
		this.patient = patient;
		this.appointmentDate = appointmentDate;
		this.appointmentReason = appointmentReason;
	}

	@Override
	public String toString() {
		return "Appointment [id=" + id + ", doctor=" + doctor + ", patient=" + patient + ", appointmentDate="
				+ appointmentDate + ", appointmentReason=" + appointmentReason + "]";
	}

	public Appointment() {
		super();
		// TODO Auto-generated constructor stub
	}
}
