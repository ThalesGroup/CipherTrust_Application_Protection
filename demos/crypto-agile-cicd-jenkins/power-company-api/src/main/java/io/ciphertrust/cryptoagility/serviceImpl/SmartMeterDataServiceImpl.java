package io.ciphertrust.cryptoagility.serviceImpl;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.cryptoagility.entity.SmartMeterData;
import io.ciphertrust.cryptoagility.repository.SmartMeterDataRepository;
import io.ciphertrust.cryptoagility.service.SmartMeterDataService;
import jakarta.persistence.EntityNotFoundException;

@Service
public class SmartMeterDataServiceImpl implements SmartMeterDataService {

    @Autowired
    private SmartMeterDataRepository smartMeterDataRepository;

    @Override
    public SmartMeterData saveSmartMeterData(SmartMeterData data) {
        return smartMeterDataRepository.save(data);
    }

    @Override
    public SmartMeterData getSmartMeterDataById(Long id) {
        return smartMeterDataRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("SmartMeterData not found with id: " + id));
    }

    @Override
    public List<SmartMeterData> getAllSmartMeterData() {
        return smartMeterDataRepository.findAll();
    }

    @Override
    public List<SmartMeterData> getSmartMeterDataByTimestampRange(LocalDateTime start, LocalDateTime end) {
        return smartMeterDataRepository.findByTimestampBetween(start, end);
    }

    @Override
    public void deleteSmartMeterData(Long id) {
        smartMeterDataRepository.deleteById(id);
    }
}