package io.ciphertrust.cryptoagility.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.cryptoagility.entity.UserPayment;

public interface UserPaymentRepository extends JpaRepository<UserPayment, Long> {
}