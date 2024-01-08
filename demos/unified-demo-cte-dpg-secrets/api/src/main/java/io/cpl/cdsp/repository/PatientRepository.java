/**
 * 
 */
package io.cpl.cdsp.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import io.cpl.cdsp.model.Patient;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface PatientRepository extends JpaRepository<Patient, Long> {

}
