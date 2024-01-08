package io.cpl.cdsp.repository;

import java.util.ArrayList;
import org.springframework.data.jpa.repository.JpaRepository;
import io.cpl.cdsp.model.LabRequest;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface LabRequestRepository extends JpaRepository<LabRequest, Long> {
	ArrayList<LabRequest> findByDoctor(String doctor);
	ArrayList<LabRequest> findByPatient(String patient);
	ArrayList<LabRequest> findByPatientAndDoctor(String patient, String doctor);
}
