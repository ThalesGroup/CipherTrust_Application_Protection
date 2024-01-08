/**
 * 
 */
package io.cpl.cdsp.repository;

import java.util.ArrayList;
import org.springframework.data.jpa.repository.JpaRepository;
import io.cpl.cdsp.model.Appointment;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface AppointmentRepository extends JpaRepository<Appointment, Long> {
	ArrayList<Appointment> findByDoctor(long doctor);
	ArrayList<Appointment> findByPatient(long patient);
	ArrayList<Appointment> findByPatientAndDoctor(long patient, long doctor);
}
