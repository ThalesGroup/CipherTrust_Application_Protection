package io.ciphertrust.cryptoagility.service;

import java.time.LocalDateTime;
import java.util.List;

import io.ciphertrust.cryptoagility.entity.SmartMeterData;

public interface SmartMeterDataService {
    SmartMeterData saveSmartMeterData(SmartMeterData data);
    SmartMeterData getSmartMeterDataById(Long id);
    List<SmartMeterData> getAllSmartMeterData();
    List<SmartMeterData> getSmartMeterDataByTimestampRange(LocalDateTime start, LocalDateTime end);
    void deleteSmartMeterData(Long id);
}