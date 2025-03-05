package io.ciphertrust.cryptoagility.serviceImpl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.cryptoagility.entity.SmartMeter;
import io.ciphertrust.cryptoagility.repository.SmartMeterRepository;
import io.ciphertrust.cryptoagility.service.SmartMeterService;
import jakarta.persistence.EntityNotFoundException;

@Service
public class SmartMeterServiceImpl implements SmartMeterService {

    @Autowired
    private SmartMeterRepository smartMeterRepository;

    @Override
    public SmartMeter addSmartMeter(SmartMeter smartMeter) {
        return smartMeterRepository.save(smartMeter);
    }

    @Override
    public SmartMeter getSmartMeterById(Long id) {
        return smartMeterRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("SmartMeter not found with id: " + id));
    }

    @Override
    public List<SmartMeter> getSmartMetersByUserId(Long userId) {
        return smartMeterRepository.findByUserId(userId);
    }

    @Override
    public void deleteSmartMeter(Long id) {
        smartMeterRepository.deleteById(id);
    }

    @Override
    public SmartMeter saveSmartMeter(SmartMeter smartMeter) {
        return smartMeterRepository.save(smartMeter);
    }

    @Override
    public List<SmartMeter> getSmartMetersByAggregatorId(Long aggregatorId) {
        return smartMeterRepository.findByAggregatorId(aggregatorId);
    }
}
