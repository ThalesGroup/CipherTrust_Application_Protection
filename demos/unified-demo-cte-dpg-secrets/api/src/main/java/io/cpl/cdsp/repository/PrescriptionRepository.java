/**
 * 
 */
package io.cpl.cdsp.repository;

import java.util.ArrayList;
import org.springframework.data.jpa.repository.JpaRepository;
import io.cpl.cdsp.model.Prescription;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface PrescriptionRepository extends JpaRepository<Prescription, String> {
	ArrayList<Prescription> findByDoctor(String doctor);
	ArrayList<Prescription> findByPatient(String patient);
	ArrayList<Prescription> findByPatientAndDoctor(String patient, String doctor);
}
