package io.ciphertrust.cdsp.api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import io.ciphertrust.cdsp.api.model.PaymentData;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface PaymentDataRepo extends JpaRepository<PaymentData, String> {

}