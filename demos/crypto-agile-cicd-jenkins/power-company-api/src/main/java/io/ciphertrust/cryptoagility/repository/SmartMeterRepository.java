package io.ciphertrust.cryptoagility.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.cryptoagility.entity.SmartMeter;

public interface SmartMeterRepository extends JpaRepository<SmartMeter, Long> {
    List<SmartMeter> findByUserId(Long userId);
}