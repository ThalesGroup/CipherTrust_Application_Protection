/**
 * 
 */
package io.cpl.cdsp.controller;

import java.util.ArrayList;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import io.cpl.cdsp.bean.PatientAppointmentsResponse;
import io.cpl.cdsp.bean.PatientLabRequestsResponse;
import io.cpl.cdsp.bean.PatientPrescriptionsResponse;
import io.cpl.cdsp.model.Appointment;
import io.cpl.cdsp.model.Doctor;
import io.cpl.cdsp.model.LabRequest;
import io.cpl.cdsp.model.Patient;
import io.cpl.cdsp.model.Prescription;
import io.cpl.cdsp.repository.AppointmentRepository;
import io.cpl.cdsp.repository.DoctorRepository;
import io.cpl.cdsp.repository.LabRequestRepository;
import io.cpl.cdsp.repository.PatientRepository;
import io.cpl.cdsp.repository.PrescriptionRepository;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api")
public class MainController {
	
	@Autowired
	PatientRepository patientRepo;
	
	@Autowired
	PrescriptionRepository prescriptionRepository;
	
	@Autowired
	LabRequestRepository labRequestRepository;
	
	@Autowired
	DoctorRepository doctorRepository;
	
	@Autowired
	AppointmentRepository appointmentRepository;
	
	@PostMapping("/patients")
	public ResponseEntity<Patient> createPatient(@RequestBody Patient patient) {
		try {
			Patient _patient = patientRepo.save(patient);
			return new ResponseEntity<>(_patient, 
					HttpStatus.CREATED);
		} catch (Exception e) {
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@PostMapping("/doctors")
	public ResponseEntity<Doctor> createDoctor(@RequestBody Doctor doctor) {
		try {
			Doctor _doctor = doctorRepository.save(doctor);
			return new ResponseEntity<>(_doctor, 
					HttpStatus.CREATED);
		} catch (Exception e) {
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@PostMapping("/appointments")
	public ResponseEntity<Appointment> createAppointment(@RequestBody Appointment appointment) {
		try {
			Appointment _appointment = appointmentRepository.save(appointment);
			return new ResponseEntity<>(_appointment, 
					HttpStatus.CREATED);
		} catch (Exception e) {
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@PostMapping("/prescriptions")
	public ResponseEntity<Prescription> createPrescription(@RequestBody Prescription prescription) {
		try {
			Prescription _prescription = prescriptionRepository.save(prescription);
			return new ResponseEntity<>(_prescription, 
					HttpStatus.CREATED);
		} catch (Exception e) {
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@PostMapping("/lab-requests")
	public ResponseEntity<LabRequest> createLabRequest(@RequestBody LabRequest labRequest) {
		try {
			LabRequest _labRequest = labRequestRepository.save(labRequest);
			return new ResponseEntity<>(_labRequest, 
					HttpStatus.CREATED);
		} catch (Exception e) {
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@GetMapping("/patients")
	public ResponseEntity<ArrayList<Patient>> listPatients(
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header,
			@RequestParam("id") Optional<String> patientId) {
		try {
			ArrayList<Patient> patients = new ArrayList<Patient>();
			Patient record = new Patient();
			if(patientId != null && !patientId.isEmpty()) {
				record = patientRepo.findById(patientId.get()).get();
				patients.add(record);
			} else {
				patientRepo.findAll().forEach(patients::add);
			}			
			return new ResponseEntity<ArrayList<Patient>>(patients, 
					HttpStatus.OK);
		} catch (Exception e) {	
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@GetMapping("/doctors")
	public ResponseEntity<ArrayList<Doctor>> listDoctors(
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header) {
		try {
			ArrayList<Doctor> doctors = new ArrayList<Doctor>();
			doctorRepository.findAll().forEach(doctors::add);
			return new ResponseEntity<ArrayList<Doctor>>(doctors, 
					HttpStatus.OK);
		} catch (Exception e) {	
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@GetMapping("/appointments")
	public ResponseEntity<ArrayList<PatientAppointmentsResponse>> listAppointments(
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header,
			@RequestParam("doctor_id") Optional<String> doctorId,
			@RequestParam("patient_id") Optional<String> patientId) {
		try {
			ArrayList<PatientAppointmentsResponse> appointments = new ArrayList<PatientAppointmentsResponse>();
			
			if(doctorId.isPresent() && patientId.isPresent()) {
				for (Appointment a : 
					appointmentRepository
					.findByPatientAndDoctor(
						patientId.get(),
						doctorId.get())) {
					PatientAppointmentsResponse pa = new PatientAppointmentsResponse();
					pa.setDoctor(doctorRepository.findById(a.getDoctor()).get());
					pa.setPatient(patientRepo.findById(a.getPatient()).get());
					pa.setDate(a.getAppointmentDate());
					pa.setReason(a.getAppointmentReason());
					appointments.add(pa);
				}
			} else if(doctorId.isPresent() && !patientId.isPresent()) {
				for (Appointment a : 
					appointmentRepository
					.findByDoctor(
						doctorId.get())) {
					PatientAppointmentsResponse pa = new PatientAppointmentsResponse();
					pa.setDoctor(doctorRepository.findById(a.getDoctor()).get());
					pa.setPatient(patientRepo.findById(a.getPatient()).get());
					pa.setDate(a.getAppointmentDate());
					pa.setReason(a.getAppointmentReason());
					appointments.add(pa);
				}
			} else if(!doctorId.isPresent() && patientId.isPresent()) {
				for (Appointment a : 
					appointmentRepository
					.findByPatient(
						patientId.get())) {
					PatientAppointmentsResponse pa = new PatientAppointmentsResponse();
					pa.setDoctor(doctorRepository.findById(a.getDoctor()).get());
					pa.setPatient(patientRepo.findById(a.getPatient()).get());
					pa.setDate(a.getAppointmentDate());
					pa.setReason(a.getAppointmentReason());
					appointments.add(pa);
				}
			} else {
				for (Appointment a : 
					appointmentRepository
					.findAll()) {
					PatientAppointmentsResponse pa = new PatientAppointmentsResponse();
					pa.setDoctor(doctorRepository.findById(a.getDoctor()).get());
					pa.setPatient(patientRepo.findById(a.getPatient()).get());
					pa.setDate(a.getAppointmentDate());
					pa.setReason(a.getAppointmentReason());
					appointments.add(pa);
				}
			}
			return new ResponseEntity<ArrayList<PatientAppointmentsResponse>>(appointments, 
					HttpStatus.OK);
		} catch (Exception e) {
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@GetMapping("/prescriptions")
	public ResponseEntity<ArrayList<PatientPrescriptionsResponse>> listPrescriptions(
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header,
			@RequestParam("doctor_id") Optional<String> doctorId,
			@RequestParam("patient_id") Optional<String> patientId) {
		try {
			ArrayList<PatientPrescriptionsResponse> prescriptions = new ArrayList<PatientPrescriptionsResponse>();	
			
			if(doctorId.isPresent() && patientId.isPresent()) {
				for (Prescription p : 
					prescriptionRepository
					.findByPatientAndDoctor(
						patientId.get(),
						doctorId.get())) {
					PatientPrescriptionsResponse pr = new PatientPrescriptionsResponse();
					pr.setDoctor(doctorRepository.findById(p.getDoctor()).get());
					pr.setPatient(patientRepo.findById(p.getPatient()).get());
					pr.setDurationInDays(p.getPrescriptionLength());
					pr.setFilename(p.getPrescriptionPDF());
					pr.setPrescriptionDate(p.getPrescriptionDate());
					prescriptions.add(pr);
				}
			} else if(doctorId.isPresent() && !patientId.isPresent()) {
				for (Prescription p : 
					prescriptionRepository
					.findByDoctor(
						doctorId.get())) {
					PatientPrescriptionsResponse pr = new PatientPrescriptionsResponse();
					pr.setDoctor(doctorRepository.findById(p.getDoctor()).get());
					pr.setPatient(patientRepo.findById(p.getPatient()).get());
					pr.setDurationInDays(p.getPrescriptionLength());
					pr.setFilename(p.getPrescriptionPDF());
					pr.setPrescriptionDate(p.getPrescriptionDate());
					prescriptions.add(pr);
				}
			} else if(!doctorId.isPresent() && patientId.isPresent()) {
				for (Prescription p : 
					prescriptionRepository
					.findByPatient(
							patientId.get())) {
					PatientPrescriptionsResponse pr = new PatientPrescriptionsResponse();
					pr.setDoctor(doctorRepository.findById(p.getDoctor()).get());
					pr.setPatient(patientRepo.findById(p.getPatient()).get());
					pr.setDurationInDays(p.getPrescriptionLength());
					pr.setFilename(p.getPrescriptionPDF());
					pr.setPrescriptionDate(p.getPrescriptionDate());
					prescriptions.add(pr);
				}
			} else {
				for (Prescription p : 
					prescriptionRepository
					.findAll()){
					PatientPrescriptionsResponse pr = new PatientPrescriptionsResponse();
					pr.setDoctor(doctorRepository.findById(p.getDoctor()).get());
					pr.setPatient(patientRepo.findById(p.getPatient()).get());
					pr.setDurationInDays(p.getPrescriptionLength());
					pr.setFilename(p.getPrescriptionPDF());
					pr.setPrescriptionDate(p.getPrescriptionDate());
					prescriptions.add(pr);
				}
			}
			return new ResponseEntity<ArrayList<PatientPrescriptionsResponse>>(prescriptions, 
					HttpStatus.OK);
		} catch (Exception e) {	
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
	
	@GetMapping("/lab-requests")
	public ResponseEntity<ArrayList<PatientLabRequestsResponse>> listLabRequests(
			@RequestHeader(HttpHeaders.AUTHORIZATION) String header,
			@RequestParam("doctor_id") Optional<String> doctorId,
			@RequestParam("patient_id") Optional<String> patientId) {
		try {
			ArrayList<PatientLabRequestsResponse> labRequests = new ArrayList<PatientLabRequestsResponse>();
			
			if(doctorId.isPresent() && patientId.isPresent()) {
				for (LabRequest lr : 
					labRequestRepository
					.findByPatientAndDoctor(
						patientId.get(),
						doctorId.get())) {
					PatientLabRequestsResponse pr = new PatientLabRequestsResponse();
					pr.setDoctor(doctorRepository.findById(lr.getDoctor()).get());
					pr.setPatient(patientRepo.findById(lr.getPatient()).get());
					pr.setFilename(lr.getLabRequisitionPDF());
					pr.setRequestDate(lr.getLabRequisitionDate());
					pr.setSymptoms(lr.getSymptoms());
					labRequests.add(pr);
				}
			} else if(doctorId.isPresent() && !patientId.isPresent()) {
				for (LabRequest lr : 
					labRequestRepository
					.findByDoctor(
						doctorId.get())) {
					PatientLabRequestsResponse pr = new PatientLabRequestsResponse();
					pr.setDoctor(doctorRepository.findById(lr.getDoctor()).get());
					pr.setPatient(patientRepo.findById(lr.getPatient()).get());
					pr.setFilename(lr.getLabRequisitionPDF());
					pr.setRequestDate(lr.getLabRequisitionDate());
					pr.setSymptoms(lr.getSymptoms());
					labRequests.add(pr);
				}
			} else if(!doctorId.isPresent() && patientId.isPresent()) {
				for (LabRequest lr : 
					labRequestRepository
					.findByPatient(
							patientId.get())) {
					PatientLabRequestsResponse pr = new PatientLabRequestsResponse();
					pr.setDoctor(doctorRepository.findById(lr.getDoctor()).get());
					pr.setPatient(patientRepo.findById(lr.getPatient()).get());
					pr.setFilename(lr.getLabRequisitionPDF());
					pr.setRequestDate(lr.getLabRequisitionDate());
					pr.setSymptoms(lr.getSymptoms());
					labRequests.add(pr);
				}
			} else {
				for (LabRequest lr : 
					labRequestRepository
					.findAll()) {
					PatientLabRequestsResponse pr = new PatientLabRequestsResponse();
					pr.setDoctor(doctorRepository.findById(lr.getDoctor()).get());
					pr.setPatient(patientRepo.findById(lr.getPatient()).get());
					pr.setFilename(lr.getLabRequisitionPDF());
					pr.setRequestDate(lr.getLabRequisitionDate());
					pr.setSymptoms(lr.getSymptoms());
					labRequests.add(pr);
				}
			}
			return new ResponseEntity<ArrayList<PatientLabRequestsResponse>>(labRequests, 
					HttpStatus.OK);
		} catch (Exception e) {	
			return new ResponseEntity<>(null, 
				HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}
}
