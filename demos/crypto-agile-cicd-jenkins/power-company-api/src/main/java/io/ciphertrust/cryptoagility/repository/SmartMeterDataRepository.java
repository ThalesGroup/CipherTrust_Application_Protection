package io.ciphertrust.cryptoagility.repository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import io.ciphertrust.cryptoagility.entity.SmartMeterData;

public interface SmartMeterDataRepository extends JpaRepository<SmartMeterData, Long> {
    List<SmartMeterData> findByTimestampBetween(LocalDateTime start, LocalDateTime end);
    List<SmartMeterData> findBySmartMeterId(Long smartMeterId);
    List<SmartMeterData> findBySmartMeterIdAndTimestampBetween(Long smartMeterId, LocalDateTime start, LocalDateTime end);
    @Query("SELECT t FROM SmartMeterData t WHERE t.smartMeter.id = :smartMeterId AND t.timestamp >= :startTime")
    List<SmartMeterData> findTelemetryDataBySmartMeterIdAndTimestampAfter(
            @Param("smartMeterId") Long smartMeterId,
            @Param("startTime") LocalDateTime startTime);
}