package io.ciphertrust.migration.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.migration.entity.UserPayment;

public interface UserPaymentRepository extends JpaRepository<UserPayment, Long> {
}