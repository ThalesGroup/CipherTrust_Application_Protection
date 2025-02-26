package io.ciphertrust.cdsp.api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import io.ciphertrust.cdsp.api.model.HealthData;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface HealthDataRepo extends JpaRepository<HealthData, String> {

}