package io.ciphertrust.migration.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.migration.entity.SmartMeter;

public interface SmartMeterRepository extends JpaRepository<SmartMeter, Long> {
    List<SmartMeter> findByUserId(Long userId);
    List<SmartMeter> findByAggregatorId(Long aggregatorId);
}