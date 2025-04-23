package io.ciphertrust.migration.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.migration.entity.UserBill;

public interface UserBillRepository extends JpaRepository<UserBill, Long> {

}
