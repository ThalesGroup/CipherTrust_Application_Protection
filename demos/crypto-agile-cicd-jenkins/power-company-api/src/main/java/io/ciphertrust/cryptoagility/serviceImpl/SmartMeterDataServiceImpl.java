package io.ciphertrust.cryptoagility.serviceImpl;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import io.ciphertrust.cryptoagility.entity.SmartMeterData;
import io.ciphertrust.cryptoagility.repository.SmartMeterDataRepository;
import io.ciphertrust.cryptoagility.service.SmartMeterDataService;
import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityNotFoundException;

@Service
public class SmartMeterDataServiceImpl implements SmartMeterDataService {

    @Autowired
    private SmartMeterDataRepository smartMeterDataRepository;

    @Autowired
    private EntityManager entityManager;

    @Override
    @Transactional
    public SmartMeterData saveSmartMeterData(SmartMeterData data) {
        SmartMeterData saved = smartMeterDataRepository.save(data);
        entityManager.flush();
        return saved;
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