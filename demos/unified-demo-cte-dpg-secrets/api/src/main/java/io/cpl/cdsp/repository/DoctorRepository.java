/**
 * 
 */
package io.cpl.cdsp.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import io.cpl.cdsp.model.Doctor;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface DoctorRepository extends JpaRepository<Doctor, Long> {

}
