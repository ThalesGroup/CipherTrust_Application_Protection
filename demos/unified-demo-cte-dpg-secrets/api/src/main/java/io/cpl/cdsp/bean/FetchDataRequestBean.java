/**
 * 
 */
package io.cpl.cdsp.bean;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public class FetchDataRequestBean {
	private String doctorId;
	private String patientId;

	public String getDoctorId() {
		return doctorId;
	}

	public void setDoctorId(String doctorId) {
		this.doctorId = doctorId;
	}

	public String getPatientId() {
		return patientId;
	}

	public void setPatientId(String patientId) {
		this.patientId = patientId;
	}

	@Override
	public String toString() {
		return "FetchDataRequestBean [doctorId=" + doctorId + ", patientId=" + patientId + "]";
	}

	public FetchDataRequestBean(String doctorId, String patientId) {
		super();
		this.doctorId = doctorId;
		this.patientId = patientId;
	}

	public FetchDataRequestBean() {
		super();
		// TODO Auto-generated constructor stub
	}
}
