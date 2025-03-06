package io.ciphertrust.cryptoagility.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.cryptoagility.entity.UserBill;

public interface UserBillRepository extends JpaRepository<UserBill, Long> {

}
