package io.ciphertrust.cryptoagility.service;

import java.util.List;

import io.ciphertrust.cryptoagility.entity.SmartMeter;

public interface SmartMeterService {
    SmartMeter addSmartMeter(SmartMeter smartMeter);
    SmartMeter getSmartMeterById(Long id);
    List<SmartMeter> getSmartMetersByUserId(Long userId);
    void deleteSmartMeter(Long id);
}
